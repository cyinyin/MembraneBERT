import os
import sys


class Args:
    def __init__(self):
        # Get the current file path
        self._curr_dir, _curr_file_name = os.path.split(os.path.abspath(__file__))  # unit path.py

        # Root directory
        self._root = os.path.abspath(os.path.join(self._curr_dir, ".."))
        self.data_path = os.path.join(self._root, 'data')
        self.dataset_path = os.path.join(self._root, 'dataset')
        self.pdf_path = os.path.join(self.data_path, 'pdf')
        self.plain_text_path = os.path.join(self.data_path, 'plain_text')
        self.dataset_path = os.path.join(self._root, 'dataset')
        self.unit_path = os.path.join(self._root, 'unit')
        self.outputs_path = os.path.join(self.unit_path, 'outputs')
        self.extracted_results_path = os.path.join(self.unit_path, 'extracted_results')
        self.papers = os.path.join(self.data_path, 'papers.xlsx')
        self.MOF_COF = os.path.join(self.data_path, 'MOF-COF.xlsx')
        self.model_path = os.path.join(self.unit_path, 'model')
        self.pic_path = os.path.join(self.unit_path, 'pic')
        # print(self.pdf_path)

if __name__ =='__main__':
    Args()