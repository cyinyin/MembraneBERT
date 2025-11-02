import os
import json
import re
from unit.path import Args
from docx import Document


def read_word_file(file_path):
    doc = Document(file_path)
    data = []

    for para in doc.paragraphs:
        tokens = []
        labels = []

        # Split text using regular expressions, matching words and labels
        items = re.findall(r'(\S+):\s*(\S+)', para.text)

        for word, label in items:
            tokens.append(word.strip())
            labels.append(label.strip())

        if tokens and labels:
            data.append({"tokens": tokens, "labels": labels})

    return data


def process_directory(input_directory, output_directory):
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    for filename in os.listdir(input_directory):
        if filename.endswith('.docx'):
            file_path = os.path.join(input_directory, filename)
            file_data = read_word_file(file_path)

            if not file_data:
                print(f"No valid data found in {filename}")

            json_filename = f"{os.path.splitext(filename)[0]}.json"
            json_path = os.path.join(output_directory, json_filename)

            with open(json_path, 'w', encoding='utf-8') as json_file:
                json.dump(file_data, json_file, ensure_ascii=False, indent=4)


input_directory = 'D:/test_tag'
output_directory = 'D:/test_json'

process_directory(input_directory, output_directory)
