from selenium.webdriver import ChromeOptions 
from selenium.webdriver.common.by import By
from seleniumrequests import Chrome as Chrome
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium_stealth import stealth
import os

class Downloader:
    
    def __init__(self):
        """Cria webdriver e marca a verificação de idade. Configura pasta de downloads
        """
        self.download_dir = os.path.join(os.getcwd(), "downloads")
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)
            
        self.base_url = ['https://www.justice.gov/epstein/files/DataSet%20','/EFTA','.pdf']
        
        self.driver = self.start_wd()
        self.driver.get('https://www.justice.gov/age-verify?')
        self.driver.find_element(By.ID, 'age-button-yes').click()
    
    def start_wd(self):
        """Configura webdriver

        Returns:
            driver: webdriver seleniumrequests
        """
        service = ChromeService(executable_path=ChromeDriverManager().install())
        options = ChromeOptions()
        options.add_argument("--headless")
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-popup-blocking')
        options.add_argument('--start-maximized')
        options.add_argument('--disable-extensions')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        
        driver = Chrome(service=service, options=options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        
        stealth(driver,
            languages=["pt-BR", "en-US"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
            )

        return driver
    
    def request(self, URL:str, method:str='GET', stream:bool=True, **kwargs):
        return self.driver.request(method, URL, stream=stream, **kwargs)
        
    def get(self, URL:str):
        return self.driver.get(URL)
    
    def download_all_dataset(self, dataset:int, file_start:int, file_end:int):
        """Download de arquivos em um intervalo de um dataset escolhido

        Args:
            dataset (int): número do dataset
            file_start (int): primeiro arquivo do dataset
            file_end (int): último arquivo do dataset
        """
        for curr_file in range(file_start, file_end+1):
            file_number = '00000000'[:-len(str(curr_file))] + str(curr_file)
            URL = self.base_url[0] + str(dataset) + self.base_url[1] + file_number + self.base_url[2]
                    
            response = self.request(URL)
            if response.status_code == 200:
                with open(self.download_dir + f'\{curr_file}.pdf', 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
            else:
                print(f"Failed to download {file_number}. Status code: {response.status_code}")
                break
        self.driver.close()
        self.driver.quit()