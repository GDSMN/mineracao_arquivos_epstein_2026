import pdfplumber
import os
import re
import pandas as pd
import time

class Extractor:
    
    def __init__(self):
        self.download_dir = os.path.join(os.getcwd(), "downloads")
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)
            
    def extract_from_files(self, dataset:int, file_list:list):
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
        
        text_content = [[0,''] for i in range(len(file_list))]
        failed = 0
        for i, curr_file in enumerate(file_list):
            file_number = int(curr_file[4:12])
            while not os.path.exists(self.download_dir + f'\{curr_file}'):
                time.sleep(3)
            try:
                with pdfplumber.open(self.download_dir + f'\{curr_file}') as pdf:
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if re.search(r'EFTA\d{8}' , page_text[-12:]): page_text = page_text[:-12]
                        text_content[i][0] = curr_file
                        text_content[i][1] += page_text
                os.remove(self.download_dir + f'\{curr_file}')
                failed = 0
            except:
                print(f'Exceção: arquivo {curr_file}')
                failed += 1
                if failed > 20:
                    break
        
        new = pd.DataFrame(data=text_content, columns=['file','content'])
        dt = pd.concat([dt, new], ignore_index=True)
        dt.to_csv(path)