import os, time
import whisperx
import pandas as pd
import torch


class WhisperXTranscriber:
    def __init__(self, model_name="base", lang='en', device=None, compute_type="float32", batch_size=24):
        self.device = device if device is not None else "cuda" if torch.cuda.is_available() else "cpu"
        self.model = whisperx.load_model(model_name, self.device, language=lang, compute_type=compute_type)
        self.batch_size = batch_size

    def transcribe_and_save(self, wav_file, base_file):
        start_time = time.time()
        audio = whisperx.load_audio(wav_file)
        print('a'*10, audio)
        load_audio_time = time.time()
        print(f"Audio loading time: {load_audio_time - start_time:.2f} seconds")

        result = self.model.transcribe(audio, batch_size=self.batch_size)
        transcribe_time = time.time()
        print(f"Transcription time: {transcribe_time - load_audio_time:.2f} seconds")

        model_a, metadata = whisperx.load_align_model(language_code=result["language"], device=self.device)
        result = whisperx.align(result["segments"], model_a, metadata, audio, self.device, return_char_alignments=False)
        align_time = time.time()
        print(f"Alignment time: {align_time - transcribe_time:.2f} seconds")

        diarize_model = whisperx.DiarizationPipeline(use_auth_token='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', device=self.device)
        diarize_segments = diarize_model(audio)
        diarization_time = time.time()
        print(f"Diarization time: {diarization_time - align_time:.2f} seconds")

        result = whisperx.assign_word_speakers(diarize_segments, result)
        speaker_assignment_time = time.time()
        print(f"Speaker assignment time: {speaker_assignment_time - diarization_time:.2f} seconds")

        df = pd.DataFrame(result['segments'])
        # Assuming modifications are needed to handle file saving correctly with the provided format
        csv_file = base_file + '.segments.csv'
        csv_file_with_words = base_file + '.segments_with_words.csv'
        json_file = base_file + '.segments.json'
        df.to_csv(csv_file_with_words, sep='|', index=False)
        df.to_json(json_file)
        df.drop('words', axis=1, inplace=True)
        df.to_csv(csv_file, sep='|', index=False)
        file_saving_time = time.time()
        print(f"File saving time: {file_saving_time - speaker_assignment_time:.2f} seconds")

        total_time = time.time() - start_time
        print(f"Total operation time: {total_time:.2f} seconds")
        return json_file

    def process_file(self, wav_path):
        base_name = os.path.splitext(wav_path)[0]
        print('Processing file {0} '.format(wav_path))
        vtt_file = self.transcribe_and_save(wav_path, base_name)


    def process_directory(self, directory):
        for root, dirs, files in os.walk(directory):
            for filename in files:
                if filename.endswith(".wav") or filename.endswith(".mp3"):
                    print(filename)
                    self.process_file(os.path.join(root, filename))


if __name__ == '__main__':
    directory_to_process = '../../---'
    transcriber = WhisperXTranscriber(model_name='large-v2',lang='en')
    transcriber.process_directory(directory_to_process)

