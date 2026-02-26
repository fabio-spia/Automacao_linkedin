from datetime import datetime
import math
import random
import time
from config import get_driver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from conection_sheet import adicionar_registro
from cookies import loads_cookies
COOKIE_FILE_PATH ="data/cookie_file_path.json" # Arquivo com cookies do perfil

def extract_metrics(driver):
    driver.get("https://www.linkedin.com/sales/ssi")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    time.sleep(random.randint(5, 10))  

    marca_profissional = driver.find_element(
        By.ID, "establish-brand__sub-score-bar"
    ).get_attribute("value")

    localizar_pessoas = driver.find_element(
        By.ID, "find-people__sub-score-bar"
    ).get_attribute("value")

    interagir = driver.find_element(
        By.ID, "engage-with-insights__sub-score-bar"
    ).get_attribute("value")

    criar_relacionamentos = driver.find_element(
        By.ID, "build-relationships__sub-score-bar"
    ).get_attribute("value")

    ssi = math.ceil(float(marca_profissional)+float(localizar_pessoas)+float(interagir)+float(criar_relacionamentos))

    data = datetime.now().strftime("%d/%m/%y")

    print(marca_profissional)
    print(localizar_pessoas)
    print(interagir)
    print(criar_relacionamentos)
    print(ssi)
    
    print("Registrando no google sheets...")
    #Adcionar na planilha 
    row = [data, marca_profissional, localizar_pessoas, interagir, criar_relacionamentos, ssi]
    adicionar_registro(row,"Métricas")

if __name__ == "__main__":
    driver = get_driver()   # Abre o browser
    driver.get("https://www.linkedin.com")  # Abre LinkedIn
    loads_cookies(driver, COOKIE_FILE_PATH)
    extract_metrics(driver)