import csv
import time
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import get_driver

# 🔹 Caminho do arquivo CSV
CSV_FILE = "profiles.csv"

def accept_invites():
    """Aceita convites e salva nome + link no CSV"""
    driver = get_driver()
    driver.get("https://www.linkedin.com/mynetwork/invitation-manager/")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    time.sleep(5)

    with open(CSV_FILE, "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        while True:
            # 🔹 Encontrar botões "Aceitar"
            accept_buttons = driver.find_elements(By.XPATH, "//button[.//span[text()='Aceitar']]")

            if not accept_buttons:
                print("✅ Todos os convites foram aceitos!")
                break

            for btn in accept_buttons:
                try:
                    user_card = btn.find_element(By.XPATH, "./ancestor::li")
                    user_name_element = user_card.find_element(By.XPATH, ".//a[@data-test-app-aware-link]/strong")
                    user_name = user_name_element.text.strip()
                    user_link = user_card.find_element(By.XPATH, ".//a[@data-test-app-aware-link]").get_attribute("href")
                    data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                    # 🔹 Salvar no CSV
                    writer.writerow([data_hora, user_name, user_link])
                    print(f"✔ Convite aceito de {user_name} ({user_link}) em {data_hora}")

                    btn.click()
                    time.sleep(2)

                except Exception as e:
                    print(f"⚠ Erro ao aceitar convite: {e}")

            driver.refresh()
            time.sleep(5)

    driver.quit()

if __name__ == "__main__":
    accept_invites()
