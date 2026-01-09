""" Module to handle go2rtc interactions """
from __future__ import annotations

from loguru import logger
import subprocess
import numpy as np

class Go2RTCStreamer:
    """Class to manage external stream provider and byte based ffmpeg streaming"""

    def __init__(self, rtsp_server_address, name) -> None:
        self.rtsp_server_address = rtsp_server_address
        self.name = name
        self.ffmpeg_process = None
    
    def open_ffmpeg_stream_process(self):
        args = (
            # "ffmpeg -re -f rawvideo -pix_fmt "
            # "bgr24 -s 1920x1080 -i pipe:0 "
            # "-c mjpeg -huffman 0 -pix_fmt yuvj420p "
            # # "-vcodec libx264 -pix_fmt yuv420p "
            # f"-f rtsp -rtsp_transport tcp rtsp://{self.rtsp_server_address}/{self.name}"
            # #"-f mpjpeg http://localhost:1984/api/frame.jpeg?dst=mystream"

             f"ffmpeg -re -f rawvideo -pixel_format bgr24 -video_size 1920x1080 -i - -c:v libx264 -preset veryfast -tune zerolatency -f rtsp -rtsp_transport tcp rtsp://{self.rtsp_server_address}/{self.name}"
        ).split()
        return subprocess.Popen(args, stdin=subprocess.PIPE)

    def write(self, frame):
        self.ffmpeg_process.stdin.write(frame.astype(np.uint8).tobytes())

    def start(self):
        logger.info("Video stream start")
        self.ffmpeg_process = self.open_ffmpeg_stream_process() 

    def stop(self):
        self.ffmpeg_process.kill()
