from accept_invites import accept_invites
from send_messages import send_messages
from conection_sheet import adicionar_registro
from config import get_driver
from send_comment import send_comment
import json

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
   
    print("\nComentando em posts recentes...")
    send_comment(driver,20,3)

    driver.quit()

    print("\n Salvando no google sheets...")
    print("\nSalvando perfis...")
    adicionar_registro("data/profiles.csv","AutoAccept")
    print("Salvando posts...")
    adicionar_registro("data/posts.csv","AutoComment")

    
    