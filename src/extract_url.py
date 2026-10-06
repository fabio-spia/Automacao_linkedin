import csv
import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException, ElementClickInterceptedException
from config import get_driver

URL = "https://rdsummit.rdstation.com/palestrantes"
CSV_FILE = "data/profiles_conections.csv"

driver = get_driver()
driver.get("https://agiletrendsbr.com/agile-trends-nordeste-2026/")

speakers = WebDriverWait(driver, 20).until(
    EC.presence_of_all_elements_located(
        (By.CSS_SELECTOR, "li.sz-speaker h3.sz-speaker__name a")
    )
)
print("\n"+str(len(speakers))+"\n")

dados = []

for speaker in speakers:
    driver.execute_script("arguments[0].click();", speaker)

    modal = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located(
            (By.CSS_SELECTOR, "div.sz-modal, div[role='dialog'], .modal")
        )
    )

    try:
        linkedin = modal.find_element(
            By.CSS_SELECTOR,
            ".sz-speaker__links a[href*='linkedin.com']"
        )
        linkedin_url = linkedin.get_attribute("href")
    except:
        linkedin_url = ""

    print(linkedin_url)
    dados.append([linkedin_url])

    fechar = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, ".sz-modal__close, .modal-close, button[aria-label='Close']")
        )
    )
    fechar.click()

with open(CSV_FILE, "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.writer(f)
    writer.writerows(dados)

print(f"Salvo {len(dados)} registros salvos")
driver.quit()
