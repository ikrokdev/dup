import os
import subprocess

import torch
import whisperx
import pandas as pd

batch_size=24

def transcribe_and_save(wav_file, base_file):
    audio = whisperx.load_audio(wav_file)
    result = model.transcribe(audio, batch_size=batch_size)

    model_a, metadata = whisperx.load_align_model(language_code=result["language"], device=DEVICE)
    result = whisperx.align(result["segments"], model_a, metadata, audio, DEVICE, return_char_alignments=False)
    diarize_model = whisperx.DiarizationPipeline(use_auth_token='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', device=DEVICE)

    # add min/max number of speakers if known
    diarize_segments = diarize_model(audio)
    result = whisperx.assign_word_speakers(diarize_segments, result)

    # transcribe_output = model.transcribe(wav_file)
    # segments = transcribe_output.get('segments', [])
    df = pd.DataFrame(result['segments'])
    vtt_file = base_file + '.segments.csv'
    json_file = base_file + '.segments.json'
    df.to_csv(vtt_file, sep='|')
    df.to_json(json_file)
    return vtt_file

def convert_to_wav(mp3_file, wav_file):
    # Replace backslashes with forward slashes for Linux compatibility
    mp3_file_path = mp3_file.replace('\\', '/')
    wav_file_path = wav_file.replace('\\', '/')

    # Remove wav_file if it already exists
    if os.path.exists(wav_file_path):
        os.remove(wav_file_path)

    command = ['ffmpeg', '-i', mp3_file_path, '-acodec', 'pcm_s16le', '-ac', '1', '-ar', '16000', wav_file_path]
    subprocess.run(command, check=True)
    return wav_file_path


def process_file(mp3_path):
    base_name = os.path.splitext(mp3_path)[0]
    print(
        'Processing file {0} '.format(mp3_path)
    )
    wav_path = convert_to_wav(mp3_path, base_name + '.wav')
    vtt_file = transcribe_and_save(wav_path, base_name)


def process_directory(directory):
     for root, dirs, files in os.walk(directory):
        for filename in files:
            if filename.endswith(".mp3"):
                process_file(os.path.join(root, filename))


if __name__ == '__main__':
    directory_to_process = '../---'

    model_name = "base.en"
    DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
    compute_type = "float32"

    model = whisperx.load_model(model_name, DEVICE, compute_type=compute_type)

    process_directory(directory_to_process)
