import random
import sys
import os
import pyautogui
import pyperclip
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import csv
import json
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import get_driver
from bot_linkedin import gerar_resposta
from langdetect import detect

#constantes
COOKIE_FILE_PATH ="data/cookie_file_path.json" # Arquivo com cookies do perfil
CSV_FILE = "data/posts.csv"
PROMPT_COMMENT = "data/prompt_comment.txt"
PROMPT_POST = "data/prompt_rate_post.txt"
CONTEXTO_COMMENT = "data/dataset_comment.csv"
CONTEXTO_POST = "data/dataset_post.csv"
RECENT = "assets/recent.png" # Botão "Recentes"

#Função para escrever de maneira automatizada
def humanized_writing(text):
    for char in text:
        if char == " ":
            pyautogui.press("space")
        else:
            pyperclip.copy(char)
            pyautogui.hotkey("ctrl", "v")
        time.sleep(random.uniform(0.1,0.5))

# Função para fazer scroll e carregar mais posts
def scroll_feed(driver, num_scrolls, delay):
    for i in range(num_scrolls):
        # Scroll até o final da página
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(delay)

def cont_post(posts):
    cont = 0
    for post in posts:
        print(f"texto do post:\n{post.text[:100]}")
        if post.text[:30] != f"Número da publicação no feed {cont+1}":
            continue
        cont += 1
    return cont

def clear_posts(posts):
    index = 0
    posts_true = []
    for post in posts:
        if post.text[:29] != f"Número da publicação no feed " or post.text[:30] == posts[index-1].text[:30]:
            index += 1
            continue
        posts_true.append(post)
        index += 1
    return posts_true

def send_comment(driver, max_posts, max_comments):
    driver.get("https://www.linkedin.com/feed/")  # Abre LinkedIn
    print("Aguardando a página carregar...")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

    # Classificando por recentes
    print("Clicando em 'Classificar por'...")
    dropdown_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((
    By.XPATH, "//button[contains(., 'Classificar por:')]"
    )))
    dropdown_button.click()
    time.sleep(random.randint(2, 5))
    recent_button = pyautogui.locateCenterOnScreen(RECENT, confidence=0.8)
    pyautogui.click(recent_button)
    time.sleep(random.randint(5, 10))

    deu_certo = 0
    post_index = 0
    qtd_posts = 0

    # Carregar posts
    posts = driver.find_elements(By.XPATH, '//div[contains(@class, "feed-shared-update-v2")]')

    
    while qtd_posts < max_posts:    
        try:

            # Carregar novos posts
            if post_index >= len(posts):
                print("Carregando novos posts...")
                scroll_feed(driver, num_scrolls=1, delay=3)
                posts = driver.find_elements(By.XPATH, '//div[contains(@class, "feed-shared-update-v2")]')
        

            post = posts[post_index]

            # Verificar se realmente e um post
            if post.text[:29] != f"Número da publicação no feed " or post.text[:30] == posts[post_index-1].text[:30]:
                post_index += 1
                continue

            # Analisando post
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", post)
            print(f"Analisando post {qtd_posts+1}...")
            time.sleep(random.randint(2, 5))

            qtd_posts +=1
            post_index += 1  # Vai para o próximo post

            # Ignora posts promovidos
            if "Promovido" in post.text:
                print("--Anuncio--")
                continue
            
            # Extrai legenda do post
            try:
                legend = post.find_elements(By.XPATH, './/span[@dir="ltr"]')
            except Exception:
                print(f"⚠ Erro ao analisar o post")
                continue  
            legend = " ".join([s.text.strip() for s in legend if s.text.strip()])
            
            # Detecta idioma
            if not legend or detect(legend) != 'pt':
                print("--Não é portugues--")
                continue
            
            print("Legenda: "+legend)

            # Analisa se o post é comentavel
            analysis = gerar_resposta(legend, PROMPT_POST,contexto=CONTEXTO_POST)
            classe = analysis[0]
            reason = analysis[1:]
            print(f"Analise do bot: {reason}")

            # Comenta no post
            if classe == "1":
                # Curtir post
                button_like = post.find_element(By.XPATH, ".//button[contains(@class,'react-button__trigger')]")
                if button_like:
                    button_like.click()

                # gerando comentario
                response = gerar_resposta(legend, PROMPT_COMMENT, contexto=CONTEXTO_COMMENT)
                print("Bot: "+response)
                
                # Enviando mensagem
                button_commenter = WebDriverWait(post, 10).until(
                    EC.presence_of_element_located((By.XPATH, ".//button[contains(@class,'comment-button flex-wrap')]"))
                )
                button_commenter.click()
                time.sleep(random.randint(5,10))
                humanized_writing(response)
                button_commenter = WebDriverWait(post, 10).until(
                    EC.presence_of_element_located((By.XPATH, ".//button[contains(@class,'box__submit-button')]"))
                )
                button_commenter.click()
                time.sleep(5)
                # Salvando post
                with open(CSV_FILE, "a", newline="", encoding="utf-8") as file:
                    writer = csv.writer(file)
                    writer.writerow([legend, reason, response])
                deu_certo +=1

            if deu_certo >= max_comments:               
                break
        
            
        except Exception as e:
            print(f"⚠ Erro ao analisar post: {e}")
            post_index += 1  # Pula esse post problemático
   

if __name__ == "__main__":
    driver = get_driver() # Abre browser
    driver.get("https://www.linkedin.com")  # Abre LinkedIn

    # Carrega cookies do JSON
    with open(COOKIE_FILE_PATH, "r", encoding="utf-8") as f:
        cookies = json.load(f)

    for cookie in cookies:
        if "sameSite" in cookie:
            if cookie["sameSite"] not in ["Strict", "Lax", "None"]:
                del cookie["sameSite"]
        driver.add_cookie(cookie)
    
        # ✅ Verifica se foi redirecionado para login (cookies expirados)
    if "login" in driver.current_url:
        print("🔒 Sessão expirada. Faça login para atualizar cookies...")
        driver.quit()

        # 🧠 Abre o navegador e pede login manual
        from save_cookies import save_cookies #Importar cookies do perfil desejado 
        save_cookies()

        print("✅ Cookies atualizados. Recomeçando a automação...")
        send_comment()  # ⬅ Chama a si mesma novamente com cookies válidos

    
    print("Enviando comentario...")
    send_comment(driver,20,3)
    driver.quit()        
    