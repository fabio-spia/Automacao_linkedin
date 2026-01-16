import csv
import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException, ElementClickInterceptedException

URL = "https://rdsummit.rdstation.com/palestrantes"
CSV_FILE = "data/palestrantes.csv"

opts = Options()
opts.add_argument("--start-maximized")
# opts.add_argument("--headless=new")  # se quiser headless
driver = webdriver.Chrome(options=opts)
wait = WebDriverWait(driver, 20)
driver.get(URL)

def js_click(el):
    driver.execute_script("arguments[0].click();", el)

button1 = WebDriverWait(driver, 4).until(
    EC.presence_of_element_located((By.XPATH, "//label[span[text()='1° Dia | 05.11']]/input"))
)
button2 = WebDriverWait(driver, 4).until(
    EC.presence_of_element_located((By.XPATH, "//label[span[text()='2° Dia | 06.11']]/input"))
)
js_click(button1)
js_click(button2)
time.sleep(5)

def dismiss_banners():
    try:
        for _ in range(2):
            btn = WebDriverWait(driver, 4).until(
                EC.presence_of_element_located((
                    By.XPATH,
                    "//button[contains(translate(.,'ACEITAROKENTENDI','aceitarokentendi'),'aceitar') or "
                    "contains(translate(.,'ACEITAROKENTENDI','aceitarokentendi'),'ok') or "
                    "contains(translate(.,'ACEITAROKENTENDI','aceitarokentendi'),'entendi') or "
                    "@id[contains(.,'accept')] or contains(@class,'accept') or contains(@class,'consent')]"
                ))
            )
            if btn.is_displayed():
                js_click(btn)
                time.sleep(0.6)
    except Exception:
        pass

def gentle_scroll():
    last_h = 0
    for _ in range(20):
        driver.execute_script("window.scrollBy(0, document.documentElement.clientHeight*0.7);")
        time.sleep(0.4)
        h = driver.execute_script("return document.body.scrollHeight;")
        if h == last_h:
            break
        last_h = h

def load_more_if_any():
    try:
        while True:
            btn = WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((
                    By.XPATH, "//button[contains(.,'Carregar') or contains(.,'Mais') or contains(.,'Load')]"
                ))
            )
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
            time.sleep(0.2)
            js_click(btn)
            time.sleep(1.2)
    except Exception:
        pass

def collect_cards():
    # Heurística: elementos clicáveis que parecem card de speaker
    js = """
    const nodes = Array.from(document.querySelectorAll('a,article,div,button')).filter(el => {
      const cls = (el.className||'').toString().toLowerCase();
      const tid = (el.getAttribute('data-testid')||'').toLowerCase();
      const role = (el.getAttribute('role')||'').toLowerCase();
      const clickable = el.tagName==='A' || el.tagName==='BUTTON' || role==='button' || el.onclick;
      const hasName = el.querySelector('h1,h2,h3,h4');
      const hasImg  = el.querySelector('img');
      const looks = /speaker|palestrant|card/.test(cls+tid) || (hasName && hasImg);
      const visible = !!(el.offsetWidth || el.offsetHeight || el.getClientRects().length);
      return clickable && looks && visible;
    });
    return nodes;
    """
    return driver.execute_script(js) or []

def wait_modal_open():
    return wait.until(EC.visibility_of_element_located((
        By.CSS_SELECTOR, "div[role='dialog'], div[class*='modal'], section[class*='modal']"
    )))

def close_modal():
    # tenta botão de fechar; se não houver, clica fora
    try:
        btn = WebDriverWait(driver, 6).until(EC.element_to_be_clickable((
            By.XPATH,
            "//div[@role='dialog']//button[@aria-label][contains(translate(@aria-label,'FECHARCLOSE','fecharclose'),'fechar') or contains(translate(@aria-label,'FECHARCLOSE','fecharclose'),'close')]"
        )))
        js_click(btn)
    except Exception:
        try:
            driver.execute_script("""
              const m = document.querySelector("div[role='dialog'], div[class*='modal'], section[class*='modal']");
              if (m) m.click();
            """)
        except Exception:
            pass
    try:
        WebDriverWait(driver, 8).until(EC.invisibility_of_element_located((
            By.CSS_SELECTOR, "div[role='dialog'], div[class*='modal'], section[class*='modal']"
        )))
    except TimeoutException:
        pass

def extract_from_modal(modal):
    # Nome
    try:
        name_el = modal.find_element(By.XPATH, ".//h1|.//h2|.//h3")
        nome = name_el.text.strip()
    except Exception:
        nome = ""

    # Empresa: primeiro bloco de texto imediatamente anterior ao nome
    empresa = ""
    try:
        empresa_el = modal.find_element(
            By.XPATH,
            f".//{name_el.tag_name}/preceding::*[(self::p or self::span or self::div) and normalize-space()][1]"
        )
        empresa = empresa_el.text.strip()
    except Exception:
        pass

    # LinkedIn
    try:
        linkedin = modal.find_element(By.XPATH, ".//a[contains(@href,'linkedin')]").get_attribute("href")
    except Exception:
        linkedin = ""

    # Data: procura um chip/botao com padrão 05.11 ou abreviações
    data = ""
    try:
        chip = modal.find_element(
            By.XPATH,
            ".//button[contains(.,'.') or contains(.,'Qua') or contains(.,'Qui') or contains(.,'Sex') or contains(.,'Sáb') or contains(.,'Dom')]"
        )
        data = chip.text.strip()
    except Exception:
        # fallback: qualquer span/div com esse padrão
        try:
            chip = modal.find_element(
                By.XPATH,
                ".//*[contains(.,'Qua') or contains(.,'Qui') or contains(.,'Sex') or contains(.,'Sáb') or contains(.,'Dom')][string-length(normalize-space())<20]"
            )
            data = chip.text.strip()
        except Exception:
            pass

    # limpeza simples da data
    if data:
        m = re.search(r"\d{2}\.\d{2}.*", data)
        if m:
            data = m.group(0).strip()

    return nome, empresa, linkedin, data

# fluxo
dismiss_banners()
time.sleep(2)
gentle_scroll()
load_more_if_any()
cards = collect_cards()
print(f"Cards detectados: {len(cards)}")

rows = []
for i in range(len(cards)):
    cards = collect_cards()
    if i >= len(cards):
        break
    el = cards[i]

    try:
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
        time.sleep(0.2)
        try:
            el.click()
        except (ElementClickInterceptedException, StaleElementReferenceException):
            js_click(el)

        modal = wait_modal_open()
        time.sleep(0.3)
        nome, empresa, linkedin, data_txt = extract_from_modal(modal)
        rows.append({
            "Nome": nome,
            "Empresa": empresa,
            "LinkedIn": linkedin,
            "Data": data_txt
        })
        print(f"{i+1}. {nome} | {empresa} | {linkedin} | {data_txt}")
        close_modal()
        time.sleep(0.3)

    except TimeoutException:
        continue
    except StaleElementReferenceException:
        continue

# salvar CSV
with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["Nome", "Empresa", "LinkedIn", "Data"])
    writer.writeheader()
    writer.writerows(rows)

print(f"Salvo {len(rows)} registros em {CSV_FILE}")
driver.quit()
