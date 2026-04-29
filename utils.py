import pandas as pd
from pathlib import Path
import re
from os import getcwd

class Utils:
    
    def load(path:str='/datasets', *datasets:int) -> pd.DataFrame:
        """Carrega os datasets informados da pasta atual.
        Args:
            path: Diretório onde estão os csv dos datasets
            datasets: Número do datasets para carregar que estão no diretório informado
        Returns:
            dataset: Datasets concatenados e indicados por número
        """
        if not datasets:
            datasets = [re.search(r'\d{1,2}',f.name).group() for f in Path(getcwd()+path).iterdir() if f.is_file()]
        dataset = pd.DataFrame(columns=['dataset', 'file', 'content'])
        for i in datasets:
            temp_dt = pd.read_csv(f'{getcwd()+path}/dataset{i}.csv', sep='|')
            temp_dt['dataset'] = i
            dataset = pd.concat([dataset, temp_dt])
        dataset = dataset.sort_values('content', na_position='first')
        dataset = dataset.drop_duplicates(keep='last')
        return dataset