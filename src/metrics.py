from datetime import datetime
import math
import os
import random
import time
from config import get_driver
import json
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from conection_sheet import autenticar_google_sheets

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
    ABA = "Métricas"
    row = [data, marca_profissional, localizar_pessoas, interagir, criar_relacionamentos, ssi]
    json_keyfile = "credentials/google_sheets_credentials.json"
    nome_planilha = os.getenv("NAME_SHEET") # Preencha de acordo com sua variavel no arquivo .env
    sheet = autenticar_google_sheets(json_keyfile, nome_planilha, ABA)
    sheet.append_row(row)

if __name__ == "__main__":
    driver = get_driver()   # Abre o browser
    driver.get("https://www.linkedin.com")  # Abre LinkedIn

    # Carrega cookies do JSON
    with open(COOKIE_FILE_PATH, "r", encoding="utf-8") as f:
        cookies = json.load(f)

    for cookie in cookies:
        if "sameSite" in cookie:
            if cookie["sameSite"] not in ["Strict", "Lax", "None"]:
                del cookie["sameSite"]
        driver.add_cookie(cookie)
    WebDriverWait(driver, 30).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )

    # ✅ Verifica se foi redirecionado para login (cookies expirados)
    if "login" in driver.current_url:
        print("🔒 Sessão expirada. Faça login para atualizar cookies...")
        driver.quit()

        # 🧠 Abre o navegador e pede login manual
        from save_cookies import save_cookies #Importar cookies do perfil desejado 
        save_cookies()

        print("✅ Cookies atualizados. Execute novamente")
    
    extract_metrics(driver)