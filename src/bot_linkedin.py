from pathlib import Path
import openai
import csv
from dotenv import load_dotenv
import os
import base64
import requests
from io import BytesIO
import pandas as pd
import google.generativeai as genai #no cmd py -m pip install google-generativeai python-dotenv pillow
from PIL import Image
from io import BytesIO

load_dotenv("credentials/.env")


# Sua chave da API da OpenAI
client = openai.OpenAI(api_key = os.getenv("API_KEY")) # Preencha de acordo com sua variavel no arquivo .env

#Gerar imagem
def gerar_imagem(prompt: str, caminho_saida: str, model: str = "gemini-2.5-flash-image") -> str:
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY nao encontrada nas variaveis de ambiente")

    genai.configure(api_key=api_key)

    out_path = Path(caminho_saida)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    m = genai.GenerativeModel(model)

    resp = m.generate_content(
        prompt,
        generation_config={
            "response_modalities": ["IMAGE"]
        },
    )

    img_bytes = None

    candidates = getattr(resp, "candidates", None) or []
    for cand in candidates:
        content = getattr(cand, "content", None)
        parts = getattr(content, "parts", None) or []
        for p in parts:
            inline = getattr(p, "inline_data", None)
            if inline and getattr(inline, "data", None):
                img_bytes = inline.data
                break
        if img_bytes:
            break

    if not img_bytes:
        raise RuntimeError("Nao veio imagem na resposta. Talvez o modelo nao suporte IMAGE ou sua conta nao tenha acesso")

    out_path.write_bytes(img_bytes)
    return str(out_path)



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
    prompt = "data/creat_post/prompt_legend.txt"
    csv_treinamento = "data/dataset_comment.csv"
    local_imagem = "data/creat_post/images/post.png"
    prompt_imagem = input("Como voce quer sua imagem ? ")
    gerar_imagem(prompt_imagem,local_imagem)
    print("Analisador de Texto e Imagem com GPT-4o")
    while True:
        user_input = input("Digite sua mensagem (ou 'sair' para encerrar): ")
        if user_input.lower() == 'sair':
            break
        url_imagem = input("Cole o link da imagem (ou pressione ENTER para não usar imagem): ").strip()
        resposta = gerar_resposta(user_input, prompt)
        print("\nResposta:\n", resposta)
        print("-" * 50)
