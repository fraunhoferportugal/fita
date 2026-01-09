from pydantic import BaseModel
from enum import Enum

class ImageInferenceType(str, Enum):
    openvino = 'open_vino'
    darknet = 'darknet'

class ImageInferenceDevice(str, Enum):
    cpu = 'CPU'
    gpu = 'GPU'

class StartVideoProcessingReq(BaseModel):
    inference_type: ImageInferenceType
    device: ImageInferenceDevice
    process_image: bool
    device_uri: str | None
