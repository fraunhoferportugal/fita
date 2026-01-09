#!/usr/bin/env python3

import logging
import os
import sys
from math import exp

import cv2
import numpy as np
from openvino.inference_engine import IECore

import ngraph as ng
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'common'))

logging.basicConfig(format="[ %(levelname)s ] %(message)s", level=logging.INFO, stream=sys.stdout)
log = logging.getLogger()

class YoloParams:
    # ------------------------------------------- Extracting layer parameters ------------------------------------------
    # Magic numbers are copied from yolo samples
    def __init__(self, param, side):
        self.num = 3 if 'num' not in param else int(param['num'])
        self.coords = 4 if 'coords' not in param else int(param['coords'])
        self.classes = 80 if 'classes' not in param else int(param['classes'])
        self.side = side
        self.anchors = [10.0, 13.0, 16.0, 30.0, 33.0, 23.0, 30.0, 61.0, 62.0, 45.0, 59.0, 119.0, 116.0, 90.0, 156.0,
                        198.0,
                        373.0, 326.0] if 'anchors' not in param else param['anchors']

        self.isYoloV3 = False

        if param.get('mask'):
            mask = param['mask']
            self.num = len(mask)

            maskedAnchors = []
            for idx in mask:
                maskedAnchors += [self.anchors[idx * 2], self.anchors[idx * 2 + 1]]
            self.anchors = maskedAnchors

            self.isYoloV3 = True # Weak way to determine but the only one.

def preprocess_frame(frame, input_height, input_width, nchw_shape, keep_aspect_ratio):
    in_frame = resize(frame, (input_width, input_height), keep_aspect_ratio)
    if nchw_shape:
        in_frame = in_frame.transpose((2, 0, 1))  # Change data layout from HWC to CHW
    in_frame = np.expand_dims(in_frame, axis=0)
    return in_frame

def scale_bbox(x, y, height, width, class_id, confidence, color, im_h, im_w, is_proportional):
    if is_proportional:
        scale = np.array([min(im_w/im_h, 1), min(im_h/im_w, 1)])
        offset = 0.5*(np.ones(2) - scale)
        x, y = (np.array([x, y]) - offset) / scale
        width, height = np.array([width, height]) / scale
    xmin = int((x - width / 2) * im_w)
    ymin = int((y - height / 2) * im_h)
    xmax = int(xmin + width * im_w)
    ymax = int(ymin + height * im_h)
    # Method item() used here to convert NumPy types to native types for compatibility with functions, which don't
    # support Numpy types (e.g., cv2.rectangle doesn't support int64 in color parameter)
    return dict(xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax, class_id=class_id.item(), confidence=confidence.item(), color=color)


def intersection_over_union(box_1, box_2):
    width_of_overlap_area = min(box_1['xmax'], box_2['xmax']) - max(box_1['xmin'], box_2['xmin'])
    height_of_overlap_area = min(box_1['ymax'], box_2['ymax']) - max(box_1['ymin'], box_2['ymin'])
    if width_of_overlap_area < 0 or height_of_overlap_area < 0:
        area_of_overlap = 0
    else:
        area_of_overlap = width_of_overlap_area * height_of_overlap_area
    box_1_area = (box_1['ymax'] - box_1['ymin']) * (box_1['xmax'] - box_1['xmin'])
    box_2_area = (box_2['ymax'] - box_2['ymin']) * (box_2['xmax'] - box_2['xmin'])
    area_of_union = box_1_area + box_2_area - area_of_overlap
    if area_of_union == 0:
        return 0
    return area_of_overlap / area_of_union


def resize(image, size, keep_aspect_ratio, interpolation=cv2.INTER_LINEAR):
    if not keep_aspect_ratio:
        return cv2.resize(image, size, interpolation=interpolation)

    iw, ih = image.shape[0:2][::-1]
    w, h = size
    scale = min(w/iw, h/ih)
    nw = int(iw*scale)
    nh = int(ih*scale)
    image = cv2.resize(image, (nw, nh), interpolation=interpolation)
    new_image = np.full((size[1], size[0], 3), 128, dtype=np.uint8)
    dx = (w-nw)//2
    dy = (h-nh)//2
    new_image[dy:dy+nh, dx:dx+nw, :] = image
    return new_image


def filter_objects(objects, iou_threshold, prob_threshold):
    # Filtering overlapping boxes with respect to the --iou_threshold CLI parameter
    objects = sorted(objects, key=lambda obj : obj['confidence'], reverse=True)
    for i in range(len(objects)):
        if objects[i]['confidence'] == 0:
            continue
        for j in range(i + 1, len(objects)):
            if intersection_over_union(objects[i], objects[j]) > iou_threshold:
                objects[j]['confidence'] = 0

    return tuple(obj for obj in objects if obj['confidence'] >= prob_threshold)


def put_highlighted_text(frame, message, position, font_face, font_scale, color, thickness):
    cv2.putText(frame, message, position, font_face, font_scale, (255, 255, 255), thickness + 2) # white border
    cv2.putText(frame, message, position, font_face, font_scale, color, thickness)


class ImageInference:
    def __init__(self, model, model_type, device, labels, weights):
        self.model = model
        self.model_type = model_type
        self.device = device
        self.model = model
        self.colors = np.random.randint(0, 255, size=(80, 3), dtype='uint8')

        if labels:
            with open(labels, 'r') as f:
                self.labels_map = [x.strip() for x in f]
        else:
            self.labels_map = None

        # ------------- 1. Plugin initialization for specified device and load extensions library if specified -------------
        log.info("Creating Inference Engine...")
        self.ie = IECore()

        config_user_specified = {}
        config_min_latency = {}

        log.info("Loading network")
        if model_type == "open_vino":
            self.net = self.ie.read_network(model, os.path.splitext(model)[0] + ".bin")
            self.input_blob = next(iter(self.net.input_info))

            # Read and pre-process input images
            if self.net.input_info[self.input_blob].input_data.shape[1] == 3:
                self.input_height, self.input_width = self.net.input_info[self.input_blob].input_data.shape[2:]
                self.nchw_shape = True
            else:
                self.input_height, self.input_width = self.net.input_info[self.input_blob].input_data.shape[1:3]
                self.nchw_shape = False
        elif model_type == "darknet":
            self.net = cv2.dnn.readNetFromDarknet(model, weights)
            self.input_height = 416
            self.input_width = 416
        else:
            log.error("Unknown model type")
            return


        if 'CPU' == self.device:
            config_min_latency['CPU_THROUGHPUT_STREAMS'] = '1'
        elif 'GPU' == self.device:
            config_min_latency['GPU_THROUGHPUT_STREAMS'] = '1'
        else:
            log.error("Unknown device")
            return

        log.info("Loading model to the plugin")

        if model_type == "open_vino":
            self.exec_net = self.ie.load_network(network=self.net, device_name=self.device,
                                                        config=config_min_latency,
                                                        num_requests=1)
        elif model_type == "darknet":
            self.net = cv2.dnn.readNetFromDarknet(model, weights)
            self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
            self.ln = self.net.getLayerNames()
            self.ln = [self.ln[i - 1] for i in self.net.getUnconnectedOutLayers()]

    def infer_image(self, frame, prob_threshold):
        #log.info("Starting inference...")

        if self.model_type == "open_vino":
            in_frame = preprocess_frame(frame, self.input_height, self.input_width, self.nchw_shape, False)
            result = self.exec_net.infer(inputs={self.input_blob: in_frame})

            objects = self.open_vino_get_objects(result, self.net, (self.input_width, self.input_height), frame.shape[:-1], prob_threshold, False)
        elif self.model_type == "darknet":
            blob = cv2.dnn.blobFromImage(frame, 1/255.0, (self.input_width, self.input_height), swapRB=True, crop=False)
            self.net.setInput(blob)
            result = self.net.forward(self.ln)
            objects = self.darknet_get_objects(result, frame)
        else:
            return frame

        #log.info(objects)
        objects = filter_objects(objects, 0.4, prob_threshold)

        origin_im_size = frame.shape[:-1]
        for obj in objects:
            # Validation bbox of detected object
            obj['xmax'] = min(obj['xmax'], origin_im_size[1])
            obj['ymax'] = min(obj['ymax'], origin_im_size[0])
            obj['xmin'] = max(obj['xmin'], 0)
            obj['ymin'] = max(obj['ymin'], 0)
            color = obj['color']
            det_label = self.labels_map[obj['class_id']] if self.labels_map and len(self.labels_map) >= obj['class_id'] else \
                str(obj['class_id'])

            cv2.rectangle(frame, (obj['xmin'], obj['ymin']), (obj['xmax'], obj['ymax']), color, 3)
            put_highlighted_text(frame,
                        "#" + det_label + ' ' + str(round(obj['confidence'] * 100, 1)) + ' %',
                        (obj['xmin'], obj['ymin'] - 7), cv2.FONT_HERSHEY_COMPLEX, 1, color, 2)
        
        return frame

    def darknet_get_objects(self, outputs, frame):
        objects = list()

        boxes = []
        confidences = []
        classIDs = []
        h, w = frame.shape[:2]
        #log.info(outputs)

        for output in outputs:
            for detection in output:
                scores = detection[5:]
                classID = np.argmax(scores)
                confidence = scores[classID]
                color = [int(c) for c in self.colors[classID]]
                box = detection[:4] * np.array([w, h, w, h])
                (centerX, centerY, width, height) = box.astype("int")
                x = int(centerX - (width / 2))
                y = int(centerY - (height / 2))
                classIDs.append(classID)
                objects.append({"confidence":float(confidence),"xmin":x,"xmax":x+int(width),"ymin":y,"ymax":y+int(height),"class_id":classID,"color":color})

        return objects

    def open_vino_get_objects(self, output, net, new_frame_height_width, source_height_width, prob_threshold, is_proportional):
        objects = list()
        function = ng.function_from_cnn(net)
        for layer_name, out_blob in output.items():
            #out_blob = out_blob.reshape(net.layers[net.layers[layer_name].parents[0]].out_data[0].shape)
            #layer_params = YoloParams(net.layers[layer_name].params, out_blob.shape[2])
            out_blob = out_blob.reshape(net.outputs[layer_name].shape)
            params = [x._get_attributes() for x in function.get_ordered_ops() if x.get_friendly_name() == layer_name][0]
            layer_params = YoloParams(params, out_blob.shape[2])
            objects += self.parse_yolo_region(out_blob, new_frame_height_width, source_height_width, layer_params,
                                        prob_threshold, is_proportional)
        return objects

    def parse_yolo_region(self, predictions, resized_image_shape, original_im_shape, params, threshold, is_proportional):
        # ------------------------------------------ Validating output parameters ------------------------------------------
        _, _, out_blob_h, out_blob_w = predictions.shape
        assert out_blob_w == out_blob_h, "Invalid size of output blob. It sould be in NCHW layout and height should " \
                                        "be equal to width. Current height = {}, current width = {}" \
                                        "".format(out_blob_h, out_blob_w)

        # ------------------------------------------ Extracting layer parameters -------------------------------------------
        orig_im_h, orig_im_w = original_im_shape
        resized_image_h, resized_image_w = resized_image_shape
        objects = list()
        size_normalizer = (resized_image_w, resized_image_h) if params.isYoloV3 else (params.side, params.side)
        bbox_size = params.coords + 1 + params.classes
        # ------------------------------------------- Parsing YOLO Region output -------------------------------------------
        for row, col, n in np.ndindex(params.side, params.side, params.num):
            # Getting raw values for each detection bounding box
            bbox = predictions[0, n*bbox_size:(n+1)*bbox_size, row, col]
            x, y, width, height, object_probability = bbox[:5]
            class_probabilities = bbox[5:]
            if object_probability < threshold:
                continue
            # Process raw value
            x = (col + x) / params.side
            y = (row + y) / params.side
            # Value for exp is very big number in some cases so following construction is using here
            try:
                width = exp(width)
                height = exp(height)
            except OverflowError:
                continue
            # Depends on topology we need to normalize sizes by feature maps (up to YOLOv3) or by input shape (YOLOv3)
            width = width * params.anchors[2 * n] / size_normalizer[0]
            height = height * params.anchors[2 * n + 1] / size_normalizer[1]

            class_id = np.argmax(class_probabilities)
            color = [int(c) for c in self.colors[class_id]]
            confidence = class_probabilities[class_id]*object_probability
            if confidence < threshold:
                continue
            objects.append(scale_bbox(x=x, y=y, height=height, width=width, class_id=class_id, confidence=confidence, color=color,
                                    im_h=orig_im_h, im_w=orig_im_w, is_proportional=is_proportional))
        return objects