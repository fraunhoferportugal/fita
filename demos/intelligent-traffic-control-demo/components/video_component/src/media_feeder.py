import os
import time
import threading
import asyncio
import cv2

from loguru import logger

from .noise_handler import NoiseHandler

class MediaFeeder:
    def __init__(self, video_path):
        self.video_path = video_path
        self.recording = False
        self.frames_to_skip = 0
        self.skip_frame_counter = 0
        self.callback = None
        self.device_uri = None
        self.noise_handler = NoiseHandler(video_path, "temp_audio.wav")

    def is_recording(self):
        return self.recording
    
    def trigger(self, callback, frames_to_skip, device_uri):
        # Trigger camera recording
        self.frames_to_skip = frames_to_skip
        self.callback = callback
        self.device_uri = device_uri

        if not self.recording:
            self.recording = True
            self.recording_thread = threading.Thread(target=self.record_loop)
            self.recording_thread.start()

    def stop(self):
        # Stop camera recording
        self.recording = False

    def record_loop(self):
        logger.info("Record loop starting")

        while True and self.recording:
            self.skip_frame_counter = 0
            self.seconds_count = 0

            cap = cv2.VideoCapture(self.video_path)
            pos_frame = cap.get(cv2.CAP_PROP_POS_FRAMES)
            
            while True and self.recording:
                try:
                    flag, frame = cap.read()
                    if flag:
                        self._handle_frame(frame)                        
                        self._handle_noise(cap)

                    else:
                        # The next frame is not ready, so we try to read it again
                        cap.set(cv2.CAP_PROP_POS_FRAMES, pos_frame - 1)
                        logger.info("frame is not ready")
                        
                        # It is better to wait for a while for the next frame to be ready
                        cv2.waitKey(1)

                    # If the number of captured frames is equal to the total number of frames, we stop
                    if cap.get(cv2.CAP_PROP_POS_FRAMES) == cap.get(cv2.CAP_PROP_FRAME_COUNT):
                        break

                except Exception as e:
                    logger.exception(e)
                    time.sleep(5)

        self.noise_handler.remove_audio()

    def _handle_frame(self, frame):
        if self.skip_frame_counter == self.frames_to_skip:
            self.callback(frame)
            self.skip_frame_counter = 0
        else:
            self.skip_frame_counter = self.skip_frame_counter + 1

    def _handle_noise(self, cap):
        if cap.get(cv2.CAP_PROP_POS_FRAMES) > cap.get(cv2.CAP_PROP_FPS) * self.seconds_count:
            dbfs = self.noise_handler.calculate_dbfs_segment(self.seconds_count * 1000, 1000)
            if (self.device_uri != None):
                asyncio.run(self.noise_handler.send_noise_coap(self.device_uri, dbfs))
            self.seconds_count += 1
