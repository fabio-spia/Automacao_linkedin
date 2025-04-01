import csv
import random
import time
import pyautogui #precisa ser instalado
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException, ElementNotInteractableException
from config import get_driver
from selenium.webdriver.common.keys import Keys

CSV_FILE = "profiles.csv"


def generate_message(name):
    """Gera uma mensagem personalizada"""
    
    mensagens = [
        f"Olá {name}, obrigado por se conectar! Será um prazer trocar ideias com você. Para conhecer mais sobre meu trabalho, acesse: fabionudge.com/",
        f"Oi {name}, é ótimo nos conectarmos aqui! Espero que possamos compartilhar bons insights. Para conhecer mais sobre meu trabalho, acesse: fabionudge.com/",
        f"Olá {name}, agradeço pela conexão! Fique à vontade para trocar experiências comigo. Para conhecer mais sobre meu trabalho, acesse: fabionudge.com/",
        f"Oi {name}, feliz por estarmos conectados! Vamos manter contato e compartilhar conhecimento. Para conhecer mais sobre meu trabalho, acesse: fabionudge.com/",
        f"Olá {name}, obrigado por se conectar! Espero que possamos colaborar e aprender juntos. Para conhecer mais sobre meu trabalho, acesse: fabionudge.com/",
        f"Oi {name}, que bom nos conectarmos! Conte comigo para boas conversas e troca de experiências. Para conhecer mais sobre meu trabalho, acesse: fabionudge.com/",
        f"Olá {name}, é uma honra estar na sua rede! Que possamos compartilhar boas oportunidades. Para conhecer mais sobre meu trabalho, acesse: fabionudge.com/",
        f"Oi {name}, agradeço a conexão! Espero que possamos interagir e crescer juntos profissionalmente. Para conhecer mais sobre meu trabalho, acesse: fabionudge.com/",
        f"Olá {name}, muito obrigado pela conexão! Será um prazer compartilhar ideias e conhecimentos. Para conhecer mais sobre meu trabalho, acesse: fabionudge.com/",
        f"Olá {name}, é uma honra me conectar com você por aqui. Para conhecer mais sobre meu trabalho, acesse: fabionudge.com/",
        f"Oi {name}, fico feliz com nossa conexão! Para conhecer mais sobre meu trabalho, acesse: fabionudge.com/"
    ]
    return random.choice(mensagens)

def close_all_chat_windows():
    """Encontra e fecha todas as janelas de conversa no LinkedIn usando PyAutoGUI."""
    while True:
        try:
            # Tenta localizar o botão "fechar" na tela
            regiao_chat = (0, 50, 1366, 718)  # (x, y, largura, altura)

            close_button = pyautogui.locateCenterOnScreen("fechar.png", region=regiao_chat, confidence=0.6)
            
            if close_button:
                pyautogui.click(close_button)  # Clica no botão de fechar
                time.sleep(0,5)  # Pequena pausa para garantir o fechamento
                print("achou botao")
                
            else:
                print("Todas as janelas foram fechadas.")
                break  # Sai do loop se não encontrar mais janelas abertas

        except Exception as e:
            print(f"Erro ao fechar janelas: {e}")
            break  # Evita loops infinitos se algo der errado

def send_messages():
    
    """Lê o CSV e envia mensagens para cada perfil"""
    driver = get_driver()
    
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
                    print("Botão encontrado")
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
                
                    
                
                # 🔹 Encontra a caixa de mensagem e escreve
                message_box.send_keys(generate_message(first_name))
                time.sleep(2)

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
