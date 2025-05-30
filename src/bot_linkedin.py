import openai
from dotenv import load_dotenv
import os
load_dotenv("credentials/.env")

# Sua chave da API da OpenAI
client = openai.OpenAI(api_key = os.getenv("API_KEY")) # Preencha de acordo com sua variavel no arquivo .env

# Prompt base do sistema
with open("data/prompt.txt", "r", encoding="utf-8") as f:
    PROMPT_BASE = f.read()

# Função para gerar resposta
def gerar_resposta(mensagem_usuario):
    response = client.chat.completions.create(
        model="gpt-4o",  # Use "gpt-4o" se quiser o modelo mais recente
        messages=[
            {"role": "system", "content": PROMPT_BASE},
            {"role": "user", "content": mensagem_usuario}
        ]
    )
    return response.choices[0].message.content.strip()

if __name__ == "__main__":
    print("Bem-vindo ao Gerador de Respostas com ChatGPT (GPT-4o)!")
    while True:
        user_input = input("Digite sua mensagem (ou 'sair' para encerrar): ")
        if user_input.lower() == 'sair':
            break
        resposta = gerar_resposta(user_input)
        print("\nResposta do ChatGPT:\n", resposta)
        print("-" * 50)