import ast
import csv
import json
import os

import pandas as pd
from dataclasses import dataclass, field
from typing import List, Dict, Optional

@dataclass
class ConversationLoader:
    def __init__(self, filename: str):
        self.filename = filename

    def load(self) -> Dict[str, Speaker]:
        speakers = {}
        self.data = pd.read_json(self.filename)
        df = self.combine_speaker_text()
        # Iterate over the rows of the DataFrame
        for index, row in df.iterrows():
            speaker_id = row['speaker']
            # If this is the first time we've seen this speaker, add them to the dictionary
            if speaker_id not in speakers:
                speakers[speaker_id] = Speaker(speaker_id=speaker_id)

            words_data = row['words']

            # Create a list of Word objects from the words data
            words_data = row['words']
            words = []
            for wd in words_data:
                try:
                    word = Word(
                        word=wd.get('word',''),
                        start=wd.get('start', 0),  # Use 0 or a default value if 'start' key is missing
                        end=wd.get('end', 0),  # Use 0 or a default value if 'end' key is missing
                        score=wd.get('score', 0),  # Use 0 or a default value if 'score' key is missing
                        speaker_id=wd.get('speaker', speaker_id)  # Fallback to the turn's speaker if missing
                    )
                    words.append(word)
                except KeyError as e:
                    print(f"KeyError for row {index}: {e}, in word data: {wd}")
                    continue  # Skips this word and continues with the next

            # Create a new SpeakerTurn object with the parsed data
            turn = SpeakerTurn(start=row['start'], end=row['end'], text=row['text'], words=words,
                               speaker_id=speaker_id)

            # Add the turn to the corresponding speaker
            speakers[speaker_id].add_turn(turn)

        return speakers

    def combine_speaker_text(self):
        combined_text = []
        current_speaker = None
        current_text = ""
        current_words = []
        start_time = None
        end_time = None

        for row in self.data.itertuples():
            if row.speaker == current_speaker:
                current_text += " " + row.text
                end_time = row.end
                current_words.extend(row.words)
            else:
                if current_text:
                    combined_text.append((current_speaker, start_time, end_time, current_text, current_words))
                current_speaker = row.speaker
                current_text = row.text
                current_words = row.words
                start_time = row.start
                end_time = row.end

        if current_text:
            combined_text.append((current_speaker, start_time, end_time, current_text, current_words))

        return pd.DataFrame(combined_text, columns=['speaker', 'start', 'end', 'text', 'words'])

    def save_to_folder(self, speakers: Dict[str, Speaker], folder_name: str = None):
        if folder_name is None:
            folder_name = os.path.splitext(self.filename)[0] + "_conversation"

        # Create the output folder if it doesn't exist
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)

        # Prepare data for turns.csv and words.csv
        turns_data = []
        words_data = []
        for speaker_id, speaker in speakers.items():
            for turn_index, turn in enumerate(speaker.turns):
                turn_id = f"{speaker_id}_{turn_index}"
                turns_data.append({
                    'turn_id': turn_id,
                    'speaker_id': speaker_id,
                    'start': turn.start,
                    'end': turn.end,
                    'text': turn.text
                })
                # Append words for this turn to words_data
                for word in turn.words:
                    words_data.append({
                        'turn_id': turn_id,
                        'word': word.word,
                        'start': word.start,
                        'end': word.end,
                        'score': word.score
                    })

        # Save turns.csv
        turns_df = pd.DataFrame(turns_data)
        turns_df.to_csv(os.path.join(folder_name, "turns.csv"), index=False)

        # Save words.csv
        words_df = pd.DataFrame(words_data)
        words_df.to_csv(os.path.join(folder_name, "words.csv"), index=False)


filename = '../segments.json'

# Instantiate the ConversationLoader with your CSV file
loader = ConversationLoader(filename)

# Load the conversation data into a dictionary of Speaker objects
conversation_speakers = loader.load()
loader.save_to_folder(conversation_speakers)