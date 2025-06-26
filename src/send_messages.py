import csv
import time
import json
import pyautogui #precisa ser instalado
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException, ElementNotInteractableException
from config import get_driver
from selenium.webdriver.common.keys import Keys
from bot_linkedin import gerar_resposta

#Constantes
CSV_FILE = "data/profiles.csv" # Arquivo com perfis
COOKIE_FILE_PATH ="data/cookie_file_path.json" # Arquivo com cookies do perfil
CLOSE_IMAGE = "assets/fechar.png" # Print do botão de fechar 
REGIAO_CHAT = (0, 50, 1366, 718) # Região da tela para buscar chats abertos
PROMPT = "data/prompt_message.txt" # Prompt das mensagens

# Encontra e fecha todas as janelas de conversa no LinkedIn usando PyAutoGUI
def close_all_chat_windows():
    while True:
        close_button = None
        try:
            #Tenta localizar o botão "fechar" na tela
            close_button = pyautogui.locateCenterOnScreen(CLOSE_IMAGE, region=REGIAO_CHAT, confidence=0.8)
            #close_button = WebDriverWait().until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@class,'artdeco-button--tertiary ember-view')]")))

            if close_button:
                #close_button.click()
                pyautogui.click(close_button)  # Clica no botão de fechar
                time.sleep(0.5)  # Pequena pausa para garantir o fechamento
    
                
            else:
                print("Todas as janelas foram fechadas.")
                break  # Sai do loop se não encontrar mais janelas abertas

        except Exception as e:
            if close_button != None:
                print(f"Erro ao fechar janelas: {e}")
            break  # Evita loops infinitos se algo der errado

def send_messages(): 
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
        send_messages()  # ⬅ Chama a si mesma novamente com cookies válidos
        return  # Importante: evita duplicação de execução abaixo

    # Lê o CSV e envia mensagens para cada perfil
    with open(CSV_FILE, "r", encoding="utf-8") as file:
        reader = csv.reader(file)
        
        next(reader)  # Pula o cabeçalho
          
        for row in reader:
            if len(row) < 3:
                continue
            
            date, name, profile_link = row
            
            
            first_name = name.split()[0]  # Apenas o primeiro nome


            print(f"📩 Enviando mensagem para {first_name}...")

            try:
                driver.get("https://tinyurl.com/5n74kwt5") # Abre pagina de busca do linkedin
                WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                time.sleep(5)
                
                # 🔹 Verifica todas as janelas abertas e muda para a mais recente
                window_handles = driver.window_handles
                driver.switch_to.window(window_handles[-1])
                
                #Buscar nome
                
                text_field = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "search-conversations")))
                text_field.click()
                text_field.send_keys(name)
                text_field.send_keys(Keys.ENTER)
                try:
                    # Espera o UL com as conversas aparecer
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "ul.msg-conversations-container__conversations-list"))
                    )

                    # Encontra o primeiro link de conversa visível
                    convo_links = driver.find_elements(By.CSS_SELECTOR, "div.msg-conversation-listitem__link")
                    
                    for link in convo_links:
                        if link.is_displayed():
                            WebDriverWait(driver, 10).until(EC.element_to_be_clickable(link))
                            link.click() # Clicando no chat especifico
                            time.sleep(2)
                            clicou = True                            
                            break
                    if len(convo_links)==0:
                        clicou = False
                    if clicou:
                        message_box = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'msg-form__contenteditable')]"))
                        )
                        try:
                            # Extraindo mensagens recebidas 
                            mensagens = [
                                el.text for el in driver.find_elements(By.CSS_SELECTOR, "li.msg-s-message-list__event p.msg-s-event-listitem__body")
                            ]
                            mensagem_concatenada = first_name + ": " + " ".join(mensagens)
                            print(f"🔍 Mensagem recebida: {mensagem_concatenada}")
                            resposta = gerar_resposta(mensagem_concatenada, PROMPT) # Gerando resposta
                            print(f"🤖 Resposta gerada: {resposta}")
                            time.sleep(10)

                        except Exception as e:
                            print(f"⚠ Erro ao verificar mensagens recebidas: {e}")

                        

                    else:
                        # Mandando mensagem diretamente no perfil
                        print("Nenhuma conversa visível e clicável foi encontrada.")
                        resposta = gerar_resposta(first_name, PROMPT)
                        driver.get(profile_link)
                        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                        time.sleep(2)

                        # 🔹 Verifica todas as janelas abertas e muda para a mais recente
                        window_handles = driver.window_handles
                        driver.switch_to.window(window_handles[-1])
                    
                        time.sleep(10)
                        close_all_chat_windows()
                        
                        # 🔥 Scroll suave para forçar o carregamento do botão
                        def scroll_smooth(driver, total=1000, step=100, delay=0.5):
                            for y in range(0, total, step):
                                driver.execute_script(f"window.scrollTo(0, {y});")
                                time.sleep(delay)
                        scroll_smooth(driver)
                        time.sleep(2)
                        

                    # 🔹 Tenta encontrar o botão "Enviar mensagem"
                        try:
                            message_button = WebDriverWait(driver, 20).until(
                                EC.element_to_be_clickable((By.XPATH, 
                                                            "//button[contains(@aria-label, 'Enviar mensagem') or contains(., 'Enviar mensagem')]"))
                            )
                        except TimeoutException:
                            print(f"❌ Botão 'Enviar mensagem' não encontrado para {first_name}. Pulando...")
                            continue  # Pula para o próximo contato

                        # 🔹 Aguarda o botão ficar visível
                        WebDriverWait(driver, 5).until(EC.visibility_of(message_button))

                        # 🔹 Tenta clicar no botão normalmente
                        try:
                            print("🔹 Tentando clicar no botão 'Enviar mensagem'...")
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
                            print(f"⚠ O chat para {first_name} não carregou. Recarregando a página e tentando novamente...")
                            driver.refresh()
                            time.sleep(5)
                            continue  # Pula para o próximo contato
                except Exception as e:
                    print(f"Ocorreu um erro: {e}")
                
                # Escreve a resposta no campo de texto
                message_box.send_keys(resposta)

                time.sleep(5)

                try:

                    # 🔹 Espera até o botão "Enviar" estar presente e visível
                    send_button = WebDriverWait(driver, 10).until(
                        EC.visibility_of_element_located((By.XPATH, "//button[contains(@class, 'msg-form__send-button') and text()='Enviar']"))
                    )

                    # 🔹 Rola a tela até o botão "Enviar"
                    driver.execute_script("arguments[0].scrollIntoView(true);", send_button)
                    time.sleep(2)

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
                time.sleep(3)

                print(f"✅ Mensagem enviada para {first_name}")

            except Exception as e:
                print(f"⚠ Erro ao enviar mensagem para {first_name}: {e}")

    driver.quit()

if __name__ == "__main__":
    send_messages()
