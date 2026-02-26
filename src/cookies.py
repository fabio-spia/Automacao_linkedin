import json
from config import get_driver 
from selenium.webdriver.support.ui import WebDriverWait

COOKIE_FILE = "data/cookie_file_path.json"

def save_cookies(driver):
    
    driver.get("https://www.linkedin.com/")

    print("🔐 Faça o login manualmente no LinkedIn.")
    input("✅ Pressione Enter aqui quando o login estiver concluído...")

    # Salvar os cookies da sessão
    cookies = driver.get_cookies()
    with open(COOKIE_FILE, "w", encoding="utf-8") as f:
        json.dump(cookies, f, indent=2)

    print(f"💾 Cookies salvos com sucesso em '{COOKIE_FILE}'")
    driver.quit()

def loads_cookies(driver,arquivo):
    # Carrega cookies do JSON
    with open(arquivo, "r", encoding="utf-8") as f:
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
        save_cookies()

        print("✅ Cookies atualizados. Execute novamente")

if __name__ == "__main__":
    driver = get_driver()
    save_cookies(driver)
