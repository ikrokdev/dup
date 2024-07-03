import ast
import json
import os
from dataclasses import dataclass
import duckdb

from domain.conversation.conversation import Conversation
from domain.conversation.speaker import Speaker
from domain.conversation.speaker_turn import SpeakerTurn
from domain.conversation.sentence import Sentence
from domain.conversation.word import Word
from domain.conversation.time_range import TimeRange


class ConversationRepository:

    def __init__(self, db_path):
        self.con = duckdb.connect()
        # Create virtual tables for each CSV file with specified column names
        self.con.execute(
            f"CREATE VIEW turns AS SELECT * FROM read_csv_auto('{os.path.join(db_path, 'conversation.csv')}', header=True)")
        self.con.execute(
            f"CREATE VIEW sentences AS SELECT * FROM read_csv_auto('{os.path.join(db_path, 'sentences.csv')}', header=True)")
        self.con.execute(
            f"CREATE VIEW words AS SELECT * FROM read_csv_auto('{os.path.join(db_path, 'words.csv')}', header=True)")
        self.con.execute(
            f"CREATE VIEW topics AS SELECT * FROM read_csv_auto('{os.path.join(db_path, 'topics.csv')}', header=True)")

    def fetch_turn(self, turn_id):
        return self.con.execute(f"SELECT * FROM turns WHERE turn_id = '{turn_id}'").fetch_df().iloc[0]

    def fetch_topics_for_turn(self, turn_id):
        topics_result = self.con.execute(f"SELECT topics FROM topics WHERE turn_id = '{turn_id}'").fetchall()
        return self.parse_jarray(topics_result[0]) if topics_result else []

    def fetch_words_for_turn(self, turn_id):
        return self.con.execute(f"SELECT * FROM words WHERE turn_id = '{turn_id}'").fetchall()

    def fetch_sentences_for_turn(self, turn_id):
        return self.con.execute(
            f"SELECT sentence_id, text, start, \"end\" FROM sentences WHERE turn_id = '{turn_id}'").fetchall()

    def fetch_all_turns(self):
        return self.con.execute("SELECT * FROM turns").fetchall()

    # Close the connection if needed
    def close(self):
        self.con.close()

    def parse_jarray(self, array_str):
        try:
            # Convert the string representation to valid JSON format
            array_list = ast.literal_eval(array_str[0])
            if isinstance(array_list, list):
                return array_list
            else:
                return []
        except json.JSONDecodeError:
            return []


@dataclass
class ConversationQueries:
    db_folder: str

    def __init__(self, db_folder: str):
        self.conv_db = ConversationRepository(db_folder)

    def get_turn(self, turn_id, include_words=False):
        turn_result = self.conv_db.fetch_turn(turn_id)
        sentences = self.conv_db.fetch_sentences_for_turn(turn_id)
        topics = self.conv_db.fetch_topics_for_turn(turn_id)
        words = self.conv_db.fetch_words_for_turn(turn_id) if include_words else []

        return SpeakerTurn(
            turn_id=turn_id,
            speaker_id=turn_result['speaker_id'],
            text=turn_result['text'],
            words=[Word(word=row[4],
                        time_range=TimeRange(start=row[1], end=row[2]),
                        score=row[3])
                   for row in words],
            topics=topics,
            sentences=[Sentence(words=[],
                                sentence_id=row[0],
                                speaker_id=turn_result['speaker_id'],
                                time_range=TimeRange(start=row[2], end=row[3]),
                                text=row[1])
                       for row in sentences],
            time_range=TimeRange(start=turn_result['start'], end=turn_result['end'])
        )

    def get_conversation(self, include_words=False):
        conversation = Conversation(conversation_id='1', speakers={})
        turns_result = self.conv_db.fetch_all_turns()

        for turn_row in turns_result:
            turn = self.get_turn(turn_row[0], include_words)
            speaker_id = turn.speaker_id
            if speaker_id not in conversation.speakers:
                conversation.speakers[speaker_id] = Speaker(name=speaker_id, speaker_id=speaker_id)
            conversation.add_turn(turn)

        return conversation


if __name__ == '__main__':
    data_path = '---'
    queries = ConversationQueries(data_path)

    result = queries.get_conversation(include_words=False)
    print(result)
