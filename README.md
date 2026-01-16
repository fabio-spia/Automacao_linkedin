# Automacao LinkedIn 

Projeto em Python para automatizar tarefas no LinkedIn usando Selenium (e PyAutoGUI em alguns passos).
O fluxo principal pode:
- aceitar convites
- enviar mensagens personalizadas com IA
- comentar em posts (com filtro por relevancia e idioma)
- enviar pedidos de conexao para autores de posts comentados (com nota personalizada)
- registrar tudo em CSV e no Google Sheets
- extrair metricas do SSI

Aviso importante:
Automacoes no LinkedIn podem violar termos de uso e podem gerar bloqueios, captchas ou restricoes na conta.
Use com cuidado, de preferencia em ambiente de testes, e mantenha delays altos.

## Funcionalidades (o que existe hoje no projeto)

1) Aceitar convites
- Abre o gerenciador de convites e aceita todos
- Salva data, nome, url do perfil e titulo em `data/profiles.csv`

2) Enviar mensagens (pos aceite)
- Abre o perfil e clica em "Enviar mensagem"
- Gera resposta via IA usando `data/prompt_message.txt`
- Digita de forma humanizada (PyAutoGUI + pyperclip)
- Fecha chats abertos usando imagens em `assets/fechar1.png` e `assets/fechar2.png`

3) Comentar no feed
- Varre posts do feed e ignora:
  - posts promovidos
  - posts nao em portugues (langdetect)
  - posts ja curtidos/comentados
- Classifica se vale comentar usando `data/prompt_rate_post.txt` + `data/dataset_post.csv`
- Se aprovado, gera comentario com `data/prompt_comment.txt` + `data/dataset_comment.csv`
- Salva:
  - `data/posts.csv` com legenda, motivo e comentario
  - `data/profiles_conections.csv` com perfis dos autores (para depois conectar)

4) Enviar conexoes para perfis coletados
- Le `data/profiles_conections.csv`
- Para cada perfil:
  - se ja for conexao (1o), envia mensagem
  - se nao for, envia convite com nota (mensagem gerada por IA)

5) Extrair metricas SSI
- Abre `https://www.linkedin.com/sales/ssi`
- Extrai sub-scores e SSI total
- Registra na aba `Metricas` no Google Sheets

6) Criar post 
- Coleta temas em alta no feed
- Escolhe tema, gera legenda e gera imagem via Gemini
- Anexa imagem e marca perfis

## Requisitos

- Python 3.9+
- Google Chrome instalado
- Ambiente com interface grafica (necessario para PyAutoGUI)
- Conta Google (para Google Sheets)
- Chaves:
  - OpenAI (mensagens e analises)
  - Gemini (geracao de imagem, usado no script de criar post)

## Instalacao
```sh
pip install selenium chromedriver-autoinstaller
pip install pyautogui pyperclip
pip install python-dotenv
pip install openai
pip install pandas requests pillow
pip install google-generativeai
pip install gspread oauth2client
pip install langdetect
```

## Variaveis de ambiente
Crie/edite credentials/.env com:
```sh
API_KEY="SUA_CHAVE_OPENAI"
GEMINI_API_KEY="SUA_CHAVE_GEMINI"
NAME_SHEET="NOME_DA_SUA_PLANILHA_NO_GOOGLE_SHEETS"
```

## Arquivos gerados e formatos

data/profiles.csv
data_hora, nome, url, titulo

data/posts.csv
legenda, motivo, comentario

data/profiles_conections.csv
data_hora, nome, url, titulo, legenda_do_post

data/erro.csv
nome_busca, motivo_erro (usado no fluxo de conexoes por busca)

## Estrutura do projeto
```sh
Automacao_linkedin/
  src/
    main.py
    config.py
    save_cookies.py
    accept_invites.py
    send_messages.py
    send_comment.py
    send_connection.py
    metrics.py
    creat_post.py
    bot_linkedin.py
    conection_sheet.py
    filter_posts.py
    extract_comment.py
    extract_url.py
  assets/
    fechar1.png
    fechar2.png
    conectar.png
    conectar2.png
    mais.png
    recent.png
  credentials/
    .env
    google_sheets_credentials.json
  data/
    cookie_file_path.json
    cookies_teste.json
    profiles.csv
    posts.csv
    profiles_conections.csv
    dataset_comment.csv
    dataset_post.csv
    prompt_message.txt
    prompt_comment.txt
    prompt_rate_post.txt
    prompt_connection.txt
    prompt_event.txt
    creat_post/
      images/post.png
      prompt_choose_theme.txt
      prompt_legend.txt
      topics_posted.csv
```
## Personalização

### Edite os prompts para perssonalizar a mensagem enviada para o usuario


## Criado por João Pedro na NCD