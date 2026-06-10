import random
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import time
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from config import get_driver
from bot_linkedin import gerar_resposta, extrair_dado, debugging
import requests
from cookies import loads_cookies

#Constantes
COOKIE_FILE_PATH ="data/cookie_file_path.json" # Arquivo com cookies do perfil
PROMPT = "data/prompt_respond.txt"
url_webhook = "https://n8n.ncdia.cloud/webhook/d73ee559-9927-49b1-a883-9778697e9291"
#Função para escrever de maneira automatizada

def get_profile(driver):
    try:
        top_card = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH, "//main//section[.//h2][1]")))
        dados_profile = top_card.find_elements(By.TAG_NAME, "p")
        dados_profile = [p.text.strip() for p in dados_profile if p.text.strip()]
        dados_profile = "\n* ".join(dados_profile)
        prompt = "Voce vai receber uma lista de dados de um perfil do linkedin, retorne o titulo e empresas"
        user_title = gerar_resposta(dados_profile,prompt)
        return user_title
    except:
        print("Erro para extrair o perfil")
        return " "  # Caso o nome não seja encontrado, retorna um valor padrã'o
    
def send_webhook(nome,url_profile,url_webhook):
    payload = {
        "nome": nome,
        "url": url_profile
    }
    try:
        response = requests.post(url_webhook, json=payload, timeout=5)
        response.raise_for_status()
        print("Webhook enviado com sucesso!")
        print(response.text)
    except requests.exceptions.RequestException as e:
        print("Erro ao enviar webhook:", e)
        debugging(e)


def humanized_writing(field, text):
    for char in text:
        try:
            if char == "&":
                time.sleep(1)
                field.send_keys(Keys.ENTER)    
            else:
                field.send_keys(char)
        except:
            pass
        time.sleep(random.uniform(0.05, 0.5))

def respond_chat(driver):
    # Abre mensagens não lidas
    driver.get("https://www.linkedin.com/messaging/thread/2-NGNiZDM2YzAtNWEyYS00YzgyLTg2NjgtOWM1MGVhMTQ2ODkzXzEwMA==/?filter=unread")  
    print("Aguardando a página carregar...")
    WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, "ul.msg-conversations-container__conversations-list")))
    print("Listando conversas...")
    conversas = driver.find_elements(By.CSS_SELECTOR,"li.msg-conversation-listitem")
    for conversa in conversas:
        conversa.click()
        print("Extraindo titulo e nome")
        time.sleep(random.randint(3, 5))
        chat = driver.find_element(By.CSS_SELECTOR,"div.msg-s-message-list.scrollable")
        ActionChains(driver).move_to_element(chat)#.click().perform()
        chat.send_keys(Keys.HOME)
        chat.send_keys(Keys.HOME)
        time.sleep(random.randint(3, 10))
        if driver.find_elements(By.XPATH,"//div[contains(@class, 'msg-spinmail-thread-presenter__top-banner')]//p[normalize-space()='Em destaque']"):
           print("Anuncio, pulando...")
           continue 
        header = driver.find_element(By.CSS_SELECTOR, "div.artdeco-entity-lockup__content")
        nome = extrair_dado("Nome da pessoa com o chat aberto")
        titulo = header.find_element(By.CSS_SELECTOR, "div.artdeco-entity-lockup__subtitle div").text.strip()
        print("Nome: "+nome)
        print("Titulo: "+titulo)
        try:
            url = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"a.msg-thread__link-to-profile")))
            url = url.get_attribute("href")
        except:
            print("URL não econtrada.")
            url = " "

        print("Extraindo mensagens com "+nome.split()[0])
        mensagens = []
        eventos = driver.find_elements(By.CLASS_NAME, "msg-s-event-listitem")
        for evento in eventos:
            try:
                texto = evento.find_element(By.CLASS_NAME,"msg-s-event-listitem__body").text.strip()
                if not texto:
                    continue
                classes = evento.get_attribute("class")
                autor = nome if "msg-s-event-listitem--other" in classes else "eu"
                mensagens.append(f"{autor}: {texto}")
            except Exception:
                # ignora eventos sem texto (reações, sistema, etc)
                pass

        mensagem_concatenada = "Titulo: "+titulo+"\nConversa: \n"+"\n ".join(mensagens)
        print(mensagem_concatenada)
        resposta = gerar_resposta(mensagem_concatenada,PROMPT)
        if resposta and resposta.strip().lower() == "null":
            print(nome.split()[0]+" não precisa de resposta.")
            continue
        else:
            if resposta[0] == "1":
                print(nome.split()[0]+" é um perfil interessante. Enviando notificação...")
                send_webhook(nome,url,url_webhook)
                resposta = resposta[1:]
            print("Escrevendo resposta...") 
            box = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'div.msg-form__contenteditable[contenteditable="true"][role="textbox"]')))
            humanized_writing(box,resposta)
            send_button = WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.msg-form__send-button[type="submit"]')))
            send_button.click()
            print("Conversa com "+nome.split()[0]+" concluida")
            
    print("Conversas respondidas com sucesso!")

if __name__ == "__main__":
    driver = get_driver() # Abre browser
    driver.get("https://www.linkedin.com")  # Abre LinkedIn
    loads_cookies(driver, COOKIE_FILE_PATH)
    print("Respondendo chats...")
    respond_chat(driver)
    driver.quit()