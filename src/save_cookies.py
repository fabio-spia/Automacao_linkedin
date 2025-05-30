import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import chromedriver_autoinstaller

# Instala automaticamente o driver compatível com seu Chrome
chromedriver_autoinstaller.install()

COOKIE_FILE = "data/cookie_file_path.json"

def save_cookies():
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    driver = webdriver.Chrome(options=options)
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
    save_cookies()
