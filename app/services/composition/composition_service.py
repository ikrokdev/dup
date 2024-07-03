from datetime import datetime
import pandas as pd
from .proto import composition_pb2, composition_pb2_grpc
import os


class CompositionService(composition_pb2_grpc.CompositionServiceServicer):

    def create_ls(self, base_folder):
        # Initialize an empty DataFrame to hold all metadata
        all_metadata = pd.DataFrame(columns=[
            "conv_id", "source_path", "video_id", "channel_id",
            "title", "duration", "upload_date", "view_count",
            "description", "created_at", "updated_at"
        ])

        # Walk through the directory structure
        for root, dirs, files in os.walk(base_folder):
            # Check if 'metadata.csv' exists in the directory
            if 'video_metadata.csv' in files:
                # Construct the full path to the metadata.csv file
                metadata_file = os.path.join(root, 'video_metadata.csv')

                # Read the metadata.csv file into a DataFrame
                metadata_df = pd.read_csv(metadata_file)

                # Get the creation and last modified date of the file
                created_at = datetime.fromtimestamp(os.path.getctime(metadata_file))
                updated_at = datetime.fromtimestamp(os.path.getmtime(metadata_file))

                # Populate the additional columns
                metadata_df['conv_id'] = metadata_df['video_id']
                metadata_df['source_path'] = os.path.relpath(root, base_folder)
                metadata_df['created_at'] = created_at
                metadata_df['updated_at'] = updated_at

                # Append this data to the all_metadata DataFrame
                all_metadata = all_metadata._append(metadata_df, ignore_index=True)

        # Save the collected data to 'ls.csv' file
        all_metadata.to_csv(os.path.join(base_folder, 'ls.csv'), index=False)

    def GetComposition(self, request, context):
        # Construct the path to the composition folder
        folder_path = os.path.join('../data/',f"{request.username}@comp-{request.composition_id}")
        # Check if the ls.csv file exists
        ls_csv_path = os.path.join(folder_path, 'ls.csv')
        if not os.path.exists(ls_csv_path):
            # If ls.csv does not exist, gather metadata and create it
            self.create_ls(folder_path)

        df = pd.read_csv(ls_csv_path)

        # Create Composition object
        composition_items = []

        for index, row in df.iterrows():
            # You can add print statements here to check each field's type
            print("Index:", index)
            print("Source Path:", row['source_path'], type(row['source_path']))
            print("Title:", row['title'], type(row['title']))
            print("Duration:", row['duration'], type(row['duration']))
            print("Description:", row['description'], type(row['description']))
            print("Created At:", row['created_at'], type(row['created_at']))
            print("File Path:", ls_csv_path, type(ls_csv_path))

            # Creating FileMetadata object
            file_metadata = composition_pb2.FileMetadata(
                created_at=str(row['created_at']),
                filepath=ls_csv_path,
                title=row['title']
            )

            # Creating CompositionItem object
            composition_item = composition_pb2.CompositionItem(
                id=str(index),
                source_path=row['source_path'],
                title=row['title'],
                duration=str(row['duration']),  # Assuming duration is a string
                description=str(row['description'])
            )

            # Adding the CompositionItem to the list
            composition_items.append(composition_item)

        file_metadata = composition_pb2.FileMetadata(
            created_at=str(pd.to_datetime(df['created_at']).min()),  # Assuming 'created_at' is the same for all rows
            filepath=ls_csv_path,
            title=folder_path
        )

        composition = composition_pb2.Composition(
            items=composition_items,
            metadata=file_metadata
        )

        return composition_pb2.GetCompositionResponse(composition=composition)
