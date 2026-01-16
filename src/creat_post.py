import csv
from datetime import datetime
import os
import random
import time

import pyautogui
import pyperclip
from config import get_driver
import json
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bot_linkedin import gerar_resposta, gerar_imagem
from send_connection import send_connection_request
from conection_sheet import adicionar_registro, consultar_registros

PROMPT_TEMA = "data/creat_post/prompt_choose_theme.txt" # Escolher o tema
PROMPT_CONNECTION = "data/prompt_connection.txt"
PROMPT_LEGEND = "data/creat_post/prompt_legend.txt"
COOKIE_FILE_PATH ="data/cookie_file_path.json" # Arquivo com cookies do perfil
CSV_PROFILES = "data/profiles_conections.csv" #Arquivo com perfis conectados
TOPICS_POSTED = "data/creat_post/topics_posted.csv" #Arquivo com temas ja postados

#Marcar perfil linkedin
def clicar_perfil_linkedin(driver, nome, titulo):
    opcoes = WebDriverWait(driver,10).until(EC.visibility_of_all_elements_located((By.XPATH, "//*[@role='option']")))
    nome_l = nome.lower().strip()
    titulo_l = titulo.lower().strip()
    if not opcoes:
        print("Opções não encontradas")
        return False 
    for opcao in opcoes:
        txt = (opcao.text or "").lower()
        if nome_l in txt and (not titulo_l or titulo_l in txt):
            opcao.click()
            return True

    print("Nenhuma sugestão encontrada com o nome e título informados.")
    return False

#Função para escrever de maneira automatizada
def humanized_writing(text):
    for char in text:
        if char == " ":
            pyautogui.press("space")
        else:
            pyperclip.copy(char)
            pyautogui.hotkey("ctrl", "v")
        time.sleep(random.uniform(0.1,0.5))

def creat_post(driver):
    driver.get("https://www.linkedin.com/feed/")  # Abre LinkedIn
    print("Aguardando a página carregar...")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

    #Extraindo temas
    print("Extraindo temas...")
    botao_exibir_mais = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[.//span[text()='Exibir mais']]")
        )
    )
    botao_exibir_mais.click()
    
    titles_elements = driver.find_elements(
        By.CSS_SELECTOR,
        "div.news-module__headline"
    )
    titles = [el.text.strip() for el in titles_elements if el.text.strip()]
    titles = ";".join(titles)
    print(titles)
    
    #Escolhendo o tema
    tema = gerar_resposta(titles,PROMPT_TEMA,contexto=TOPICS_POSTED)
    tema = "Janeiro branco: acompanhe as conversas"
    
    if tema == "NULL":
        print("Nenhum tema de interesse em alta")
        return False
    
    else:
        print("Tema escolhido: "+tema)
        print("Gerando legenda e imagem para o post...")    
        #Gerar legenda
        legend = gerar_resposta(tema,PROMPT_LEGEND)
        
        print(legend)
        
        #Gerar imagem
        caminho_img = os.path.abspath("data/creat_post/images/post.png")
        prompt_imagem = f"Crie uma imagem tamanho 1080x1080 sobre: {tema}, e consciencia digital. Não escreva nada na imagem"
        gerar_imagem(prompt_imagem,caminho_img)
        

        for headline in titles_elements:
            if headline.text.strip() == tema:
                # Clica no título
                headline.find_element(By.XPATH, "./ancestor::a").click()
                break
        
        #Conectar com editor e extrair dados
        print("Conectar com editor e extrair dados...")
        editor = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "span.storyline-info-card__creator-link a")))
        editor.click()
        nome = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "h1.inline.t-24.v-align-middle.break-words")))
        nome = nome.text.strip()
        titulo = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.text-body-medium.break-words")))
        titulo = titulo.text.strip()
        editor = [{"Nome":nome,"Titulo":titulo}]
        data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        url = driver.current_url
        with open(CSV_PROFILES, "a", newline="", encoding="utf-8") as file:#Salvando no csv
            writer = csv.writer(file)
            writer.writerow([data_hora, nome, url, titulo, tema])
        #send_connection_request(driver,tema,PROMPT_CONNECTION)

        #Conectar com autores e extrair dados
        autores = []
        driver.back()
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        print("Conectar com autores e extrair dados...")
        for i in range(5):
            posts = driver.find_elements(By.CSS_SELECTOR, "[role='article']")
            if i >= len(posts):
                break
            post = posts[i]
            # Garante que o post esteja visível
            driver.execute_script("arguments[0].scrollIntoView();", post)
            time.sleep(1)
            # Dentro do post, pega o link do nome do autor
            autor = post.find_element(By.CSS_SELECTOR, "a[href*='/in/']")
            driver.execute_script("""
            arguments[0].scrollIntoView({block: 'center', inline: 'center'});
            """, autor)
            
            print(f"Clicando no perfil {i+1}")
            # Clica no nome
            autor.click()
            nome = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "h1.inline.t-24.v-align-middle.break-words")))
            nome = nome.text.strip()
            titulo = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.text-body-medium.break-words")))
            titulo = titulo.text.strip()
            autores.append({
                "Nome": nome,
                "Titulo": titulo})
            data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            url = driver.current_url
            with open(CSV_PROFILES, "a", newline="", encoding="utf-8") as file:#Salvando no csv
                writer = csv.writer(file)
                writer.writerow([data_hora, nome, url, titulo, tema])
            #send_connection_request(driver,tema,PROMPT_CONNECTION)
            driver.back()
            time.sleep(5)

        #Criar post
        print("Criando post...")
        driver.get("https://www.linkedin.com/feed/")
        time.sleep(5)
        #Anexando imagem
        btn = WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[aria-label="Adicionar mídia"].image_video-detour-btn')))
        driver.execute_script("arguments[0].click();", btn)
        file_input = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.ID, "media-editor-file-selector__file-input")))
        file_input.send_keys(caminho_img)
        botao_avancar = WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.XPATH, '//button[@aria-label="Avançar"]')))
        botao_avancar.click()
        time.sleep(5)
        
        #Escrevendo legenda
        humanized_writing(legend)
        pyautogui.press("enter")
        
        #Marcar perfis
        humanized_writing("@"+editor[0]['Nome'])
        clicar_perfil_linkedin(driver,editor[0]['Nome'],editor[0]['Titulo'])
        humanized_writing(" selecionou otimos posts, escritos por")
        for autor in autores:
            pyautogui.write(" ")
            humanized_writing("@"+autor['Nome'])
            clicar_perfil_linkedin(driver,autor['Nome'],autor['Titulo'])
        #Salvando tema
        with open(TOPICS_POSTED, "a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow([tema])

      



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

    creat_post(driver)
    time.sleep(200)
    driver.quit()
    print("\nSalvando perfis pedido de conexão...")
    adicionar_registro("data/profiles_conections.csv","AutoConnect")