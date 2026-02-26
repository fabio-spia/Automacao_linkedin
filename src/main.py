from accept_invites import accept_invites
from metrics import extract_metrics
from config import get_driver
from send_comment import send_comment
from cookies import loads_cookies
from respond_chat import respond_chat
from creat_post import creat_post

COOKIE_FILE_PATH ="data/cookie_file_path.json" # Arquivo com cookies do perfil


if __name__ == "__main__":
    driver = get_driver()   # Abre o browser
    driver.get("https://www.linkedin.com")  # Abre LinkedIn
    loads_cookies(driver, COOKIE_FILE_PATH)    

    print("🔄 Aceitando convites...")
    accept_invites(driver)

    print("\nComentando em posts...")
    send_comment(driver,20,8)
    
    print("Respondendo chat...")    
    respond_chat(driver)

    print("Criando post...")
    creat_post(driver)

    print("Extraindo metrics de hoje")
    extract_metrics(driver)

    driver.quit()


    
    
    

    
    