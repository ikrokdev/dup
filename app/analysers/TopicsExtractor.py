import os
import pandas as pd
from openai import OpenAI
import configparser
import json


class TopicsExtractor:
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)
        # OpenAI(base_url="http://localhost:1234/v1", api_key=openai_api_key)

    def validate_content(self, content):
        try:
            # Try parsing as JSON
            parsed = json.loads(content)
            if isinstance(parsed, list):
                return parsed  # Return the list if content is a JSON array of strings
            else:
                return parsed  # Return the JSON object if it's JSON but not an array of strings
        except json.JSONDecodeError:
            # Not JSON
            return None  # Return None if content is not JSON

    def summarize_text(self, text):
        try:
            # Constructing the message payload for the API request
            messages = [
                {
                    'role': 'system',
                    'content': 'What specific goal is this statement aiming to achieve in the context of the sales process, and how does it align with the stages of introduction, needs assessment, product presentation, handling objections, closing the sale, or follow-up?',
                    #'content': 'provide a few (up to 5) main topic names on given text response should be provided as a simple json array'
                },
                {
                    'role': 'user',
                    'content': f'Text: {text}  provide an answer in json array only, in curly brackets there must be only two keys "Goal" and "Alignment" and their values, do not add anything else'
                }
            ]

            MODEL = "gpt-3.5-turbo"
            response = self.client.chat.completions.create(
                model=MODEL,
                messages=messages,
                temperature=0.1,
                max_tokens=100
            )

            # Extracting the content from the response
            if response.choices:
                try:
                    content = response.choices[0].message.content
                    print(content)
                    if self.validate_content(content) is not None:
                        return content
                except Exception as e:
                    print(e)
                    return None
            return ""

        except Exception as specific_error:
            print(f"Error: {specific_error}")  # More specific error message
            return f"Error in summarization: {specific_error}"

    def save_summary(self, df, filename):
        df.to_csv(filename, index=False)


def process_file(file_path, api_key):
    summarizer = TopicsExtractor(api_key)
    df = pd.read_csv(file_path)

    topics_data = []
    print(df)

    for index, row in df[:1000].iterrows():
        turn_id = index  #row['turn_id']
        text = row['text']
        print('text'*10, text)
        summary = summarizer.summarize_text(text)
        print('summ'*10, summary.replace('\n', ''))
        # Assuming summary is a JSON array of topics
        topics = json.loads(summary.replace('\n', '').strip())

        topics_data.append({
            'turn_id': turn_id,
            'topics': topics
        })

    topics_df = pd.DataFrame(topics_data)
    output_filename = os.path.join(os.path.dirname(file_path), 'topics.csv')
    topics_df.to_csv(output_filename, index=False)


def process_directory(directory, api_key):
    for root, dirs, files in os.walk(directory):
        for filename in files:
            if filename.endswith("speaker_turns.csv"):
                process_file(os.path.join(root, filename), api_key)


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('config.ini')

    api_key = config['OPEN_AI']['API_KEY']
    directory = '../../---'
    process_directory(directory, api_key)
