import csv
from datetime import datetime
import os
import random
import time
import pyautogui
import pyperclip
from config import get_driver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from bot_linkedin import gerar_resposta, gerar_imagem, debugging, extrair_dado
from send_connection import send_connection_request
import re
from cookies import loads_cookies

PROMPT_TEMA = "data/creat_post/prompt_choose_theme.txt" # Escolher o tema
PROMPT_CONNECTION = "data/prompt_connection.txt"
PROMPT_LEGEND = "data/creat_post/prompt_legend.txt"
COOKIE_FILE_PATH ="data/cookie_file_path.json" # Arquivo com cookies do perfil
TOPICS_POSTED = "data/creat_post/topics_posted.csv" #Arquivo com temas ja postados
CAMINHO_IMG = os.path.abspath("data/creat_post/images/post.png")
    
def norm(s: str) -> str:
    s = (s or "").lower()
    s = s.replace("\u00a0", " ")     # nbsp
    s = re.sub(r"\s+", " ", s).strip()  # colapsa espaços, tabs e quebras de linha
    return s


#Marcar perfil linkedin
def clicar_perfil_linkedin(nome, titulo):
    posicao = extrair_dado("Nas opçoes de perfil, quero o numero da posição(1, 2, 3...) exata de "+nome+", que tem o titulo: "+titulo)
    if posicao == False:
        print("Nenhuma sugestao encontrada para "+nome)
        return False
    print("Posição de "+nome+": "+posicao)
    for _ in range(int(posicao)):
        pyautogui.press("down")
        time.sleep(0.1)
    pyautogui.press("enter")

    
#Função para escrever de maneira automatizada

def humanized_writing(text):
    especiais = set("áàãâéêíóôõúüçÁÀÃÂÉÊÍÓÔÕÚÜÇ@")

    for char in text:

        if char == "&":
            time.sleep(1)
            pyautogui.press("enter")

        elif char in especiais:
            pyperclip.copy(char)
            pyautogui.hotkey("ctrl", "v")

        else:
            pyautogui.write(char)

        time.sleep(random.uniform(0.05, 0.5))

def creat_post(driver):
    driver.get("https://www.linkedin.com/feed/")  # Abre LinkedIn
    print("Aguardando a página carregar...")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    
    #Extraindo temas
    time.sleep(5)
    print("Extraindo temas...")
    botao_exibir_mais = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[.//span[text()='Exibir mais notícias']]")
        )
    )
    botao_exibir_mais.click()
    
    titles_elements = driver.find_elements(By.CSS_SELECTOR, "a[href*='/news/story/']")
    titles = []
    for element in titles_elements:
        title = element.find_element(By.XPATH, ".//p[not(contains(text(),'Há'))]").text
        titles.append(title)
    # Não repetir temas
    itens_csv = set()
    with open(TOPICS_POSTED, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            itens_csv.add(row["tema"].strip())
    titles = [t for t in titles if t not in itens_csv]
    titles = ";".join(titles)
    print(titles)
    
    #Escolhendo o tema
    tema = gerar_resposta(titles,PROMPT_TEMA)
    
    
    if tema == "NULL" or "Null":
        tentativas = 1
        while tentativas<5 and tema == "NULL":
            print("Nenhum tema de interesse em alta, analisando novamente...")
            tema = gerar_resposta(titles,PROMPT_TEMA)
            tentativas = tentativas+1 
        if tema == "NULL":
            print("Nenhum tema de interesse em alta, encerrando...")
            return False
    
    print("Tema escolhido: "+tema)
    for headline in titles_elements:
        compara = headline.find_element(By.XPATH, ".//p[not(contains(text(),'Há'))]").text
        if compara == tema:
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", headline)
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable(headline))
            headline.click()
            break

    #driver.get("https://www.linkedin.com/news/story/pessoas-falam-menos-e-especialistas-alertam-para-riscos-9382434/")
    time.sleep(random.uniform(5,10))
    #Conectar com editor e extrair dados
    print("Conectar com editor e extrair dados...")
    try:
        editor = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "span.storyline-info-card__creator-link a")))
        editor.click()
        time.sleep(random.uniform(5,10))
        nome = extrair_dado("Nome do perfil do linkedin")
        if nome == False:
            print("Nome do editor não encontrado")
            return
        titulo = extrair_dado("Titulo do perfil de "+nome)
        if titulo == False:
            titulo = ""
        print("Nome editor: "+nome)
        print("Titulo editor: "+titulo)
        editor = [{"Nome":nome,"Titulo":titulo}]
        conexao = driver.find_elements(By.XPATH,"//span[contains(@class,'dist-value') and normalize-space()='1º']")
        pendente = driver.find_elements(By.XPATH, "//button[contains(@aria-label, 'Pendente')]")
        if not conexao and not pendente:
            print("Conectando com "+nome)
            send_connection_request(driver,tema,PROMPT_CONNECTION)   

        #Conectar com autores e extrair dados
        autores = []
        driver.back()
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        print("Conectar com autores e extrair dados...")
        for i in range(3):
            posts = driver.find_elements(By.CSS_SELECTOR, "[role='article']")
            if i >= len(posts):
                break
            post = posts[i]
            # Garante que o post esteja visível
            driver.execute_script("arguments[0].scrollIntoView();", post)
            time.sleep(1)
            # Dentro do post, pega o link do nome do autor
            autores_in = post.find_elements(By.CSS_SELECTOR, "a[href*='/in/']")
            if not autores_in:
                print(f"Post {i+1}: sem autor pessoa (/in). Pulando.")
                continue
            autor = autores_in[0]
            driver.execute_script("""
            arguments[0].scrollIntoView({block: 'center', inline: 'center'});
            """, autor)
            time.sleep(random.uniform(5,10))
            print(f"Clicando no perfil {i+1}")
            # Clica no nome
            autor.click()
            nome = extrair_dado("Nome do perfil do linkedin")
            if nome == False:
                print("Nome do autor não encontrado")
                continue
            titulo = extrair_dado("Titulo do perfil de "+nome)
            if titulo == False:
                titulo = ""
            print("Nome autor: "+nome)
            print("Titulo autor: "+titulo)
            autores.append({
                "Nome": nome,
                "Titulo": titulo})
            conexao = driver.find_elements(By.XPATH,"//span[contains(@class,'dist-value') and normalize-space()='1º']")
            if not conexao:
                print("Conectando com "+nome)
                send_connection_request(driver,tema,PROMPT_CONNECTION)     
            driver.back()
            time.sleep(random.uniform(5,10))
            perfis = True
    except:
        print("Erro ao extrair perfis")
        perfis = False
    print("Gerando legenda e imagem para o post...")    
    #Gerar legenda
    legend = gerar_resposta(tema,PROMPT_LEGEND)
    
    print(legend)
    
    #Gerar imagem
    PROMPT_IMAGE = f"Crie uma imagem tamanho 1080x1080 para feed do linkedin, sobre: {tema}, e consciencia digital. Não escreva nada. A imagem deve ser chamativa e impactante, para atrair o usuario a ler a legenda."
    gerar_imagem(PROMPT_IMAGE,CAMINHO_IMG)
    
    #Criar post
    print("Criando post...")
    driver.get("https://www.linkedin.com/feed/")
    time.sleep(random.uniform(5,10))
    
    btn = WebDriverWait(driver,30).until(EC.element_to_be_clickable((By.XPATH, "//div[@role='button'][.//p[contains(normalize-space(), 'Começar publicação')]]")))
    btn.click()
    time.sleep(60)
    if perfis == True:
        print("Marcando pessoas...")
        #Marcar perfis
        humanized_writing("@"+editor[0]['Nome'])
        clicar_perfil_linkedin(editor[0]['Nome'],editor[0]['Titulo'])
        humanized_writing(" selecionou otimos posts, escritos por")
        for autor in autores:
            pyautogui.write(" ")
            humanized_writing(" @"+autor['Nome'])
            clicar_perfil_linkedin(autor['Nome'],autor['Titulo'])

    print("Escrevendo legenda...")
    #Escrevendo legenda   
    pyautogui.hotkey("ctrl", "home")
    pyautogui.press("enter", presses=2)
    pyautogui.hotkey("ctrl", "home")
    humanized_writing(legend)
    time.sleep(random.uniform(5,10))

    print("Anexando imagem...")
    #Anexando imagem
    anx_img = pyautogui.locateCenterOnScreen("assets/image.png", confidence=0.8)
    pyautogui.click(anx_img)
    time.sleep(5)
    pyautogui.write(CAMINHO_IMG, interval=0.01)
    pyautogui.press("enter")
    time.sleep(5)
    btn_avancar = pyautogui.locateCenterOnScreen("assets/avancar.png",region=(1150, 420, 140, 80), confidence=0.5)
    pyautogui.click(btn_avancar)
    time.sleep(random.uniform(5,10))

    # Clicar em publicar
    btn_publicar = pyautogui.locateCenterOnScreen("assets/publicar.png", confidence=0.8)
    pyautogui.click(btn_publicar)
    time.sleep(30)
    print("Publicado!")
    
    #Salvando tema
    with open(TOPICS_POSTED, "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([tema])

      



if __name__ == "__main__":
    driver = get_driver()   # Abre o browser
    driver.get("https://www.linkedin.com")  # Abre LinkedIn
    loads_cookies(driver, COOKIE_FILE_PATH)
    creat_post(driver)
    driver.quit()
