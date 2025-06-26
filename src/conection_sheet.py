
# ✅ PASSO A PASSO PARA CONECTAR COM GOOGLE SHEETS
# ==========================================

# 1️⃣ Acesse: https://console.cloud.google.com/
#    → Faça login com sua conta Google.

# 2️⃣ Crie um novo projeto ou selecione um existente.

# 3️⃣ Ative as APIs:
#    → Google Sheets API
#    → Google Drive API
#    (Em "APIs & Services" → "Enable APIs and Services")

# 4️⃣ Crie uma Service Account:
#    → IAM & Admin → Service Accounts → Create Service Account.
#    → Dê um nome e clique em "Create and Continue".
#    → Na permissão, pode pular ("Done").

# 5️⃣ Gere a chave JSON:
#    → Na lista de Service Accounts, clique na conta criada.
#    → Aba "Keys" → "Add Key" → "Create New Key".
#    → Selecione "JSON" → "Create".
#    → Baixe, copie o conteudo do arquivo, e cole no arquivo google_sheets_credentials.json.

# 6️⃣ Compartilhe a planilha com a Service Account:
#    → Abra o arquivo JSON e copie o campo "client_email".
#    → Exemplo: minha-conta@meu-projeto.iam.gserviceaccount.com
#    → Vá até sua planilha no Google Sheets.
#    → Clique em "Compartilhar" → cole o e-mail da Service Account → envie.

import csv
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv
import os
load_dotenv("credentials/.env")

# Autenticação
def autenticar_google_sheets(json_keyfile, sheet_name):
    scope = ["https://spreadsheets.google.com/feeds",
             "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(json_keyfile, scope)
    client = gspread.authorize(creds)
    sheet = client.open(sheet_name).sheet1
    return sheet

# Função para adicionar um novo registro
def adicionar_registro():
    json_keyfile = "credentials/google_sheets_credentials.json"
    nome_planilha = os.getenv("NAME_SHEET") # Preencha de acordo com sua variavel no arquivo .env
    CSV_FILE = "data/profiles.csv"
    sheet = autenticar_google_sheets(json_keyfile, nome_planilha)
    
    with open(CSV_FILE, "r", encoding="utf-8") as file:
        reader = csv.reader(file)
        
        next(reader)  # Pula o cabeçalho    

        for row in reader:
            if len(row) < 3:
                continue
            
            date, name, profile_link = row
            nova_linha = [date, name, profile_link]
            sheet.append_row(nova_linha)
            print(name+" adicionado.")     

if __name__ == "__main__":
    adicionar_registro()

           
                  
    
    
