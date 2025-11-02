# MembraneBERT :A Domain-Tailored Natural Language Processing Model for Automated Information Extraction in Membrane Separation
Separation process is the core link of chemical production, widely used in purification, resource recovery and environmental protection, etc., and the energy consumption accounts for about 45% of the total energy consumption of the industry. Membrane separation technology is getting more and more attention due to its advantages of low energy consumption, simple operation and easy regulation, in which the performance of membrane material is the key to determine the separation efficiency.

At present, a large amount of literature has reported the experimental data and industrial application cases related to membrane separation, which can truly reflect the performance of materials under different conditions, with wide coverage. The automatic extraction of unstructured information in the literature by natural language processing (NLP) technology can not only significantly improve the processing efficiency and reduce the labor cost, but also accelerate the data structuring and integration, which can help the research and application of membrane separation.

MembraneBERT is a model based on NLP technology for extracting membrane separation related information from the literature.
## Requirements

- Python(>=3)
    
Python modules（version used in this work）    

- pandas (2.0.3)
- numpy (1.24.3)
- scipy (1.10.1)
- transformers (4.46.3)
- datasets (2.19.1)
- torch (2.4.1)
- bs4 (0.0.2)
- requests (2.32.3)
 
## Project structure
```bash
root
|-- data        // Updating model vocabulary data
|   |--membrane_fill_name.txt        // Filling material information
|   |--membrane_name.txt        // Membrane name information
|-- dataset    
|-- unit // model training
|   |-- result     // The model after training is completed
|   |-- scibert_scivocab_cased     // Pre-trained models
|   |-- get_sci-hub.py  //  Download article (PDF) 
|   |-- make_tag.py     //  Automatically label text with O
|   |-- model.py     // Training models
|   |-- ConnenctionPaper.py  // Getting article information via ConnectionPaper 
|   |-- path.py  // Pathway 
|   |-- pdf_text.py     // Extract plain text from PDF
|   |-- read_excel_doi.py     // Reading DOI numbers from excel
|   |-- test_model.py  // Testing the trained model
|   |-- wordtojson.py  // Convert word documents into JSON format according to the paragraph
```
## Usage：
1、Place the PDF file to be processed in the data/pdf folder;
2、Run the pdf_text.py script to extract the plain text content from the PDF;
3、Run test_model.py script to process the extracted text;
The results will be saved in the . /outputs folder.

## Test model (See test.py for details):
 text = "The ZIF-301 exhibited a significantly higher permeance for H₂ compared to CH₄, resulting in an H2/CH4 selectivity of 12.5 at 25 °C and 1 bar,." ，膜分离信息为：
Exports (See extracted_record.json for details)：
{
  "metadata": {
    "timestamp": "2025-07-01T08:52:14.447467",
    "model": "",
    "source": "MembraneBERT"
  },
  "original_text": "The MMM was prepared by blending Pebax with 20 wt% ZIF-8. The membrane showed a CO2 permeability of 123 Barrer and CO2/N2 selectivity of 35 at 25°C.",
  "extracted_data": {
    "Membrane_Name": "MMM",
    "Fill_Name": "Pebax ZIF-8",
    "Fill_Ratio": "20",
    "Gas": "CO2 CO2/N2",
    "Permeability": "123",
    "Permeability_Unit": "barrer",
    "Selectivity": "35",
    "Temperature": "25°c"
  }
}
  ```
