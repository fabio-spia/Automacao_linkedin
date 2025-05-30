# 🤖 Automação LinkedIn com Selenium

Automação completa para **aceitar convites** e **enviar mensagens personalizadas** no LinkedIn, utilizando **Python + Selenium**.

---

## 🚀 Funcionalidades

- Aceita todos os convites pendentes automaticamente
- Extrai o **nome e link** do perfil aceito e salva no google sheets
- Envia uma **mensagem personalizada** automaticamente para cada contato aceito
- Utiliza cookies para guardar informações de login, precisa logar apenas 1 vez
- Simula comportamento humano com rolagem suave
- Totalmente automático e robusto contra erros

---

## 🛠️ Requisitos

- Python 3.9+
- Google Chrome
- Conta no google
- Chave de API do chtgpt

### 📦 Instale os pacotes:

```sh
pip install selenium webdriver-manager psutil
pip install pyautogui
pip install chromedriver_autoinstaller
```
## ▶️ Como Executar

1. Siga as instruções contidas no arquivo conection_sheet.py 
2. Crie suas variaveis de ambiente no arquivo .env
3. Rode o script principal:
python main.py
4. Na primeira vez será necessario fazer login.
5. Após inserir as credenciais, vá ate o terminal e pressione "enter"
OBS: O Processo de login não deverá ser feito sempre, apenas quando os cookies expirarem.

## 📄 Estrutura do Projeto
Automacao_linkedin/
├── src                                        # Codigos-fonte
    ├── main.py                                # Executa o fluxo completo
    ├── accept_invites.py                      # Aceita convites + salva CSV
    ├── send_messages.py                       # Envia mensagens personalizadas
    ├── config.py                              # Configurações do Chrome e WebDriver
    ├── bot_linkedin.py                        # Conexão com a api do chatgpt
    ├── conection_sheet.py                     # Conexão com a planilha que vai armazenar os perfis
    ├── save_cookies.py                        # Extrair e salvar cookies do perfil logado
├── assets                                     # Imagens utilizadas
    ├── fechar.png                             # Print do botão de fechar conversa
    ├── search_mesage.png                      # Print do campo de buscar mensagens
├── credentials                                # Credenciais exclusivas de cada maquina que executar esse programa
    ├── .env                                   # Arquvivo com variaveis de ambiente
    ├── google_sheets_credentials.json         # Credenciais do google sheets
├── data                                       # Dados salvos
    ├── cookie_file_path.json                  # Cookies do perfil do linkedin
    ├── profiles.csv                           # Arquivo para armazenar perfis
    ├── prompt.txt                             # Prompt para gerar mensagens



## 💬 Personalização

### Edite o prompt no arquivo prompt.txt para perssonalizar a mensagem enviada para o usuario


## Criado por João Pedro




```
