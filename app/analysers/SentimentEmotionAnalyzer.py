import os
from collections import Counter
import nltk
import pandas as pd
from nltk.corpus import stopwords
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.tokenize import word_tokenize
from transformers import pipeline

class SentimentEmotionAnalyzer:
    def __init__(self, file_path, sentiment_model="siebert/sentiment-roberta-large-english", emotion_model="SamLowe/roberta-base-go_emotions"):
        self.file_path = file_path
        self.sentiment_analysis = pipeline("sentiment-analysis", model=sentiment_model)
        self.emotion_classifier = pipeline(task="text-classification", model=emotion_model, top_k=None)

        nltk.download('vader_lexicon')
        self.sia = SentimentIntensityAnalyzer()

    def get_polarity_compound_score(self, text):
        return self.sia.polarity_scores(text)['compound']

    def get_sentiment(self, text):
        return self.sentiment_analysis(text)

    def get_emotion(self, text):
        model_outputs = self.emotion_classifier(text)[0]
        return model_outputs[0]

    def analyze(self, analyses):
        main_df = pd.read_csv(self.file_path, delimiter='|')
        results = {'main': main_df}

        if 'sentiments' in analyses:
            results['sentiments'] = pd.DataFrame(main_df['text'].apply(self.get_sentiment).tolist())
            results['sentiments']['index'] = main_df.index

        if 'emotions' in analyses:
            results['emotions'] = pd.DataFrame(main_df['text'].apply(self.get_emotion).tolist())
            results['emotions']['index'] = main_df.index

        if 'topics' in analyses:
            results['topics'] = self.analyze_topics()

        return results

    def analyze_topics(self, top_n=100):
        nltk.download('punkt')
        nltk.download('stopwords')
        nltk_words = set(stopwords.words('english'))
        word_counter = Counter()

        df = pd.read_csv(self.file_path, delimiter='|')
        for text in df['text']:
            tokens = word_tokenize(text.lower())
            tokens = [word for word in tokens if word.isalpha() and word not in nltk_words]
            word_counter.update(tokens)

        topics_df = pd.DataFrame(word_counter.most_common(top_n))
        return topics_df

    def save_results(self, results):
        directory = os.path.dirname(self.file_path)

        for key, df in results.items():
            if key != 'main' and not df.empty:
                filename = os.path.join(directory, f'segments.{key}.csv')
                df.to_csv(filename, index=False)

def process_file(file_path):
    base_name = os.path.splitext(file_path)[0]
    print(
        'Processing file {0} '.format(file_path)
    )
    analyzer = SentimentEmotionAnalyzer(file_path)
    results = analyzer.analyze(['sentiments', 'emotions', 'topics'])
    # results = analyzer.analyze(['topics'])
    analyzer.save_results(results)

def process_directory(directory):
    for root, dirs, files in os.walk(directory):
        for filename in files:
            if filename.endswith(".segments.csv"):
                process_file(os.path.join(root, filename))


if __name__ == '__main__':
    directory = '../../---'
    process_directory(directory)
