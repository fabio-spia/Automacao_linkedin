import random
import time
import pyautogui #precisa ser instalado
import pyperclip
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from config import get_driver
from bot_linkedin import gerar_resposta, extrair_dado
from cookies import loads_cookies

#Constantes
COOKIE_FILE_PATH ="data/cookie_file_path.json" # Arquivo com cookies do perfil
PROMPT = "data/prompt_message.txt" # Prompt das mensagens
CSV_FILE = "data/profiles.csv"

#Função para escrever de maneira automatizada
def humanized_writing(text):
    for char in text:
        if char == " ":
            pyautogui.press("space")
        else:
            pyperclip.copy(char)
            pyautogui.hotkey("ctrl", "v")
        pyautogui.press("end")
        time.sleep(random.uniform(0.1,1))


def send_message(driver):
    WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    time.sleep(random.randint(2, 5))
    name = extrair_dado("Nome do perfil aberto")
    first_name = name.split()[0]
    regiao_chat = (0, 300, 700, 600)  # (x, y, largura, altura)

    # 🔹 Tenta encontrar o botão "Enviar mensagem" 
    try:    
        message_button = pyautogui.locateCenterOnScreen("assets/mensage.png", region=regiao_chat, confidence=0.8)
        pyautogui.click(message_button)
    except TimeoutException:
        print(f"❌ Botão 'Enviar mensagem' não encontrado para {first_name}. Pulando...")

    time.sleep(random.randint(5, 10))
    # Extraindo mensagen recebida
    mensagen = extrair_dado("Mensagem enviada por "+name)
    if mensagen != False:
        mensagem_concatenada = first_name + ": " +mensagen
        print(f"🔍 Mensagem recebida: {mensagem_concatenada}")
    else:
        # Verificar nacionalidade
        local = extrair_dado("Local no perfil de "+name) 
        if local != False:
            print(local)
        else:
            print("Local não encontrado: ")
            local = " "
        mensagem_concatenada = first_name+" "+local
    print(mensagem_concatenada)
    resposta = gerar_resposta(mensagem_concatenada, PROMPT)
    print(f"Bot: {resposta}")
    # Escreve a resposta no campo de text
    humanized_writing(resposta)
    pyautogui.hotkey("ctrl", "enter")
    time.sleep(random.randint(5, 10))
    print(f"Mensagem enviada para {first_name}!")

if __name__ == "__main__":
    driver = get_driver()   # Abre o browser
    driver.get("https://www.linkedin.com")  # Abre LinkedIn
    loads_cookies(driver, COOKIE_FILE_PATH)
    url_profile = " "
    driver.get(url_profile)
    send_message(driver)
    driver.quit()