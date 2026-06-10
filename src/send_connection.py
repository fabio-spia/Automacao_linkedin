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
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from config import get_driver
from bot_linkedin import gerar_resposta, extrair_dado, debugging
from conection_sheet import adicionar_registro
from cookies import loads_cookies

URL_PROFILE = "data/profiles_conections.csv" # Perfis do linkedin
ERRO = "data/erro.csv" # Perfis que nao conseguiram se conectar
NAME_PROFILE = "data/name_profile.csv" 
PROMPT_NOTA = "data/prompt_event.txt"
EVENTO = "Agile Trends"
PROMPT_MESSAGE = "data/prompt_message.txt" # Prompt das mensagens"
cookie_file_path ="data/cookie_file_path.json"

#Salvar errro
def save_error(name):
    with open(ERRO, "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([name,"Erro ao conectar"])

#Função para escrever de maneira automatizada
def humanized_writing(text):
    for char in text:
        if char == " ":
            pyautogui.press("space")
        else:
            pyperclip.copy(char)
            pyautogui.hotkey("ctrl", "v")
        time.sleep(random.uniform(0.1,0.5))



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
            EC.presence_of_element_located((By.XPATH, "//main//h2[normalize-space()]"))
        )
        user_name = user_name_element.text.strip()
        print(user_name)
        return user_name
    except TimeoutException:
        print("Erro para extrair o nome")
        return " "  # Caso o nome não seja encontrado, retorna um valor padrão

def get_profile_title(driver):
    try:
        top_card = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH, "//main//section[.//h2][1]")))
        dados_profile = top_card.find_elements(By.TAG_NAME, "p")
        dados_profile = [p.text.strip() for p in dados_profile if p.text.strip()]
        dados_profile = "\n* ".join(dados_profile)
        user_title = extrair_dado("Titulo do perfil aberto")
        print(user_title)
        return user_title
    except TimeoutException:
        print("Erro para extrair o titulo")
        return " "  # Caso o nome não seja encontrado, retorna um valor padrã'o

def send_message(driver, message):
    regiao_chat = (0, 300, 700, 600)  # (x, y, largura, altura)
    # 🔹 Tenta encontrar o botão "Enviar mensagem" 
    try:    
        message_button = pyautogui.locateCenterOnScreen("assets/mensage.png", region=regiao_chat, confidence=0.8)
        pyautogui.click(message_button)
    except Exception as e:
        print(f"❌ Botão 'Enviar mensagem' não encontrado. Pulando...")
        debugging(str(e))
        return False
    time.sleep(random.randint(5, 10))
    try:
        field = pyautogui.locateCenterOnScreen("assets/campo_msg.png", region=regiao_chat, confidence=0.6)
        pyautogui.click(field)
    except Exception as e:
        print(f"❌ Campo de mensagem não encontrado. Pulando...")
        debugging(str(e))
        return False

    print(f"Bot: {message}")
    # Escreve a resposta no campo de text
    humanized_writing(message)
    pyautogui.hotkey("ctrl", "enter")
    time.sleep(random.randint(5, 10))
    print(f"Mensagem enviada!")


# Envia uma solicitação de conexão com mensagem
def send_connection_request(driver, TEMA, PROMPT):    
    WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    time.sleep(random.randint(10,20))
    name = extrair_dado("Nome do perfil aberto")
    if name == False:
        return False
    # Verifica se ja é conexão
    if is_already_connected(driver):
        print(f"Já é conexão: {name}, enviando mensagem...")
        message = TEMA+","+name+",é conexão"
        resposta = gerar_resposta(message,PROMPT)
        if send_message(driver, resposta) == False:
            return False
        return

    message = TEMA+","+name+",não é conexão"
    resposta = gerar_resposta(message,PROMPT)
     
    time.sleep(random.randint(2,5))
    
   

    
    while True:
        try:
            # Tenta encontrar o botão "Conectar" diretamente
            regiao_chat = (0, 300, 700, 600)  # (x, y, largura, altura)
            connect_button = pyautogui.locateCenterOnScreen("assets/conectar.png", region=regiao_chat, confidence=0.8)
            
            
            if connect_button:
                pyautogui.click(connect_button)  
                time.sleep(0.5)  
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
        
                    dropdown = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".artdeco-dropdown__content--is-open")))
                    btn_conectar = dropdown.find_element(By.XPATH,".//div[@role='button' and contains(@aria-label,'para se conectar')]")
                    driver.execute_script("arguments[0].click();", btn_conectar)
                else:
                    print("Botão mais não encontrado")
                    return False
            except Exception as e:        
                print(f"Não foi possível conectar com {name}, pulando...")
                debugging(str(e))                    
                return False
            break

    try:
        time.sleep(random.randint(2,5))
        pyautogui.click(718, 252)
        regiao_chat = (100, 50, 1000, 400)
        # Adicionar nota
        time.sleep(random.randint(2,5))
        add_note_button = pyautogui.locateCenterOnScreen("assets/add_nota.png", region=regiao_chat, confidence=0.8)
        pyautogui.click(add_note_button)
         
        time.sleep(random.randint(1,5))
        # Escrever a mensagem
        message = resposta
        humanized_writing(message)
        time.sleep(random.randint(1,5))
        
        # Enviar a solicitação
        send_button = pyautogui.locateCenterOnScreen("assets/enviar.png", region=regiao_chat, confidence=0.8)
        pyautogui.click(send_button)
        time.sleep(random.randint(2,5))

        print(f"Convite enviado para {name}")
    except (TimeoutException, ElementClickInterceptedException) as e:
        print(f"Erro ao enviar convite para {name}: {e}")
        debugging(str(e))
        return False

    
    time.sleep(random.randint(2,5))
    # Salvando dados
    url = driver.current_url
    title = get_profile_title(driver)
    data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    row = [data_hora, name, url, title,TEMA]
    adicionar_registro(row,"AutoConnect")

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
        debugging(e)    
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
    choise = input("Digite:\n 1 para conectar por url\n2 conectar por nome/empresa\n")

    driver = get_driver()
    driver.get("https://www.linkedin.com")  # Abre LinkedIn
    loads_cookies(driver, cookie_file_path)
    if choise == "1":
        with open(URL_PROFILE, newline='', encoding="utf-8-sig") as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                profile_url = row[0]
                print(profile_url)
                driver.get(profile_url)
                if send_connection_request(driver, EVENTO, PROMPT_NOTA)== False:
                    save_error(profile_url)
                #time.sleep(random.randint(15, 90))
    
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

        
    
