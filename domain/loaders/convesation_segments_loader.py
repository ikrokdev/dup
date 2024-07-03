import pandas as pd
from dataclasses import dataclass
from typing import List
from nltk.tokenize import sent_tokenize

from app.loaders.conversation_loader import ConversationLoader
from domain.conversation.conversation import Conversation
from domain.conversation.speaker import Speaker
from domain.conversation.sentence import Sentence
from domain.conversation.speaker_turn import SpeakerTurn
from domain.conversation.word import Word
from domain.conversation.time_range import TimeRange


@dataclass
class ConversationSegmentsLoader(ConversationLoader):
    filename: str

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

    def generate_id(self, start, end, prefix='t'):
        start_rounded = str(round(start)).zfill(3)  # Ensures at least 3 digits
        end_rounded = str(round(end)).zfill(3)
        return f"{prefix}-{start_rounded}-{end_rounded}"

    def _split_into_sentences(self, text: str) -> List[str]:
        # Basic sentence splitting logic
        return sent_tokenize(text)
        # return [sentence.strip() for sentence in text.split('.') if sentence]

    def load(self, folder_name: str) -> Conversation:
        conversation = Conversation(conversation_id='1', speakers={})
        self.data = pd.read_json(self.filename)
        df = self.combine_speaker_text()  # Assuming this method exists

        for index, row in df.iterrows():
            speaker_id = row['speaker']
            if speaker_id not in conversation.speakers:
                conversation.speakers[speaker_id] = Speaker(speaker_id=speaker_id)

            turn_id = self.generate_id(row['start'], row['end'], 't')
            turn = SpeakerTurn(
                turn_id=f"{turn_id}",
                speaker_id=speaker_id,
                text=row['text'],
                time_range=TimeRange(start=float('inf'), end=float('-inf'))
            )

            turn_sentences = self._split_into_sentences(row['text'])
            for sentence_text in turn_sentences:
                turn.add_sentence(
                    Sentence(
                        sentence_id='-',
                        speaker_id=turn.speaker_id,
                        text=sentence_text,
                        time_range=TimeRange(0, 0)
                    )
                )

            for wd in row['words']:
                start_time = wd.get('start', 0.0)
                end_time = wd.get('end', 0.0)

                # Skip words with missing or invalid timing information
                if start_time == 0.0 or end_time == 0.0:
                    continue

                word = Word(
                    word=wd.get('word', ''),
                    time_range=TimeRange(start=start_time, end=end_time),
                    score=wd.get('score', 0)
                )
                turn.words.append(word)

            # Update the time range for the entire turn based on the sentences
            if turn.words:
                turn.time_range.start = min(word.time_range.start for word in turn.words)
                turn.time_range.end = max(word.time_range.end for word in turn.words)

            conversation.add_turn(turn)
        return conversation


if __name__ == '__main__':
    filename = '../---/segments.json'
    loader = ConversationSegmentsLoader(filename)
    conversation = loader.load("c:\\_\\dub\\app\\---")
