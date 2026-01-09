FROM python:3.10

LABEL authors="João Gomes <joao.matos@fraunhofer.pt>, José Costa <jose.costa@fraunhofer.pt>"
LABEL version="1.0"

RUN apt-get update && apt-get install -y ffmpeg curl gpg-agent \
    && echo 'deb [arch=amd64 signed-by=/usr/share/keyrings/intel-graphics.gpg] https://repositories.intel.com/gpu/ubuntu jammy/lts/2350 unified' | \
       tee -a /etc/apt/sources.list.d/intel.list \
    && curl -s https://repositories.intel.com/gpu/intel-graphics.key | \
       gpg --dearmor --output /usr/share/keyrings/intel-graphics.gpg \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
       intel-opencl-icd \
       clinfo \
    && apt-get remove -y curl gpg-agent \
    && apt-get autoremove -y

WORKDIR /app

COPY ./assets ./assets
RUN cd ./assets/models/darknet && make

COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY ./src ./src
COPY ./main.py .

ENV ALGORITHM_API_PORT=6013

# Set the command to run the Python script with the -u option for unbuffered output
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${ALGORITHM_API_PORT}"]
