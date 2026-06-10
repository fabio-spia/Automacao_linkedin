from accept_invites import accept_invites
from metrics import extract_metrics
from config import get_driver
from send_comment import send_comment
from cookies import loads_cookies
from respond_chat import respond_chat
from creat_post import creat_post

COOKIE_FILE_PATH ="data/cookie_file_path.json" # Arquivo com cookies do perfil

driver = get_driver()   # Abre o browser
driver.get("https://www.linkedin.com")  # Abre LinkedIn
loads_cookies(driver, COOKIE_FILE_PATH)    

print("🔄 Aceitando convites...")
accept_invites(driver)

print("\n\n\n\n-------------------------------------------------------------")
print("\nComentando em posts...\n")
send_comment(driver,20,5)

print("\n\n\n\n-------------------------------------------------------------")
print("\nRespondendo chat...\n")
respond_chat(driver)

#print("\n\n\n\n-------------------------------------------------------------")
#print("\nCriando post...\n")
#creat_post(driver)

print("\n\n\n\n-------------------------------------------------------------")
print("\nExtraindo metrics de hoje...\n")
extract_metrics(driver)

driver.quit()


    
    
    

    
    