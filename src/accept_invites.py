# TENHA O SELENIUM E WEBDRIVER INSTALADO
import csv
import random
import time
import json
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import get_driver 
import unicodedata
from bot_linkedin import extrair_dado
from send_messages import send_message
from conection_sheet import adicionar_registro
from cookies import loads_cookies

# 🔹 Caminho do arquivo que será salvo os perfis
CSV_FILE = "data/profiles.csv"
cookie_file_path = "data/cookie_file_path.json"

# Aceita convites e salva no CSV
def accept_invites(driver):
    driver.get("https://www.linkedin.com/mynetwork/invitation-manager/")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    time.sleep(random.randint(5, 10))

    # Acessar o CSV
    with open(CSV_FILE, "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        while True: 
            # 🔹 Encontrar botões "Aceitar"
            accept_buttons = driver.find_elements(By.XPATH, "//button[.//span[text()='Aceitar']]")

            if not accept_buttons:
                print("✅ Todos os convites foram aceitos!")
                break

            for btn in accept_buttons:
                try:
                    # Capturar dados
                    user_card = btn.find_element(By.XPATH, "./ancestor::*[@role='listitem']")
                    if user_card.find_elements(By.XPATH, ".//a[contains(@href,'/newsletters/')]"):
                        continue
                    user_name_element = user_card.find_element(By.XPATH, ".//strong")                    
                    user_name = user_name_element.text.strip()
                    user_name = ''.join(c for c in user_name if not unicodedata.category(c).startswith('So')) #Remover emogi                    
                    user_link = user_card.find_element(By.XPATH, ".//a[contains(@href, '/in/')]").get_attribute("href")
                    btn.click() # Aceita convite
                    aba_original = driver.current_window_handle
                    driver.execute_script("window.open(arguments[0], '_blank');", user_link)
                    driver.switch_to.window(driver.window_handles[-1])
                    time.sleep(random.randint(5, 10))
                    user_title = extrair_dado("Titulo do perfil de "+user_name)
                    print("Titulo de "+user_name+": "+user_title)
                    if user_title == False:
                        user_title = ""
                    # Manda menssagem
                    send_message(driver)
                    driver.close()
                    driver.switch_to.window(aba_original)
                    data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                   
                    # 🔹 Salvar no CSV
                    
                    time.sleep(random.randint(2, 5))
                    writer.writerow([data_hora, user_name, user_link, user_title])
                    row = [data_hora, user_name, user_link, user_title]
                    adicionar_registro(row,"AutoAccept")
                    print(f"✔ Convite aceito de {user_name} ({user_link}) em {data_hora}")
                       
                except Exception as e:
                    print(f"⚠ Erro ao aceitar convite: {e}")

            driver.refresh()
            time.sleep(random.randint(5, 10))

    

if __name__ == "__main__":
    driver = get_driver()   # Abre o browser
    driver.get("https://www.linkedin.com")  # Abre LinkedIn
    loads_cookies(driver, cookie_file_path)

    
    # ✅ Verifica se foi redirecionado para login (cookies expirados)
    if "login" in driver.current_url:
        print("🔒 Sessão expirada. Faça login para atualizar cookies...")

        # 🧠 Abre o navegador e pede login manual
        from src.cookies import save_cookies #Importar cookies do perfil desejado
        save_cookies(driver)

        print("✅ Cookies atualizados. Recomeçando a automação...")
        accept_invites()  # ⬅ Chama a si mesma novamente com cookies válidos
    
    accept_invites(driver)
    driver.quit()