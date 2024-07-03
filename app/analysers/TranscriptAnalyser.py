import json
import pandas as pd
import os


class TranscriptAnalyzer:
    def __init__(self, file_path):
        self.file_path = file_path
        self.data = self.load_data()

    def load_data(self):
        try:
            df = pd.read_csv(self.file_path, delimiter='|')  # , names=['start', 'end', 'text', 'words', 'speaker']
            # df['text'] = df['words'].apply(lambda x: json.loads(x))
            return df
        except Exception as e:
            print(f"Error loading data: {e}")
            return pd.DataFrame()

    def combine_speaker_text(self):
        combined_text = []
        current_speaker = None
        current_text = ""
        start_time = None
        end_time = None

        for row in self.data.itertuples():
            if row.speaker == current_speaker:
                # Concatenate the text and update the end time
                current_text += " " + row.text
                end_time = row.end
            else:
                # Save the previous speaker's text (if not empty)
                if current_text:
                    combined_text.append((current_speaker, start_time, end_time, current_text))
                # Start new text concatenation
                current_speaker = row.speaker
                current_text = row.text
                start_time = row.start
                end_time = row.end

        # Add the last speaker's text
        if current_text:
            combined_text.append((current_speaker, start_time, end_time, current_text))

        combined_df = pd.DataFrame(combined_text, columns=['speaker', 'start', 'end', 'text'])
        return combined_df

    def save_speaker_turns(self):
        combined_df = self.combine_speaker_text()
        output_file_path = os.path.join(os.path.dirname(self.file_path), 'speaker_turns.csv')
        combined_df.to_csv(output_file_path, index=False)
        print(f"Combined speaker rounds saved to {output_file_path}")

    def analyze_speakers(self):
        analysis = {}
        end_time = 0
        last_speaker = None

        # Iterate through each row in the dataframe
        for entry in self.data.itertuples():
            start_time, end_time_entry, current_speaker = entry.start, entry.end, entry.speaker
            duration = end_time_entry - start_time

            if current_speaker not in analysis:
                analysis[current_speaker] = {"Frequency": 0, "Total Duration": 0, "Interruptions Caused": 0}

            analysis[current_speaker]["Frequency"] += 1
            analysis[current_speaker]["Total Duration"] += duration

            if start_time < end_time and current_speaker != last_speaker:
                analysis[current_speaker]["Interruptions Caused"] += 1

            end_time = max(end_time, end_time_entry)
            last_speaker = current_speaker

        return analysis

    def temporal_analysis(self):
        temporal_data = {}
        for entry in self.data.itertuples():
            speaker = entry.speaker
            duration = entry.end - entry.start

            if speaker not in temporal_data:
                temporal_data[speaker] = {"Total Duration": 0, "Segment Durations": []}

            temporal_data[speaker]["Total Duration"] += duration
            temporal_data[speaker]["Segment Durations"].append(duration)

        for speaker, data in temporal_data.items():
            durations = data["Segment Durations"]
            data["Average Duration"] = sum(durations) / len(durations) if durations else 0
            data["Max Duration"] = max(durations) if durations else 0
            data["Min Duration"] = min(durations) if durations else 0

        return temporal_data

    def get_segments_in_range(self, start_time, end_time):
        segments = []
        for entry in self.data.itertuples():
            if start_time <= entry.start < end_time:
                segments.append(entry)
        return segments

    def save_individual_speaker_analysis(self):
        speaker_analysis = self.analyze_speakers()
        temporal_data = self.temporal_analysis()

        # Get the directory of the original file
        output_folder = os.path.dirname(self.file_path)

        for speaker, data in speaker_analysis.items():
            output_file_path = os.path.join(output_folder, f"temporal_analysis.{speaker}.json")
            analysis_data = {
                "Speaker Analysis": data,
                "Temporal Analysis": temporal_data.get(speaker, {})
            }
            try:
                with open(output_file_path, 'w') as file:
                    json.dump(analysis_data, file, indent=4)
                print(f"Analysis for {speaker} saved to {output_file_path}")
            except Exception as e:
                print(f"Error saving analysis for {speaker}: {e}")


def process_file(file_path):
    analyzer = TranscriptAnalyzer(file_path)
    speaker_analysis = analyzer.analyze_speakers()
    temporal_analysis = analyzer.temporal_analysis()
    # segments = analyzer.get_segments_in_range(0, 300)
    analyzer.save_individual_speaker_analysis()
    analyzer.save_speaker_turns()


def process_directory(directory):
    for root, dirs, files in os.walk(directory):
        for filename in files:
            if filename.endswith(".segments.csv"):
                process_file(os.path.join(root, filename))


if __name__ == '__main__':
    directory = '../../---'
    process_directory(directory)
