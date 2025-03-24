from accept_invites import accept_invites
from send_messages import send_messages

if __name__ == "__main__":
    print("🔄 Aceitando convites e salvando no CSV...")
    accept_invites()

    print("\n📨 Enviando mensagens para os contatos aceitos...")
    send_messages()
   