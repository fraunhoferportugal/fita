import os
import time
import subprocess

import cv2
from pydub import AudioSegment

VIDEO_PATH='../assets/videos/video3.mp4'

def extract_audio(video_path, audio_output="temp_audio.wav"):
    command = [
        "ffmpeg", "-y", "-i", video_path,
        "-vn",  # no video
        "-acodec", "pcm_s24le", # audio format based on kallisto mic (should be pcm_s24be but it is not supported)
        "-ar", "16000", # sample rate based on kallisto mic
        "-ac", "1",  # mono
        audio_output
    ]
    subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return audio_output

def remove_audio(audio_path="temp_audio.wav"):
    os.remove(audio_path)

def calculate_dbfs_segment(audio, start_ms, duration_ms):
    segment = audio[start_ms:start_ms + duration_ms]
    return segment.dBFS

def record_loop():
    print("Record loop starting")
    frames_count = 0
    seconds_count = 0

    extract_audio(VIDEO_PATH)
    audio = AudioSegment.from_wav("temp_audio.wav")
    print("Audio extracted")

    cap = cv2.VideoCapture(VIDEO_PATH)
    pos_frame = cap.get(cv2.CAP_PROP_POS_FRAMES)
    print(cap.get(cv2.CAP_PROP_FPS))

    try:
        while True:
            flag, frame = cap.read()
            if flag:
                frames_count += 1
                if frames_count > cap.get(cv2.CAP_PROP_FPS):
                    frames_count = 0
                    print(calculate_dbfs_segment(audio, seconds_count * 1000, 1000))
                    seconds_count += 1

            else:
                # The next frame is not ready, so we try to read it again
                cap.set(cv2.CAP_PROP_POS_FRAMES, pos_frame - 1)
                print("frame is not ready")
                
            # It is better to wait for a while for the next frame to be ready
            cv2.waitKey(1)

            if cap.get(cv2.CAP_PROP_POS_FRAMES) == cap.get(cv2.CAP_PROP_FRAME_COUNT):
                # If the number of captured frames is equal to the total number of frames, we stop
                break

    except Exception as e:
        print(e)
        time.sleep(5)

    finally:
        remove_audio()
        print(frames_count)

if __name__ == '__main__':
    # record_loop()

    import openvino as ov

    core = ov.Core()

    print(core.available_devices)

    # device = "CPU"
    # core.get_property(device, "FULL_DEVICE_NAME")
