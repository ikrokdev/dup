# DUP

## Local Deploy

To deploy dup you should have **python>=3.10**:

1. Clone this repo

```bash
git clone https://github.com/ikrokdev/dup.git
```

2. Create a **venv** and activate it

```bash
python3 -m venv ./venv
```

```bash
source ./venv/bin/activate # if you're using Linux/Mac

.venv\Scripts\activate.bat # if you're using Windows
```

3. Install requirements

```bash
pip install -r requirements.txt
```

4. (Optional) If you don't have a **ffmpeg** package installed 

```bash
apt install ffmpeg # Linux

brew install ffmpeg # Mac

choco install ffmpeg # Windows
```

5. Drop some audio file to **data** fodler and run the scripts from **app/analysers**

```bash
python3 WhisperXTranscriber.py # example of using WhisperXTranscriber to transcribe an audio file into text and distinguish between different speakers.
```

## Docker Deploy

For this deploy you will need to have Docker and Docker-Compose installed on your system

1. Clone this repo

```bash
git clone https://github.com/ikrokdev/dup.git
```

2. Deploy dup project using docker-compose 

```bash
docker compose -p dup up -d
```

It'll create dup project and run the script provided in the **environment** section of the **docker-compose.yml** file

