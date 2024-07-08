FROM python:3.10.2

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN apt update && echo y | apt install ffmpeg

COPY . .

CMD ["python", "./app/analysers/WhisperXTranscriber.py"]
