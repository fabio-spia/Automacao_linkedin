# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

# 🔹 Caminho do perfil do Chrome (Use o seu caminho exato)
PROFILE_PATH = r"C:\Users\55839\AppData\Local\Google\Chrome\User Data"

# 🔹 Nome do perfil específico
PROFILE_NAME = "Default"  # No seu caso, é "Default"

# 🔹 Configuração do Chrome para carregar o perfil correto
chrome_options = Options()
chrome_options.add_argument(f"user-data-dir={PROFILE_PATH}")  # Caminho do User Data
chrome_options.add_argument(f"--profile-directory={PROFILE_NAME}")  # Nome do perfil
chrome_options.add_argument("--disable-blink-features=AutomationControlled")  # Evita detecção
chrome_options.add_argument("--start-maximized")  # Abre o navegador maximizado
chrome_options.add_argument("--no-first-run --no-service-autorun --password-store=basic")  # Ignora mensagens do Chrome

# 🔹 Inicializa o WebDriver corretamente
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

try:
    # 1️⃣ Acessa a página de convites do LinkedIn
    driver.get("https://www.linkedin.com/mynetwork/invitation-manager/")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    time.sleep(5)  # Aguarda o carregamento

    # 2️⃣ Loop para aceitar convites
    while True:
        accept_buttons = driver.find_elements(By.XPATH, "//button[contains(@aria-label, 'Aceitar convite')]")
        
        if not accept_buttons:
            print("✅ Todos os convites foram aceitos!")
            break
        
        for btn in accept_buttons:
            try:
                btn.click()
                time.sleep(2)  # Pequena pausa para evitar bloqueios
                print("✔ Convite aceito")
            except Exception as e:
                print(f"⚠ Erro ao aceitar convite: {e}")

        # Recarrega a página para verificar se há mais convites
        driver.refresh()
        time.sleep(5)

except Exception as e:
    print(f"🚨 Erro: {e}")

finally:
    driver.quit()  # Fecha o navegador ao final
