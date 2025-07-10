import json
from config import get_driver 

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

if __name__ == "__main__":
    driver = get_driver()
    save_cookies(driver)
