#Automação de Aceitação de Convites no LinkedIn
# 🚀 Automação de Aceitação de Convites no LinkedIn com Selenium

Este projeto é um script Python que automatiza o processo de aceitação de convites no LinkedIn, utilizando **Selenium** para interagir com o navegador Google Chrome.

---

## 🛠️ **Requisitos**
Antes de rodar o script, você precisa instalar os seguintes pacotes:

```sh
pip install selenium webdriver-manager psutil

Além disso, você precisa:

Ter o Google Chrome instalado (versão atualizada recomendada).
Ter o ChromeDriver compatível (o webdriver-manager cuida disso automaticamente).
Saber o caminho do perfil do Chrome que está logado no LinkedIn.

Configuração do Perfil do Chrome
Para que o Selenium use seu perfil logado no LinkedIn, você precisa definir o caminho correto do perfil do Chrome no código.

🔍 Como encontrar o caminho do perfil?
Abra o Google Chrome e digite na barra de endereço:
chrome://version/
Copie o valor do "Caminho do Perfil", que será algo como:
C:\Users\SEU_USUARIO\AppData\Local\Google\Chrome\User Data\Default
No código, substitua PROFILE_PATH pelo caminho copiado.

Como Rodar o Script
Feche TODOS os processos do Chrome antes de rodar o script.
No Prompt de Comando (CMD), rode:
taskkill /F /IM chrome.exe
Execute o script Python:
python linkedin_auto_accept.py
O Selenium abrirá o Chrome, acessará a página de convites do LinkedIn e aceitará automaticamente todas as solicitações pendentes.

Possíveis Erros e Soluções
❌ Erro: "session not created: Chrome failed to start: crashed."
✅ Solução: Feche o Chrome antes de rodar o script.

❌ Erro: O Chrome abre no modo Visitante.
✅ Solução: Verifique se o PROFILE_PATH está correto e se o Chrome não está rodando antes da execução.

❌ Erro: chromedriver.exe não encontrado.
✅ Solução: Atualize o webdriver-manager:
pip install --upgrade webdriver-manager

Personalização
Se quiser mudar o tempo de espera entre as ações, altere os valores de time.sleep(5).
Se quiser rodar o script periodicamente, use um agendador de tarefas no Windows ou cron jobs no Linux.

Conclusão
Este script facilita a aceitação de convites no LinkedIn de forma automática, poupando tempo e evitando ações repetitivas.
Se tiver dúvidas ou melhorias, sinta-se à vontade para contribuir! 🚀

📝 Criado por: João Pedro


