#!/bin/bash
set -e

DIR=$(cd "$(dirname "$0")" && pwd)
OPENVINO_MODEL_FOLDER="$DIR/../components/video_component/assets/models/openvino_model"
YOLO_WEIGHTS_FOLDER="$DIR/../components/video_component/assets/models/yolo_weights"
VIDEOS_FOLDER="$DIR/../components/video_component/assets/videos"

pushd $OPENVINO_MODEL_FOLDER

if [ ! -f coco.names ]; then
    wget -O coco.names https://github.com/fraunhoferportugal/fita/releases/download/0.0.1/coco.names
fi

if [ ! -f frozen_darknet_yolov4_model.xml ]; then
    wget -O frozen_darknet_yolov4_model.xml https://github.com/fraunhoferportugal/fita/releases/download/0.0.1/frozen_darknet_yolov4_model.xml
fi

if [ ! -f frozen_darknet_yolov4_model.bin ]; then
    wget -O frozen_darknet_yolov4_model.bin https://github.com/fraunhoferportugal/fita/releases/download/0.0.1/frozen_darknet_yolov4_model.bin
fi

popd

pushd $YOLO_WEIGHTS_FOLDER

if [ ! -f yolov3.weights ]; then
wget -O yolov3.weights https://github.com/fraunhoferportugal/fita/releases/download/0.0.1/yolov3.weights
fi

if [ ! -f yolov3-tiny.weights ]; then
wget -O yolov3-tiny.weights https://github.com/fraunhoferportugal/fita/releases/download/0.0.1/yolov3-tiny.weights
fi

popd

pushd $VIDEOS_FOLDER

if [ ! -f video3.mp4 ]; then
wget -O video3.mp4 https://github.com/fraunhoferportugal/fita/releases/download/0.0.1/traffic-video.mp4
fi

popd
