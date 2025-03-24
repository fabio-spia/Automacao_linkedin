from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


# 🔹 Caminho do perfil do Chrome
PROFILE_PATH = r"C:\Users\55839\AppData\Local\Google\Chrome\User Data"
PROFILE_NAME = "Profile 16"

def get_driver():
    """Configura e retorna o driver do Selenium"""
    chrome_options = Options()
    chrome_options.add_argument(f"user-data-dir={PROFILE_PATH}")
    chrome_options.add_argument(f"--profile-directory={PROFILE_NAME}")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("--disable-infobars")



    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    