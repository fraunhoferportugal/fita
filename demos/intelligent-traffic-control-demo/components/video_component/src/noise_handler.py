import os
import subprocess
import struct
import aiocoap
import cbor2

from pydub import AudioSegment

class NoiseHandler:
    def __init__(self, video_path, audio_path):
        self.video_path = video_path
        self.audio_path = audio_path
        self.audio = self._extract_audio()

        self.transport_tuning = aiocoap.TransportTuning()
        self.transport_tuning.ACK_TIMEOUT = 1 # Ack should be less than 1 second
        self.transport_tuning.MAX_RETRANSMIT = 0 # No message retransmission
        pass

    async def send_noise_coap(self, device_uri, dbfs):
        input_value = bytearray(struct.pack("<f", dbfs))
        payload = cbor2.dumps(['value', 1, input_value])

        protocol = await aiocoap.Context.create_client_context()
        request = aiocoap.Message(
            code=aiocoap.PUT,
            payload=payload,
            uri=device_uri,
            transport_tuning=self.transport_tuning
        )
        try:
            response = await protocol.request(request).response
            print(f'send_noise_coap response: {response}')
        except Exception as e:
            print(f'An {type(e)} exception ocurred')

    def calculate_dbfs_segment(self, start_ms, duration_ms):
        segment = self.audio[start_ms:start_ms + duration_ms]
        return segment.dBFS
    
    def remove_audio(self):
        os.remove(self.audio_path)

    def _extract_audio(self):
        command = [
            "ffmpeg", "-y", "-i", self.video_path,
            "-vn",  # no video
            "-acodec", "pcm_s24le", # audio format based on kallisto mic (should be pcm_s24be but it is not supported)
            "-ar", "16000", # sample rate based on kallisto mic
            "-ac", "1",  # mono
            self.audio_path
        ]
        subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return AudioSegment.from_wav(self.audio_path)
    