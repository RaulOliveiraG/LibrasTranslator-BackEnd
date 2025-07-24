
markdown
Copiar
Editar
# 🤟 LibrasTranslatorApp-BackEnd

Backend de um aplicativo de tradução de Libras (Língua Brasileira de Sinais). Ele é responsável por processar frames de vídeo, identificar gestos e expressões faciais, e traduzi-los para texto ou outros formatos, utilizando bibliotecas de visão computacional e aprendizado de máquina.

---

## ✨ Funcionalidades

- 📹 Processamento de frames de vídeo para reconhecimento de sinais.
- ✋ Identificação de gestos e expressões faciais em tempo real.
- 🎯 Calibração de modelos para melhor precisão.
- 🔗 API RESTful para comunicação com o frontend.
- 📡 Comunicação via WebSocket para streaming de dados e eventos.

---

## ⚙️ Requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)

---

## 🚀 Instalação

```bash
# 1. Clone o repositório (ou descompacte o ZIP)
git clone https://github.com/seu-usuario/LibrasTranslatorApp-BackEnd.git

# 2. Acesse o diretório do projeto
cd LibrasTranslatorApp-BackEnd

# 3. Crie e ative um ambiente virtual (recomendado)
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 4. Instale as dependências
pip install -r requirements.txt

# 5. (Opcional) Instale dependências adicionais, se necessário
▶️ Como Executar
bash
Copiar
Editar
# Inicie o servidor backend
python server.py

# (Opcional) Execute o módulo de reconhecimento para testes com a câmera
python recognition.py
📁 Estrutura do Projeto
bash
Copiar
Editar
LibrasTranslatorApp-BackEnd/
├── .git/                   # Metadados do Git
├── .gitignore              # Arquivos ignorados pelo Git
├── .vscode/                # Configurações do VS Code
├── __pycache__/            # Arquivos temporários Python
├── build/                  # Arquivos de build (se houver)
├── calibracao.py           # Módulo de calibração
├── expressoes.py           # Reconhecimento de expressões faciais
├── gestos.py               # Reconhecimento de gestos com as mãos
├── mp/                     # Módulos do MediaPipe (instalado via pip)
├── recognition.py          # Script de reconhecimento (vídeo/câmera)
├── requirements.txt        # Lista de dependências Python
├── server.py               # Servidor Flask com API + WebSocket
├── utils.py                # Funções utilitárias
└── README.md               # Este arquivo
🧪 Tecnologias Utilizadas
Python – Linguagem principal.

Flask – Microframework web para API RESTful.

Flask-SocketIO – Suporte a WebSockets com Flask.

Flask-CORS – Compartilhamento de recursos entre origens diferentes.

OpenCV – Processamento de imagem e vídeo.

MediaPipe – Framework de visão computacional (pose, mãos etc.).

NumPy – Computação numérica.

WebSockets – Comunicação em tempo real.

🤝 Contribuição
Contribuições são bem-vindas!
Abra uma issue, envie um pull request ou sugira melhorias.
