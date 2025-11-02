from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
import json
import os
from datetime import datetime


def get_current_timestamp():
    return datetime.now().isoformat()


def structure_entities(entities):
    data = {}
    current_field = None

    for ent in entities:
        ent_type = ent["entity_group"]
        value = ent["word"].replace("##", "").replace(" ", "")

        if ent_type == "O" or ent_type == "LABEL_0":
            continue

        if ent_type == "Permeability":
            if "Permeability" not in data:
                data["Permeability"] = value
            else:
                data["Permeability"] += f" {value}"

        elif ent_type == "Permeability_Unit":
            data["Permeability_Unit"] = value

        elif ent_type == "Permeance":
            if "Permeance" not in data:
                data["Permeance"] = value
            else:
                data["Permeance"] += f" {value}"

        elif ent_type == "Permeance_Unit":
            data["Permeance_Unit"] = value

        elif ent_type == "Selectivity":
            if "Selectivity" not in data:
                data["Selectivity"] = value
            else:
                data["Selectivity"] += f" {value}"

        elif ent_type == "Temperature":
            if "Temperature" not in data:
                data["Temperature"] = value
            else:
                data["Temperature"] += f" {value}"

        elif ent_type == "Fill_Ratio":
            if "Fill_Ratio" not in data:
                data["Fill_Ratio"] = value
            else:
                data["Fill_Ratio"] += f" {value}"

        else:
            if ent_type not in data:
                data[ent_type] = value
            else:
                data[ent_type] += f" {value}"

    return data


def generate_full_record(text, structured_data, model_path):
    return {
        "metadata": {
            "timestamp": get_current_timestamp(),
            "model": os.path.basename(model_path),
            "source": "MembraneBERT"
        },
        "original_text": text.strip(),
        "extracted_data": structured_data
    }


# Load model and tokenizer
model_path = "MembraneBERT/"
tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForTokenClassification.from_pretrained(model_path)
ner_pipeline = pipeline("ner", model=model, tokenizer=tokenizer, aggregation_strategy="simple")

# input text
text = """
The MMM was prepared by blending Pebax with 20 wt% ZIF-8. The membrane showed a CO2 permeability of 123 Barrer and CO2/N2 selectivity of 35 at 25°C.
"""

# Perform entity recognition
entities = ner_pipeline(text)

# Extract structured information
structured_data = structure_entities(entities)

# Generate full record
full_record = generate_full_record(text, structured_data, model_path)

# Print or save results
print("Full record:")
print(json.dumps(full_record, indent=2, ensure_ascii=False))

# Optional: save to file
with open("extracted_record.json", "w", encoding="utf-8") as f:
    json.dump(full_record, f, indent=2, ensure_ascii=False)
