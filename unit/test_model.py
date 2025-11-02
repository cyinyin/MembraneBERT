from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
import json
import os
import torch
from datetime import datetime
from docx import Document
import traceback
from unit.path import Args

tokenizer = AutoTokenizer.from_pretrained("MembraneBERT/")


def get_current_timestamp():
    return datetime.now().isoformat()


def extract_paragraphs_from_docx(docx_path):
    """Extract paragraphs from the document"""
    try:
        doc = Document(docx_path)
        return [para.text.strip() for para in doc.paragraphs if para.text.strip()]
    except Exception as e:
        print(f"Error reading {docx_path}: {str(e)}")
        return []


def filter_entities_by_score(entities, min_score=0.5):
    """Filter entities based on confidence score"""
    return [ent for ent in entities if ent.get("score", 0) >= min_score]


def merge_selected_entities(ner_results, target_labels=None):
    """
    Merge consecutive entities only for specified labels (e.g., membrane name, membrane material, filler)
    Other entities remain unchanged
    """
    if target_labels is None:
        target_labels = ["Membrane_Name", "Membrane_Material", "Fill_Name"]

    merged_entities = []
    temp = None

    for ent in ner_results:
        ent_type = ent['entity_group']
        word = ent['word'].replace('##', '').strip()
        if not word or ent_type in ["O", "LABEL_0"]:
            continue

        if ent_type in target_labels:
            if temp is None or temp['entity_group'] != ent_type:
                if temp:
                    merged_entities.append(temp)
                temp = {'entity_group': ent_type, 'word': word}
            else:
                temp['word'] += ' ' + word
        else:
            if temp:
                merged_entities.append(temp)
                temp = None
            merged_entities.append({'entity_group': ent_type, 'word': word})

    if temp:
        merged_entities.append(temp)

    return merged_entities


def structure_entities(entities):
    """Organize entities into a dictionary"""
    data = {}
    for ent in entities:
        ent_type = ent["entity_group"]
        value = ent["word"].strip()
        if not value:
            continue

        # Organize by type
        if ent_type == "Membrane_Name":
            data["Membrane_Name"] = value

        elif ent_type == "Membrane_Material":
            data.setdefault("Membrane_Materials", [])
            if value not in data["Membrane_Materials"]:
                data["Membrane_Materials"].append(value)

        elif ent_type == "Fill_Name":
            data.setdefault("Fillers", [])
            if value not in data["Fillers"]:
                data["Fillers"].append(value)

        elif ent_type == "Fill_Ratio":
            data["Fill_Ratio"] = value
        elif ent_type == "Ratio":
            data["Ratio"] = value
        elif ent_type == "Temperature":
            data["Temperature"] = value
        elif ent_type == "Pressure":
            data["Pressure"] = value
        elif ent_type == "Gas":
            data.setdefault("Gases", [])
            if value not in data["Gases"]:
                data["Gases"].append(value)
        elif ent_type == "Separation_factor":
            data["Separation_factor"] = value
        elif ent_type == "Permeance":
            data["Permeance"] = value
        elif ent_type == "Permeance_Unit":
            data["Permeance_Unit"] = value
        elif ent_type == "Permeability":
            data["Permeability"] = value
        elif ent_type == "Permeability_Unit":
            data["Permeability_Unit"] = value
        elif ent_type == "Selectivity":
            data["Selectivity"] = value
        else:
            data.setdefault("Other", [])
            data["Other"].append({"type": ent_type, "value": value})

    return data  


def split_text(paragraph, tokenizer, max_tokens=512):
    tokens = tokenizer(paragraph, return_offsets_mapping=True, add_special_tokens=False)
    input_ids = tokens["input_ids"]

    chunks = []
    for i in range(0, len(input_ids), max_tokens):
        chunk_ids = input_ids[i:i+max_tokens]
        chunk_text = tokenizer.decode(chunk_ids)
        chunks.append(chunk_text)
    return chunks

def process_paragraph(paragraph, ner_pipeline, para_idx, tokenizer, min_score=0.5):
    """Process a single paragraph"""
    try:
        # Split by token count instead of character count
        tokens = tokenizer(paragraph, return_offsets_mapping=True, add_special_tokens=False)
        if len(tokens["input_ids"]) > 512:
            chunks = split_text(paragraph, tokenizer, max_tokens=512)
            entities = []
            for chunk in chunks:
                entities.extend(ner_pipeline(chunk))
        else:
            entities = ner_pipeline(paragraph)

        # Filter by confidence
        entities = filter_entities_by_score(entities, min_score=min_score)

        # Keep only target labels
        entities = merge_selected_entities(
            entities,
            target_labels=["Membrane_Name", "Membrane_Material", "Fill_Name"]
        )

        return {
            "paragraph_index": para_idx,
            "text": paragraph,
            "entities": structure_entities(entities)
        }
    except Exception as e:
        print(f"Error processing paragraph {para_idx}: {str(e)}")
        return {
            "paragraph_index": para_idx,
            "text": paragraph,
            "entities": {}
        }


def process_single_file(docx_path, model, tokenizer, output_dir, min_score=0.5):
    """Process a single file"""
    try:
        paragraphs = extract_paragraphs_from_docx(docx_path)
        if not paragraphs:
            return {"error": "Empty document", "file": docx_path}

        # Initialize pipeline
        ner_pipeline = pipeline(
            "ner",
            model=model,
            tokenizer=tokenizer,
            aggregation_strategy="simple",
            device=0 if torch.cuda.is_available() else -1
        )

        results = []
        for idx, para in enumerate(paragraphs):
            para_result = process_paragraph(
                para,
                ner_pipeline,
                idx,
                tokenizer,
                min_score=min_score
            )
            results.append(para_result)

        # Build record
        record = {
            "metadata": {
                "timestamp": get_current_timestamp(),
                "file_name": os.path.basename(docx_path),
                "paragraph_count": len(paragraphs),
                "processed_paragraphs": len(results),
                "model": os.path.basename(model_path)
            },
            "content": results
        }

        # Save JSON
        output_file = f"{os.path.splitext(os.path.basename(docx_path))[0]}.json"
        output_path = os.path.join(output_dir, output_file)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(record, f, indent=2, ensure_ascii=False)

        return {"success": output_path}

    except Exception as e:
        return {
            "error": str(e),
            "traceback": traceback.format_exc(),
            "file": docx_path
        }


def batch_process(input_dir, output_dir, model_path, min_score=0.5):
    os.makedirs(output_dir, exist_ok=True)

    if not os.path.exists(model_path):
        print(f"Model path does not exist: {model_path}")
        return

    # Load model
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForTokenClassification.from_pretrained(model_path)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = model.to(device)
    print(f"Model loaded successfully. Using device: {device}")

    results = []
    file_count = len([f for f in os.listdir(input_dir) if f.endswith(".docx")])
    processed_count = 0

    for filename in sorted(os.listdir(input_dir)):
        if not filename.endswith(".docx"):
            continue
        docx_path = os.path.join(input_dir, filename)
        print(f"\n[{processed_count + 1}/{file_count}] Processing: {filename}")
        result = process_single_file(docx_path, model, tokenizer, output_dir, min_score=min_score)
        results.append(result)

        if "success" in result:
            print(f"Saved successfully to: {result['success']}")
        else:
            print(f"Processing failed: {result.get('error', 'Unknown error')}")
        processed_count += 1

    # Summary report
    success_count = len([r for r in results if "success" in r])
    summary = {
        "timestamp": get_current_timestamp(),
        "input_directory": input_dir,
        "total_files": file_count,
        "success_files": success_count,
        "error_files": file_count - success_count,
        "model_used": os.path.basename(model_path),
        "device_used": device
    }
    summary_path = os.path.join(output_dir, "processing_summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(f"\nProcessing completed! Success rate: {success_count}/{file_count}")
    print(f"Detailed summary saved to: {summary_path}")


if __name__ == "__main__":
    plain_text_path = Args().plain_text_path
    config = {
        "input_dir": "D:/1111",
        "output_dir": "D:/11111",
        "model_path": "MembraneBERT/"
    }
    model_path = "MembraneBERT"
    print("=" * 50)
    print("MOF/COF Literature Data Extraction System")
    print(f"Input directory: {config['input_dir']}")
    print(f"Output directory: {config['output_dir']}")
    print("=" * 50 + "\n")

    batch_process(**config)
