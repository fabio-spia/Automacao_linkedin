from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time

# 🔹 Caminho do perfil do Chrome (Altere para o caminho do seu perfil)
PROFILE_PATH = r"C:\Users\55839\AppData\Local\Google\Chrome\User Data\Default"

# 🔹 Configuração do Selenium com Chrome e perfil específico
chrome_options = Options()
chrome_options.add_argument(f"user-data-dir={PROFILE_PATH}")  # Usa o perfil salvo do Chrome
chrome_options.add_argument("--profile-directory=Default")  # Define o perfil específico

# 🔹 Inicializa o WebDriver
service = Service("chromedriver.exe")  # Certifique-se que o ChromeDriver está no PATH
driver = webdriver.Chrome(service=service, options=chrome_options)

try:
    # 1️⃣ Acessa a página de convites do LinkedIn
    driver.get("https://www.linkedin.com/mynetwork/invitation-manager/")
    time.sleep(5)  # Espera a página carregar

    # 2️⃣ Aceita todos os convites visíveis na tela
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
