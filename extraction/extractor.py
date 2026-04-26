import pdfplumber
import os
import re
import pandas as pd

class Extractor:
    
    def __init__(self):
        self.download_dir = os.path.join(os.getcwd(), "downloads")
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)
            
    def extract_from_files(self, dataset:int, file_start:int, file_end:int):
        """Extração de texto baixados de arquivos em um intervalo de um dataset escolhido

        Args:
            dataset (int): número do dataset
            file_start (int): primeiro arquivo do dataset
            file_end (int): último arquivo do dataset
        """
        path = os.path.join(os.getcwd(), f'..\\dataset{dataset}.csv')
        if not os.path.exists(path):
            dt = pd.DataFrame(columns=['file', 'content'])
        else:
            dt = pd.read_csv(path)
        
        text_content = [[0,''] for i in range(file_start, file_end+1)]
        for curr_file in range(file_start, file_end+1):
            try:
                with pdfplumber.open(self.download_dir + f'\{curr_file}.pdf') as pdf:
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if re.search(r'EFTA\d{8}' , page_text[-12:]): page_text = page_text[:-12]
                        text_content[curr_file-1][0] = curr_file
                        text_content[curr_file-1][1] += page_text
            except:
                print(f'Exceção: arquivo {curr_file}')
                text_content = text_content[:curr_file-1]
                break
        
        new = pd.DataFrame(data=text_content, columns=['file','content'])
        dt = pd.concat([dt, new], ignore_index=True)
        dt.to_csv(path)