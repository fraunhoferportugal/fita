import requests

def test_connection(video_uri, video_port):
    url = f'http://{video_uri}:{str(video_port)}/health'
    response = requests.get(url)
    print(response.json())

def set_video_off(video_uri, video_port):
    print("set_video_off")

    url = f'http://{video_uri}:{str(video_port)}/video/stop'
    response = requests.post(url,
        json = {
            "inference_type": "open_vino",
            "device": "GPU",
            "process_image": False,
            "device_uri": None
        }
    )
    print(response.json())


def set_video_on(video_uri, video_port, process_image=False, device_uri=None):
    print(f"set_video_on {video_uri}:{video_port} {process_image} {device_uri}")

    url = f'http://{video_uri}:{str(video_port)}/video/start'
    response = requests.post(url,
        json = {
            "inference_type": "open_vino",
            "device": "GPU",
            "process_image": process_image,
            "device_uri": device_uri
        }
    )
    print(response)
