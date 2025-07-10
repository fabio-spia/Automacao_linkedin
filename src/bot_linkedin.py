import openai
import csv
from dotenv import load_dotenv
import os
import base64
import requests
from io import BytesIO
import pandas as pd
load_dotenv("credentials/.env")

# Sua chave da API da OpenAI
client = openai.OpenAI(api_key = os.getenv("API_KEY")) # Preencha de acordo com sua variavel no arquivo .env

# Função para codificar a imagem em base64 e criar o formato necessário
def preparar_imagem_base64_url(url_imagem):
    response = requests.get(url_imagem)
    response.raise_for_status()
    image_data = BytesIO(response.content)
    base64_image = base64.b64encode(image_data.read()).decode("utf-8")
    return f"data:image/jpeg;base64,{base64_image}"

# Função para carregar dados do CSV e formar contexto base
def carregar_contexto_csv(caminho_csv):
    df = pd.read_csv(caminho_csv)
    contexto = ""
    for _, row in df.iterrows(): 
        pergunta = str(row.iloc[0]).strip()  
        resposta = str(row.iloc[1]).strip() 
        if pergunta and resposta:
            contexto += f"Usuário: {pergunta}\nAssistente: {resposta}\n"
            
    return contexto.strip()

# Função para gerar resposta
def gerar_resposta(mensagem_usuario, caminho_prompt, url_imagem=None, contexto=None):
    with open(caminho_prompt, "r", encoding="utf-8") as f:
        PROMPT_BASE = f.read()

     # Adiciona contexto extra do CSV, se fornecido
    if contexto:
        contexto = carregar_contexto_csv(contexto)
        PROMPT_BASE = f"{PROMPT_BASE}\n\n{contexto}"

    mensagens = [{"role": "system", "content": PROMPT_BASE}]

    if url_imagem:
        imagem_base64 = preparar_imagem_base64_url(url_imagem)
        mensagens.append({
            "role": "user",
            "content": [
                {"type": "text", "text": mensagem_usuario},
                {"type": "image_url", "image_url": {"url": imagem_base64}}
            ]
        })
    else:
        mensagens.append({"role": "user", "content": mensagem_usuario}) 

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=mensagens
    )

    return response.choices[0].message.content.strip()


# Execução
if __name__ == "__main__":
    prompt = "data/prompt_comment.txt"
    csv_treinamento = "data/dataset_comment.csv"
    print("Analisador de Texto e Imagem com GPT-4o")
    while True:
        user_input = input("Digite sua mensagem (ou 'sair' para encerrar): ")
        if user_input.lower() == 'sair':
            break
        url_imagem = input("Cole o link da imagem (ou pressione ENTER para não usar imagem): ").strip()
        resposta = gerar_resposta(user_input, prompt, url_imagem if url_imagem else None, csv_treinamento)
        print("\nResposta:\n", resposta)
        print("-" * 50)
