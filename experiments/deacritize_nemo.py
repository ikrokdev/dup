import nemo.collections.asr as nemo_asr
import soundfile as sf
from pydub import AudioSegment

# Function to transcribe audio
def transcribe_audio(asr_model, audio_file_path):
    transcript = asr_model.transcribe(paths2audio_files=[audio_file_path])[0]
    return transcript

# Diarization model function (updated to include transcription)
def diarization_and_transcription_model(audio_file_path):
    # Load pre-trained diarization model
    diar_model = nemo_asr.models.EncDecSpeakerDiarizerModel.from_pretrained('speakerverification_speakernet')

    # Load pre-trained ASR model
    asr_model = nemo_asr.models.EncDecCTCModelBPE.from_pretrained(model_name="stt_en_conformer_ctc_large")

    # Process and diarize the audio file
    diar_model.diarize(
        paths2audio_files=[audio_file_path],
        batch_size=1,
        return_dict=True
    )

    # Transcribe audio
    transcription = transcribe_audio(asr_model, audio_file_path)

    # Retrieving diarization results
    diarization_result = diar_model.get_diarization_labels()

    # Process the result
    speakers_info = diarization_result[0]
    for segment in speakers_info:
        start_time = segment['start_time']
        end_time = segment['end_time']
        speaker_label = segment['label']
        print(f"Speaker {speaker_label} from {start_time:.2f}s to {end_time:.2f}s")

    # Print the transcription
    print("\nTranscription:\n", transcription)

# Convert MP3 to WAV
def convert_mp3_to_wav(mp3_file_path, wav_file_path):
    audio = AudioSegment.from_mp3(mp3_file_path)
    audio = audio.set_frame_rate(16000).set_channels(1)
    audio.export(wav_file_path, format="wav")

# Your MP3 file
mp3_file = 'your_audio_file.mp3'
wav_file = 'temp.wav'

# Convert to WAV and load
convert_mp3_to_wav(mp3_file, wav_file)

# Diarization and transcription
diarization_and_transcription_model(wav_file)
