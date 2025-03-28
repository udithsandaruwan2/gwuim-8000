import csv
import os
from django.conf import settings

def csv_reader(file_path):
    # Remove the '/media' part from the file path if it starts with '/media'
    if file_path.startswith('/media/'):
        file_path = file_path[len('/media/'):]

    # Construct the absolute file path using MEDIA_ROOT
    full_path = os.path.join(settings.MEDIA_ROOT, file_path)

    # Ensure the file exists
    if not os.path.exists(full_path):
        print(f"File not found: {full_path}")
        return

    # Open the CSV file and process it
    with open(full_path, mode='r', newline='', encoding='utf-8') as file:
        csv_reader = csv.reader(file)
        header = next(csv_reader)

        for row in csv_reader:
            for idx, column_data in enumerate(row):
                print(f"Column {header[idx]}: {column_data}")  # Print data corresponding to each column header
            print()
