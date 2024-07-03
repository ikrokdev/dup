import os
import pandas as pd
from dataclasses import dataclass

from domain.conversation.conversation import Conversation
from domain.conversation.speaker import Speaker
from domain.conversation.sentence import Sentence
from domain.conversation.speaker_turn import SpeakerTurn
from domain.conversation.word import Word
from domain.conversation.time_range import TimeRange


@dataclass
class ConversationLoader:
    def __init__(self):
        pass

    def save(self, conversation: Conversation, folder_name: str = None):

        if not os.path.exists(folder_name):
            os.makedirs(folder_name)

        turns_data = []
        words_data = []
        sentences_data = []
        for turn in conversation.turns:
            turns_data.append({
                'turn_id': turn.turn_id,
                'speaker_id': turn.speaker_id,
                'start': turn.time_range.start,
                'end': turn.time_range.end,
                'text': turn.text
            })

            for sentence in turn.sentences:
                sentences_data.append({
                    'turn_id': turn.turn_id,
                    'sentence_id': sentence.sentence_id,
                    'start': sentence.time_range.start,
                    'end': sentence.time_range.end,
                    'text': sentence.text,
                })

            for word in turn.words:
                words_data.append({
                    'turn_id': turn.turn_id,
                    'start': word.time_range.start,
                    'end': word.time_range.end,
                    'score': word.score,
                    'word': word.word,
                })

        turns_data = sorted(turns_data, key=lambda x: x['end'])
        sentences_data = sorted(sentences_data, key=lambda x: x['end'])
        # words_data = sorted(words_data, key=lambda x: x['end'])

        turns_df = pd.DataFrame(turns_data)
        turns_df.to_csv(os.path.join(folder_name, "conversation.csv"), index=False)

        sentences_df = pd.DataFrame(sentences_data)
        sentences_df.to_csv(os.path.join(folder_name, "sentences.csv"), index=False)

        words_df = pd.DataFrame(words_data)
        words_df.to_csv(os.path.join(folder_name, "words.csv"), index=False)

    def load(self, folder_name: str) -> Conversation:
        conversation = Conversation(conversation_id='1', speakers={})
        speakers = conversation.speakers

        # Load the data from files
        turns_df = pd.read_csv(os.path.join(folder_name, "conversation.csv"))
        sentences_df = pd.read_csv(os.path.join(folder_name, "sentences.csv"))
        words_df = pd.read_csv(os.path.join(folder_name, "words.csv"))
        topics_df = pd.read_csv(os.path.join(folder_name, "topics.csv"))

        # Process each turn
        for _, turn_row in turns_df.iterrows():
            speaker_id = turn_row['speaker_id']
            turn_id = turn_row['turn_id']

            if speaker_id not in speakers:
                speakers[speaker_id] = Speaker(speaker_id=speaker_id)

            turn = SpeakerTurn(
                turn_id=turn_id,
                speaker_id=speaker_id,
                text=turn_row['text'],
                time_range=TimeRange(start=turn_row['start'], end=turn_row['end'])
            )

            # Find corresponding topics for this turn
            if turn_id in topics_df['turn_id'].values:
                turn_topics = topics_df[topics_df['turn_id'] == turn_id]['topics'].iloc[0]
                # Assuming topics are stored as a string representation of a list
                turn.add_topics(turn_topics.strip("[]").split(", "))

            # Filter and add sentences to this turn
            turn_sentences_df = sentences_df[sentences_df['turn_id'] == turn_id]
            for _, sentence_row in turn_sentences_df.iterrows():
                sentence = Sentence(
                    sentence_id=sentence_row['sentence_id'],
                    speaker_id=speaker_id,
                    text=sentence_row['text'],
                    time_range=TimeRange(start=sentence_row['start'], end=sentence_row['end'])
                )
                turn.add_sentence(sentence)

            turn_words_df = words_df[words_df['turn_id'] == turn_id]
            for _, word_row in turn_words_df.iterrows():
                word = Word(
                    word=word_row['word'],
                    time_range=TimeRange(start=word_row['start'], end=word_row['end']),
                    score=word_row.get('score', 0),
                )
                turn.add_word(word)

            conversation.add_turn(turn)

        return conversation

if __name__ == '__main__':
    filename = '../---/segments.json'
    loader = ConversationLoader()
    conversation = loader.load("c:\\_\\dub\\app\\---")
    loader.save(conversation, '../res---')
