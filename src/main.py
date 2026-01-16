import random
import time
from accept_invites import accept_invites
from send_messages import send_messages
from conection_sheet import adicionar_registro
from send_connection import send_connection_request
from metrics import extract_metrics
from config import get_driver
from send_comment import send_comment
import json
import csv
from selenium.webdriver.support.ui import WebDriverWait

COOKIE_FILE_PATH ="data/cookie_file_path.json" # Arquivo com cookies do perfil


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

    print("🔄 Aceitando convites...")
    accept_invites(driver)

    print("\n📨 Enviando mensagens para os contatos aceitos...")
    send_messages(driver)
    print("\nSalvando perfis conectados...")
    adicionar_registro("data/profiles.csv","AutoAccept")

    print("\nComentando em posts...")
    send_comment(driver,30,10)
    print("Salvando posts...")
    adicionar_registro("data/posts.csv","AutoComment")

    print("\nConectando com perfis dos posts comentados...")
    PROMPT = "data/prompt_connection.txt"
    URL_PROFILE = "data/profiles_conections.csv"
    with open(URL_PROFILE, newline='', encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Pula o cabeçalho
        for row in reader:
            profile_url = row[2]
            legenda = row[4]
            driver.get(profile_url)
            send_connection_request(driver, legenda, PROMPT)
            time.sleep(random.randint(10, 30))

    print("\nSalvando perfis pedido de conexão...")
    adicionar_registro("data/profiles_conections.csv","AutoConnect")

    print("Extraindo metrics de hoje")
    extract_metrics(driver)

    driver.quit()


    
    
    

    
    