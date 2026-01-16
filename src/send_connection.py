# TENHA O SELENIUM E WEBDRIVER INSTALADO
import csv
import random
import time
from datetime import datetime
import pyautogui
import pyperclip
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException, ElementNotInteractableException
from config import get_driver
from send_messages import close_all_chat_windows
import json
from bot_linkedin import gerar_resposta
from conection_sheet import adicionar_registro

URL_PROFILE = "data/profiles_conections.csv" # Perfis do linkedin
ERRO = "data/erro.csv" # Perfis que nao conseguiram se conectar
NAME_PROFILE = "data/name_profile.csv" 
PROMPT_NOTA = "data/prompt_event.txt"
EVENTO = "RD Summit"
PROMPT_MESSAGE = "data/prompt_message.txt" # Prompt das mensagens"

#Função para escrever de maneira automatizada
def humanized_writing(text):
    for char in text:
        if char == " ":
            pyautogui.press("space")
        else:
            pyperclip.copy(char)
            pyautogui.hotkey("ctrl", "v")
        time.sleep(random.uniform(0.1,0.5))

# Função gerar menssagem personalizada dependendo se for conexão ou não
def generate_message(name,conexao):

    if conexao == False:
        message = EVENTO+","+name+",não é conexão"
        #resposta = gerar_resposta(message,PROMPT)
    else:
        message = EVENTO+","+name+",é conexão"
        #resposta = gerar_resposta(message,PROMPT)
    #return resposta

# Salvar dados caso ocorra erro
def save_error(search_name, erro):
    with open(ERRO, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([search_name, erro])

# Verifica se o perfil já é conexão
def is_already_connected(driver):
    try:
        driver.find_element(By.XPATH, "//span[text()='1º']")
        return True  # Já é conexão
    except NoSuchElementException:
        return False  # Não é conexão
    
# Captura o nome do perfil diretamente da página
def get_profile_name(driver):
    try:
        user_name_element = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/in/') and @aria-label]"))
        )
        user_name = user_name_element.text.strip()
        return user_name
    except TimeoutException:
        return " "  # Caso o nome não seja encontrado, retorna um valor padrão

def get_profile_title(driver):
    try:
        user_title_element = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'text-body-medium break-words')]"))
        )
        user_title = user_title_element.text.strip()
        return user_title
    except TimeoutException:
        return " "  # Caso o nome não seja encontrado, retorna um valor padrã'o
    
def send_mesage(conexao, name, driver):
    
    # 🔹 Verifica todas as janelas abertas e muda para a mais recente
    #window_handles = driver.window_handles
    #driver.switch_to.window(window_handles[-1])

    # 🔥 Scroll suave para forçar o carregamento do botão
    def scroll_smooth(driver, total=1000, step=100, delay=0.5):
        for y in range(0, total, step):
            driver.execute_script(f"window.scrollTo(0, {y});")
            time.sleep(delay)
    scroll_smooth(driver)
    time.sleep(random.randint(2,5))
    
    # 🔹 Tenta encontrar o botão "Enviar mensagem"
    try:
        message_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, 
                                        "//button[contains(@aria-label, 'Enviar mensagem') or contains(., 'Enviar mensagem')]"))
        )
    except TimeoutException:
        print(f"❌ Botão 'Enviar mensagem' não encontrado para {name}. Pulando...")
        

    # 🔹 Aguarda o botão ficar visível
    WebDriverWait(driver, 5).until(EC.visibility_of(message_button))

    # 🔹 Tenta clicar no botão normalmente
    try:
        print("🔹 Clicando no botão 'Enviar mensagem'...")
        message_button.click()
    except (ElementClickInterceptedException, ElementNotInteractableException):
        print("⚠ O botão estava bloqueado, tentando clique via JavaScript...")
        driver.execute_script("arguments[0].click();", message_button)



    # 🔹 Aguarda até que a caixa de mensagem esteja carregada
    try:
        message_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'msg-form__contenteditable')]"))
        )
    except TimeoutException:
        print(f"⚠ O chat para {name} não carregou. Recarregando a página e tentando novamente...")
        driver.refresh()
        time.sleep(random.randint(5, 10))
    
    # Escreve a resposta no campo de texto
    name = name.split()[0]
    # Extraindo mensagens recebidas 
    try:
        mensagens = [
            el.text for el in driver.find_elements(By.CSS_SELECTOR, "li.msg-s-message-list__event p.msg-s-event-listitem__body")
        ]
    except Exception as e:
        print(f"⚠ Erro ao verificar mensagens recebidas: {e}")
        
    if mensagens:
        mensagem_concatenada = name + ": " + " ".join(mensagens)
        print(f"🔍 Mensagem recebida: {mensagem_concatenada}")
    else:
        local = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//span[contains(@class, 'text-body-small inline')]"))
        )
        local = local.text           
        mensagem_concatenada = name+" "+local
            
    resposta = gerar_resposta(mensagem_concatenada, PROMPT_MESSAGE)
    humanized_writing(resposta)

    time.sleep(random.randint(5, 10))

    try:

        # 🔹 Espera até o botão "Enviar" estar presente e visível
        send_button = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, "//button[contains(@class, 'msg-form__send-button') and text()='Enviar']"))
        )

        # 🔹 Rola a tela até o botão "Enviar"
        driver.execute_script("arguments[0].scrollIntoView(true);", send_button)
        time.sleep(random.randint(2,5))

        # 🔹 Verifica se o botão está realmente interativo antes de clicar
        WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'msg-form__send-button') and text()='Enviar']"))
        )

        # 🔹 Tenta clicar normalmente
        try:
            send_button.click()
        except:
            print("⚠ Clique normal falhou, tentando JavaScript...")
            driver.execute_script("arguments[0].click();", send_button)

        print("✅ Mensagem enviada!")
    except TimeoutException:
        print("❌ Botão 'Enviar' não encontrado ou não carregou.")
    except Exception as e:
        print(f"⚠ Erro desconhecido: {e}")
    time.sleep(random.randint(3,5))

    print(f"✅ Mensagem enviada para {name}")
    
    # Salvando dados
    name = get_profile_name(driver)
    url = driver.current_url
    title = get_profile_title(driver)
    data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("data/profiles.csv", "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([data_hora, name, url, title])

    

# Envia uma solicitação de conexão com mensagem
def send_connection_request(driver, TEMA, PROMPT):    
    WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    time.sleep(random.randint(10,20))
    close_all_chat_windows()
    name = get_profile_name(driver)
    name = name.split()[0]
    conexao = False
    # Verifica se ja é conexão
    if is_already_connected(driver):
        print(f"Já é conexão: {name}, enviando mensagem...")
        conexao = True
        send_mesage(conexao, name, driver)
        return

    if conexao == False:
        message = TEMA+","+name+",não é conexão"
        resposta = gerar_resposta(message,PROMPT)
    else:
        message = TEMA+","+name+",é conexão"
        resposta = gerar_resposta(message,PROMPT)
     
    # 🔥 Scroll suave para forçar o carregamento do botão
    def scroll_smooth(driver, total=1000, step=100, delay=0.5):
        for y in range(0, total, step):
            driver.execute_script(f"window.scrollTo(0, {y});")
            time.sleep(delay)
    
    scroll_smooth(driver)
    time.sleep(random.randint(2,5))
    
   

    
    while True:
        try:
            # Tenta encontrar o botão "Conectar" diretamente
            regiao_chat = (0, 50, 1366, 718)  # (x, y, largura, altura)
            connect_button = pyautogui.locateCenterOnScreen("assets/conectar.png", region=regiao_chat, confidence=0.8)
            
            if connect_button:
                pyautogui.click(connect_button)  # Clica no botão de fechar
                time.sleep(0.5)  # Pequena pausa para garantir o fechamento
                break                
            else:
                print("botao nao encontrado")
                break
        except Exception as e:
            print(f"Botão não encontrado, clicando em: Mais")
            try:
                # Se não encontrar, clica no botão "Mais" e depois no botão "Conectar"
                more_button = pyautogui.locateCenterOnScreen("assets/mais.png", region=regiao_chat, confidence=0.8)
                if more_button:
                    pyautogui.click(more_button)
                    time.sleep(random.randint(2,5))
                    connect_button = pyautogui.locateCenterOnScreen("assets/conectar2.png", region=regiao_chat, confidence=0.8)
                    pyautogui.click(connect_button)
                    
                else:
                    print("Botão mais não encontrado")
                    break
            except Exception as e:        
                with open(ERRO, "a", newline="", encoding="utf-8") as file:
                    writer = csv.writer(file)
                    writer.writerow([name,"Erro ao conectar"])
                print(f"Não foi possível conectar com {name}, pulando...")                    
                break
            break

    try:
        time.sleep(random.randint(2,5))

        # Adicionar nota
        add_note_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//button[.//span[text()='Adicionar nota']]"))
        )
        add_note_button.click()
        time.sleep(random.randint(2,5))

        # Escrever a mensagem
        message = resposta
        message_box = driver.find_element(By.XPATH, "//textarea[contains(@id, 'custom-message')]")
        message_box.click()
        humanized_writing(message)
        time.sleep(random.randint(1,5))

        # Enviar a solicitação
        send_button = driver.find_element(By.XPATH, "//button[.//span[text()='Enviar']]")
        send_button.click()
        time.sleep(random.randint(2,5))

        print(f"Convite enviado para {name}")
    except (TimeoutException, ElementClickInterceptedException) as e:
        print(f"Erro ao enviar convite para {name}: {e}")

    # Salvando dados
    name = get_profile_name(driver)
    url = driver.current_url
    title = get_profile_title(driver)
    data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("data/profiles.csv", "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([data_hora, name, url, title])

def search_profile(name_search):
    driver.get("https://www.linkedin.com/search/results/people")
    WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    time.sleep(random.randint(5, 10))
    
    #Buscar nome
    try:
        text_field = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "input[data-testid='typeahead-input']"))
        )
    except Exception as e:
        print(e)    
    text_field.click()
    humanized_writing(name_search)
    
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'ul[role="list"] > li'))
        )
        time.sleep(random.randint(1,5))

        cards = driver.find_elements(By.CSS_SELECTOR, 'ul[role="list"] > li')

        profiles = []
        for card in cards:
            try:
                link_elem = card.find_element(By.CSS_SELECTOR, "a[href*='/in/']")
                link = link_elem.get_attribute("href")
                profiles.append((link))
            except Exception:
                continue

        if len(profiles) == 0:
            print("❌ Nenhum perfil encontrado.")
            save_error(name_search, "nenhum perfil encontrado")
            return False
        elif len(profiles) > 1:
            print("⚠ Vários perfis encontrados.")
            save_error(name_search, "mais de um perfil encontrado")
            return False
        else:
            print(f"✅ Encontrado: {name_search}")
            link_elem.click()
            return True

    except TimeoutException:
        print("⏱ Tempo excedido esperando resultados.")
        save_error(name_search, "nenhum perfil encontrado")
        return False

if __name__ == "__main__":
    adicionar_registro("data/profiles.csv","AutoConnect")
    choise = input("Digite:\n 1 para conectar por url\n2 conectar por nome/empresa\n")

    driver = get_driver()
    driver.get("https://www.linkedin.com")  # Abre LinkedIn

    # Carrega cookies do JSON
    cookie_file_path ="data/cookie_file_path.json"
    with open(cookie_file_path, "r", encoding="utf-8") as f:
        cookies = json.load(f)

    for cookie in cookies:
        if "sameSite" in cookie:
            if cookie["sameSite"] not in ["Strict", "Lax", "None"]:
                del cookie["sameSite"]
        driver.add_cookie(cookie)

    if choise == "1":
        with open(URL_PROFILE, newline='', encoding="utf-8") as csvfile:
            reader = csv.reader(csvfile)
            next(reader)  # Pula o cabeçalho
            for row in reader:
                profile_url = row[0]
                driver.get(profile_url)
                send_connection_request(driver, EVENTO, PROMPT_NOTA)
                time.sleep(random.randint(30, 120))
    
    if choise == "2":
        with open(NAME_PROFILE, newline='', encoding="utf-8") as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                profile_name = row[0]+" "+row[1]
                print(profile_name)
                search_profile = search_profile(profile_name) 
                if search_profile == False:
                    profile_name = row[0]+" "+row[2]
                    search_profile = search_profile(profile_name)
                    if search_profile == False:
                        continue
                send_connection_request(driver, EVENTO, PROMPT_NOTA)
                time.sleep(random.randint(20, 40))
    
    driver.quit()
    #Salvando dados
    adicionar_registro("data/profiles.csv","AutoConnect")
    print("Dados salvos")
        
    
