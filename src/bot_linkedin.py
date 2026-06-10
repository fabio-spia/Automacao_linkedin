from pathlib import Path
import openai
from dotenv import load_dotenv
import os
import base64
import pandas as pd
import google.generativeai as genai #no cmd py -m pip install google-generativeai python-dotenv pillow
import pyautogui
import mimetypes
import time

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
def preparar_imagem_base64_url(caminho_imagem):
    if not os.path.isfile(caminho_imagem):
        raise FileNotFoundError(f"Arquivo de imagem não encontrado: {caminho_imagem}")

    mime, _ = mimetypes.guess_type(caminho_imagem)
    if not mime:
        mime = "image/png"

    with open(caminho_imagem, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")

    return f"data:{mime};base64,{b64}"

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
def gerar_resposta(mensagem_usuario, caminho_prompt, caminho_imagem=None, contexto=None):
    if os.path.isfile(caminho_prompt):
        with open(caminho_prompt, "r", encoding="utf-8") as f:
            PROMPT_BASE = f.read()
    else:
        PROMPT_BASE = caminho_prompt
     # Adiciona contexto extra do CSV, se fornecido
    if contexto:
        contexto = carregar_contexto_csv(contexto)
        PROMPT_BASE = f"{PROMPT_BASE}\n\n{contexto}"

    mensagens = [{"role": "system", "content": PROMPT_BASE}]

    if caminho_imagem:
        imagem_data_url = preparar_imagem_base64_url(caminho_imagem)
        mensagens.append({
            "role": "user",
            "content": [
                {"type": "text", "text": mensagem_usuario},
                {"type": "image_url", "image_url": {"url": imagem_data_url}}
            ]
        })
    else:
        mensagens.append({"role": "user", "content": mensagem_usuario}) 

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=mensagens
    )

    return response.choices[0].message.content.strip()

#Função para extrair dados da tela
def extrair_dado(informacao):
    time.sleep(5)
    print_tela = pyautogui.screenshot()
    print_tela.save("assets/print_tela.png")
    prompt_extrair_dado = "Voce vai receber um print da tela, retorne o dado que for pedido na mensagem. Apenas o dado. Se não encontrar retorne apenas null, e nada mais. "
    resposta = gerar_resposta(informacao, prompt_extrair_dado,"assets/print_tela.png") 
    if resposta and resposta.strip().lower() == "null":
        print("Dado nao encontrado")
        return False
    else:
        return resposta

#Função para analisar bugs
def debugging(bug):
    prompt = "Você vai receber o log de um bug, analise e retorne possiveis problemas e possiveis soluçoes. " \
    "Sua resposta deve ter no maximo 300 palavras. Seja objetivo e direto. Responda em portugues"
    print("\n\n\n--------------------------\nAnalise do bug:\n")
    resposta = gerar_resposta(bug,prompt)
    print(resposta)
    print("--------------------------\n\n\n")

# Execução
if __name__ == "__main__":
    
    
    print("Teste")
    while True:

        user_input = input("Digite sua mensagem (ou 'sair' para encerrar): ")
        time.sleep(10)
        if user_input.lower() == 'sair':
            break
        #resposta = gerar_resposta(user_input,"responda oque for perguntado sobre a imagem","assets/print_tela.png")
        resposta = debugging(user_input)
        
