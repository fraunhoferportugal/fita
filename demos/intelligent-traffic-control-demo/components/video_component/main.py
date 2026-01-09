import time
import os
import cv2

from fastapi import FastAPI, Request, status, BackgroundTasks
from fastapi.responses import JSONResponse, HTMLResponse, StreamingResponse
from fastapi.exceptions import RequestValidationError
from loguru import logger

from src.media_feeder import MediaFeeder
from src.go2rtc_streamer import Go2RTCStreamer
from src.image_inference import ImageInference
from src.request_models import ImageInferenceDevice, StartVideoProcessingReq, ImageInferenceType

def parse_bool_env(var_name, default=False):
    val = os.environ.get(var_name, str(default)).lower()
    return val in ('1', 'true', 't', 'yes', 'y', 'on')

def image_inference_builder(inference_type: ImageInferenceType, inference_device:ImageInferenceDevice = ImageInferenceDevice.gpu) -> ImageInference:
    match (inference_type):
        case ImageInferenceType.openvino:
            return ImageInference("assets/models/openvino_model/frozen_darknet_yolov4_model.xml","open_vino",inference_device,"assets/models/openvino_model/coco.names","")
        case ImageInferenceType.darknet:
            # No version with GPU implemented
            return ImageInference("assets/models/darknet/cfg/yolov3.cfg","darknet","CPU","assets/models/darknet/data/coco.names","assets/models/yolo_weights/yolov3.weights")
        case _:
            raise ValueError(f"Unkown Inference type: '{inference_type}'")


server_address = os.environ.get('VIDEO_SERVER_ADDRESS') if os.environ.get('VIDEO_SERVER_ADDRESS') != None else 'localhost:8554'
server_stream = os.environ.get('VIDEO_SERVER_STREAM') if os.environ.get('VIDEO_SERVER_STREAM') != None else 'mystream'
autostart_video = parse_bool_env('VIDEO_AUTOSTART') if os.environ.get('VIDEO_AUTOSTART') != None else False
enable_inference = parse_bool_env('VIDEO_INFERENCE') if os.environ.get('VIDEO_INFERENCE') != None else False
default_inference_model_type = ImageInferenceType(os.environ.get('VIDEO_INFERENCE_DEFAULT_MODEL_TYPE')) if os.environ.get('VIDEO_INFERENCE_DEFAULT_MODEL_TYPE') != None else ImageInferenceType.openvino

logger.info(f"Autostart Video: '{autostart_video}'")
logger.info(f"Enable inference: '{enable_inference}'")

is_image_infer_disabled = enable_inference != True
logger.info(f"Is Inference disabled '{is_image_infer_disabled}")

current_image_infer = None if is_image_infer_disabled else image_inference_builder(default_inference_model_type)
go2rtc_video_stream = Go2RTCStreamer(server_address, server_stream)
video_source = MediaFeeder('assets/videos/video3.mp4')
def on_video_message(frame):
    global current_image_infer
    global is_image_infer_disabled
    # logger.info("Frame arrived")

    if not is_image_infer_disabled and current_image_infer is not None:
        frame = current_image_infer.infer_image(frame,0.5)

    # cv2.imwrite("./frames/frame%d.jpeg" % count, frame)
    img = cv2.resize(frame,(1920,1080))

    go2rtc_video_stream.write(img)
    
    return

if autostart_video:
    go2rtc_video_stream.start()
    time.sleep(1)
    video_source.trigger(on_video_message, 0, None)


app=FastAPI()
print(f"Server Address: {server_address} Stream: {server_stream}")

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError,):
    logger.error(f"{exc}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "status_code": 422,
            "message": f"{exc}",
            "data": None
        }
    )

@app.get("/health", tags=["Health"])
def health():
    return JSONResponse(content={"status": "ok"})

@app.post("/video/start",status_code=200,)
def video_stream_start(req: StartVideoProcessingReq, background_tasks: BackgroundTasks):
    global current_image_infer
    global is_image_infer_disabled
    
    if not video_source.is_recording():
        go2rtc_video_stream.start()
        time.sleep(1)

    if req.process_image:
        if current_image_infer != None:
            if current_image_infer.model_type != req.inference_type or current_image_infer.device != req.device:
                current_image_infer = None

                if req.inference_type == ImageInferenceType.openvino:
                    current_image_infer = image_inference_builder(ImageInferenceType.openvino, req.device)
                elif req.inference_type == ImageInferenceType.darknet:
                    current_image_infer = image_inference_builder(ImageInferenceType.darknet, req.device)
        else:
            if req.inference_type == ImageInferenceType.openvino:
                current_image_infer = image_inference_builder(ImageInferenceType.openvino, req.device)
            elif req.inference_type == ImageInferenceType.darknet:
                current_image_infer = image_inference_builder(ImageInferenceType.darknet, req.device)

        background_tasks.add_task(video_source.trigger, on_video_message, 1, req.device_uri)
            
        is_image_infer_disabled = False
    else:
        is_image_infer_disabled = True

        background_tasks.add_task(video_source.trigger, on_video_message, 0, req.device_uri)

    return ""

@app.post("/video/stop",status_code=200,)
def video_stream_stop():
    global is_image_infer_disabled
    global current_image_infer

    if not video_source.is_recording():
        return

    video_source.stop()
    go2rtc_video_stream.stop()
    
    is_image_infer_disabled = True
    current_image_infer = None
