import requests
import logging
import argparse

logging.getLogger().setLevel(logging.INFO)

if __name__ == '__main__':
     # Create a new argument parser
     parser = argparse.ArgumentParser()

     # add options to the parser
     parser.add_argument('--hostname', help='API hostname', required=True)
     parser.add_argument('--port', help='API port', required=True)
     parser.add_argument('--inference_type', help='inference type: open_vino, darknet', required=False, default="open_vino")
     parser.add_argument('--inference_device', help='inference device: CPU, GPU', required=False, default="CPU")
     parser.add_argument('--process_image', help='If image should be processed by the inference or not', required=False, default="True")
     parser.add_argument('--device_uri', help='Device IP', required=False, default="coap://10.10.12.1:12345/k8s/input")

     # parse the command line arguments
     args = parser.parse_args()

     payload = {
          "inference_type": args.inference_type,
          "device": args.inference_device,
          "process_image": True,
          "device_uri": 'coap://10.10.12.1:12345/k8s/input'
     }

     response = requests.post(url=f"http://{args.hostname}:{args.port}/video/start",json=payload)
     logging.info(f"Response arrived {response}")
