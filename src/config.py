import chromedriver_autoinstaller
from selenium import webdriver 
from selenium.webdriver.chrome.options import Options

def get_driver():
    """Configura e retorna o driver do Selenium"""
    chromedriver_autoinstaller.install()
    chrome_options = Options()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("--disable-infobars")
    
    print("✅ Iniciando o Chrome com chromedriver-autoinstaller...")
    try:
        driver = webdriver.Chrome(options=chrome_options)
        return driver
    except Exception as e:
        print("❌ Erro ao iniciar o Chrome:", e)
        raise

    