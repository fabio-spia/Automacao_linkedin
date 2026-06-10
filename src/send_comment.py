from datetime import datetime
import random
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import get_driver
from bot_linkedin import gerar_resposta, debugging
from langdetect import detect
from send_connection import send_connection_request
from conection_sheet import adicionar_registro
from cookies import loads_cookies

#constantes
COOKIE_FILE_PATH ="data/cookie_file_path.json" # Arquivo com cookies do perfil
CSV_POSTS = "data/posts.csv"
CSV_PROFILES = "data/profiles_conections.csv"
PROMPT_COMMENT = "data/prompt_comment.txt"
PROMPT_POST = "data/prompt_rate_post.txt"
PROMPT_CONNECTION = "data/prompt_connection.txt"
CONTEXTO_COMMENT = "data/dataset_comment.csv"
CONTEXTO_POST = "data/dataset_post.csv"

#Função para escrever de maneira automatizada
def humanized_writing(field, text):
    for char in text:
        field.send_keys(char)
        time.sleep(random.uniform(0.05, 0.25))


# Função para fazer scroll e carregar mais posts
def scroll_feed(driver, num_scrolls, delay):
    for i in range(num_scrolls):
        # Scroll até o final da página
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(delay)

def send_comment(driver, max_posts, max_comments):
    driver.get("https://www.linkedin.com/feed/")  # Abre LinkedIn
    print("Aguardando a página carregar...")
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

    deu_certo = 0
    post_index = 0
    qtd_posts = 0
    posts_analisados = []
    # Carregar posts
    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, '//div[@data-testid="mainFeed"]//div[@role="listitem"]')))
    posts = driver.find_elements(By.XPATH, '//div[@data-testid="mainFeed"]//div[@role="listitem"]')
    
    while qtd_posts < max_posts:    
        try:

            # Carregar novos posts
            if post_index >= len(posts):
                print("Carregando novos posts...")
                scroll_feed(driver, num_scrolls=1, delay=3)
                posts = driver.find_elements(By.XPATH, '//div[@data-testid="mainFeed"]//div[@role="listitem"]')

            post = posts[post_index]
            #Verificar se o post ja foi analisado
            if post.text[:100] in posts_analisados:
                print("Post ja analisado")
                post_index += 1
                continue
            posts_analisados.append(post.text[:100])
            # Analisando post
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", post)
            print(f"Analisando post {qtd_posts+1}...")
            time.sleep(random.randint(2, 5))

            qtd_posts +=1
            post_index += 1  # Vai para o próximo post

            #Analisa se o post a foi comentado
            button_like = post.find_element(By.XPATH, ".//button[contains(@aria-label, 'reação')]")
            if "gostei" in button_like.get_attribute("aria-label").lower():
                print("Post ja comentado")
                continue
            
            # Ignora posts promovidos
            if "Promovido" in post.text:
                print("--Anuncio--")
                continue
            
            # Extrai legenda do post
            try:    
                legend_el = post.find_element(
                    By.XPATH,
                    './/*[@data-testid="expandable-text-box"]'
                )
                legend = legend_el.text.strip()
            except Exception as e:
                print(f"⚠ Erro ao extrair legenda {e}")
                debugging(str(e))
                continue
            
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
                button_like.click()

                # gerando comentario
                response = gerar_resposta(legend, PROMPT_COMMENT, contexto=CONTEXTO_COMMENT)
                if response in legend: #Evita repetir comentarios
                    print("Comentario repetido, gerando outro...")
                    legend = legend.replace(response," ")
                    response = gerar_resposta(legend, PROMPT_COMMENT, contexto=CONTEXTO_COMMENT)
                print("Bot: "+response)
                
                # Enviando mensagem
                button_commenter = WebDriverWait(post, 10).until(
                    EC.presence_of_element_located((By.XPATH, ".//button[.//span[contains(text(),'Comentar')]]"))
                )
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button_commenter)
                driver.execute_script("arguments[0].click();", button_commenter)
                time.sleep(random.randint(5,10))
                comment_box = WebDriverWait(post, 10).until(EC.element_to_be_clickable((By.XPATH,".//div[@contenteditable='true' and @role='textbox']")))
                humanized_writing(comment_box, response)
                button_commenter = WebDriverWait(post, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "( .//button[.//span[normalize-space()='Comentar']] )[last()]"))
                )
                driver.execute_script("arguments[0].click();", button_commenter)
                time.sleep(5)

                #Salvando perfil
                perfil = post.find_element(By.XPATH, "(.//a[contains(@href,'/in/') and .//p])[1]")                
                texto_perfil = (perfil.find_element(By.XPATH,".//*[@aria-label]").get_attribute("aria-label") or "").strip()
                url = perfil.get_attribute("href")
                nome = perfil.find_element(By.XPATH, ".//p[1]").text.strip()
                
                if "1º" in texto_perfil:
                    print("Ja é conexão")
                else:
                    print("Conectando com "+nome)
                    aba_original = driver.current_window_handle
                    driver.execute_script("window.open(arguments[0], '_blank');", url)
                    driver.switch_to.window(driver.window_handles[-1])
                    try:
                        send_connection_request(driver,legend,PROMPT_CONNECTION)
                    except Exception as e:
                        print(f"Erro ao processar {nome} ({url}): {e}")
                        debugging(e)
                    finally:
                        # fecha a aba atual (a nova), se ainda existir
                        if driver.current_window_handle != aba_original:
                            driver.close()
                        driver.switch_to.window(aba_original)
                # Salvando post
                print("Salvando post...")
                row = [legend, reason, response]
                adicionar_registro(row,"AutoComment")
                
                
                deu_certo +=1

            if deu_certo >= max_comments:               
                break
        
            
        except Exception as e:
            print(f"⚠ Erro: {e}")
            debugging(str(e))
            post_index += 1  # Pula esse post problemático
    return

if __name__ == "__main__":
    driver = get_driver() # Abre browser
    driver.get("https://www.linkedin.com")  # Abre LinkedIn
    loads_cookies(driver, COOKIE_FILE_PATH)
    print("Enviando comentario...")
    send_comment(driver,15,3)
    driver.quit()        
    