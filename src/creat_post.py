import csv
from datetime import datetime
import os
import random
import time
from config import get_driver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.keys import Keys
from bot_linkedin import gerar_resposta, gerar_imagem
from send_connection import send_connection_request
import re
from cookies import loads_cookies

PROMPT_TEMA = "data/creat_post/prompt_choose_theme.txt" # Escolher o tema
PROMPT_CONNECTION = "data/prompt_connection.txt"
PROMPT_LEGEND = "data/creat_post/prompt_legend.txt"
COOKIE_FILE_PATH ="data/cookie_file_path.json" # Arquivo com cookies do perfil
CSV_PROFILES = "data/profiles_conections.csv" #Arquivo com perfis conectados
TOPICS_POSTED = "data/creat_post/topics_posted.csv" #Arquivo com temas ja postados
CAMINHO_IMG = os.path.abspath("data/creat_post/images/post.png")
    
def norm(s: str) -> str:
    s = (s or "").lower()
    s = s.replace("\u00a0", " ")     # nbsp
    s = re.sub(r"\s+", " ", s).strip()  # colapsa espaços, tabs e quebras de linha
    return s

#Marcar perfil linkedin
def clicar_perfil_linkedin(driver, nome, titulo):
    nome_l = norm(nome)
    titulo_l = norm(titulo)
    for _ in range(5):
        try:
            # Espera a lista de sugestoes existir e estar visivel
            opcoes = WebDriverWait(driver, 10).until(
                EC.visibility_of_all_elements_located((By.XPATH, "//*[@role='option']"))
            )

            for opcao in opcoes:
                txt = ((opcao.text or "")).lower()
                bate_nome = nome_l and (nome_l in txt)

                if titulo_l != "":
                    bate_titulo = (not titulo_l) or (titulo_l in txt)
                    if bate_nome and bate_titulo:
                        # Click via JS costuma ser mais estavel no LinkedIn
                        driver.execute_script("arguments[0].click();", opcao)
                        return True
                elif bate_nome:
                    # Click via JS costuma ser mais estavel no LinkedIn
                    driver.execute_script("arguments[0].click();", opcao)
                    return True

            # Se nao achou ainda, as vezes a lista atualiza logo depois
            time.sleep(0.2)

        except StaleElementReferenceException:
            # DOM mudou, tenta de novo
            time.sleep(0.2)
            continue
        except TimeoutException:
            # Lista nao apareceu a tempo nessa tentativa
            time.sleep(0.2)
            continue

    print("Nenhuma sugestao encontrada com o nome e titulo informados.")
    return False
#Função para escrever de maneira automatizada

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
    
    #if tema != "NULL":
    print("Tema escolhido: "+tema)
    for headline in titles_elements:
        if headline.text.strip() == tema:
            # Clica no título
            headline.find_element(By.XPATH, "./ancestor::a").click()
            break
    time.sleep(random.uniform(5,10))
    #Conectar com editor e extrair dados
    print("Conectar com editor e extrair dados...")
    editor = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "span.storyline-info-card__creator-link a")))
    editor.click()
    nome = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//main//h2[normalize-space()]")))
    nome = nome.text.strip()
    try:
        titulo = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//main//p[contains(., '|')][1]")))
        titulo = titulo.text.strip()
    except:
        print("Erro para extrair o titulo")
        titulo = ""
    print("Nome editor: "+nome)
    print("Titulo editor: "+titulo)
    editor = [{"Nome":nome,"Titulo":titulo}]
    conexao = driver.find_elements(By.XPATH,"//span[contains(@class,'dist-value') and normalize-space()='1º']")
    pendente = driver.find_elements(By.XPATH, "//button[contains(@aria-label, 'Pendente')]")
    if not conexao and not pendente:
        print("Conectando com "+nome)
        data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        url = driver.current_url
        with open(CSV_PROFILES, "a", newline="", encoding="utf-8") as file:#Salvando no csv
            writer = csv.writer(file)
            writer.writerow([data_hora, nome, url, titulo, tema])
        send_connection_request(driver,tema,PROMPT_CONNECTION)  

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
        autores_in = post.find_elements(By.CSS_SELECTOR, "a[href*='/in/']")
        if not autores_in:
            print(f"Post {i+1}: sem autor pessoa (/in). Pulando.")
            continue
        autor = autores_in[0]
        driver.execute_script("""
        arguments[0].scrollIntoView({block: 'center', inline: 'center'});
        """, autor)
        nome = post.find_element(By.CSS_SELECTOR, ".update-components-actor__title span[aria-hidden='true']").text.strip()
        titulo = post.find_element(By.CSS_SELECTOR,".update-components-actor__description span[aria-hidden='true']").text.strip()
        print("Nome autor: "+nome)
        print("Titulo autor: "+titulo)
        print(f"Clicando no perfil {i+1}")
        # Clica no nome
        autor.click()
        autores.append({
            "Nome": nome,
            "Titulo": titulo})
        conexao = driver.find_elements(By.XPATH,"//span[contains(@class,'dist-value') and normalize-space()='1º']")
        if not conexao:
            print("Conectando com "+nome)
            data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            url = driver.current_url
            with open(CSV_PROFILES, "a", newline="", encoding="utf-8") as file:#Salvando no csv
                writer = csv.writer(file)
                writer.writerow([data_hora, nome, url, titulo, tema])
            send_connection_request(driver,tema,PROMPT_CONNECTION)     
        driver.back()
        time.sleep(random.uniform(5,10))

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
    print("Anexando imagem...")
    #Anexando imagem
    btn = WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[aria-label="Adicionar mídia"].image_video-detour-btn')))
    driver.execute_script("arguments[0].click();", btn)
    file_input = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.ID, "media-editor-file-selector__file-input")))
    file_input.send_keys(CAMINHO_IMG)
    botao_avancar = WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.XPATH, '//button[@aria-label="Avançar"]')))
    botao_avancar.click()
    time.sleep(random.uniform(5,10))
    
    legend_box  = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH,"//div[contains(@class,'ql-editor') and @contenteditable='true']")))
    print("Marcando pessoas...")
    #Marcar perfis
    print(editor[0]["Titulo"])
    humanized_writing(legend_box,"@"+editor[0]['Nome'])
    clicar_perfil_linkedin(driver,editor[0]['Nome'],editor[0]['Titulo'])
    humanized_writing(legend_box," selecionou otimos posts, escritos por")
    for autor in autores:
        legend_box.send_keys(" ")
        humanized_writing(legend_box," @"+autor['Nome'])
        clicar_perfil_linkedin(driver,autor['Nome'],autor['Titulo'])

    print("Escrevendo legenda...")
    #Escrevendo legenda   
    legend_box.send_keys(Keys.CONTROL, Keys.HOME)
    legend_box.send_keys(Keys.ENTER, Keys.ENTER)
    legend_box.send_keys(Keys.CONTROL, Keys.HOME)
    humanized_writing(legend_box,legend)
        
            
    time.sleep(random.uniform(5,10))
    # Clicar em publicar
    btn_publicar = WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.XPATH, "//button[.//span[normalize-space()='Publicar']]")))
    driver.execute_script("arguments[0].click();", btn_publicar)
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
    time.sleep(30)
    driver.quit()
