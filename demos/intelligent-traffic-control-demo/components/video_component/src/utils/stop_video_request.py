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

    # parse the command line arguments
    args = parser.parse_args()

    response = requests.post(url=f"http://{args.hostname}:{args.port}/video/stop")
    logging.info(f"Response arrived {response}")
