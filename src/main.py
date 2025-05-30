from accept_invites import accept_invites
from send_messages import send_messages
from conection_sheet import adicionar_registro

if __name__ == "__main__":
    print("🔄 Aceitando convites e salvando no CSV...")
    accept_invites()

    print("\n📨 Enviando mensagens para os contatos aceitos...")
    send_messages()
   
    print("\n Salvando no google sheets...")
    adicionar_registro()
