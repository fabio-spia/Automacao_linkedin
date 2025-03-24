# 🤖 Automação LinkedIn com Selenium

Automação completa para **aceitar convites** e **enviar mensagens personalizadas** no LinkedIn, utilizando **Python + Selenium**.

---

## 🚀 Funcionalidades

- Aceita todos os convites pendentes automaticamente
- Extrai o **nome e link** do perfil aceito para um arquivo `profiles.csv`
- Envia uma **mensagem personalizada** automaticamente para cada contato aceito
- Utiliza **seu perfil logado no Chrome**, sem precisar inserir login/senha
- Simula comportamento humano com rolagem suave
- Totalmente automático e robusto contra erros

---

## 🛠️ Requisitos

- Python 3.9+
- Google Chrome instalado
- Perfil do Chrome com LinkedIn já logado

### 📦 Instale os pacotes:

```sh
pip install selenium webdriver-manager psutil
```

## 🔐 Configuração do Perfil do Chrome

### Acesse no Chrome:
```chrome://version```
### Copie o Caminho do Perfil, ex:
```C:\Users\SeuUsuario\AppData\Local\Google\Chrome\User Data```
### Copie também o nome do diretório do perfil logado, ex:
Default, Profile 1, etc.
### No arquivo config.py, configure:
```PROFILE_PATH = "C:\\Users\\SeuUsuario\\AppData\\Local\\Google\\Chrome\\User Data"
PROFILE_NAME = "Default"
```
## ▶️ Como Executar

1. Feche todos os processos do Chrome:
```taskkill /F /IM chrome.exe```
2. Rode o script principal:
```python main.py```

## 📄 Estrutura do Projeto
Automacao_linkedin/
├── main.py                # Executa o fluxo completo
├── accept_invites.py      # Aceita convites + salva CSV
├── send_messages.py       # Envia mensagens personalizadas
├── config.py              # Configurações do Chrome e WebDriver
├── profiles.csv           # Contatos aceitos (nome + link)
├── README.md              # Este arquivo

## 💬 Personalização

### Edite a mensagem padrão no arquivo send_messages.py:
```def generate_message(name):
    return f"Olá {name}, é um prazer conectar com você!"
```
## 🧠 Possíveis Erros
### Chrome failed to start: crashed
Feche o Chrome com taskkill antes de rodar
### Abre no modo Visitante
Verifique PROFILE_PATH e PROFILE_NAME
### chromedriver.exe not found
Atualize com: ```pip install --upgrade webdriver-manager```


## Criado por João Pedro




```
