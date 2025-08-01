# 🎬 YouTube Video Analyzer com Google Gemini

Este projeto realiza uma **análise inteligente de vídeos do YouTube** com transcrição, resumo e insights automáticos usando **Google Gemini AI**. Ideal para quem quer extrair conhecimento de vídeos de forma rápida e automatizada.

---

## 🚀 Funcionalidades

- 🔗 Download de vídeos do YouTube (áudio apenas)
- 🎧 Conversão e otimização do áudio (para Whisper ou Gemini)
- ✍️ Transcrição automática usando Gemini
- 🧠 Geração de resumo (estruturado, lista ou parágrafo)
- 📊 Análise do conteúdo: público, tom, palavras-chave, complexidade
- 💾 Geração de relatórios (.txt e .md)

---

## 🛠️ Tecnologias

- Python 3.10+
- [Google Gemini API](https://ai.google.dev/)
- pytubefix
- ffmpeg-python
- python-dotenv
- pathlib

---

## 📦 Instalação

```bash
git clone https://github.com/seu-usuario/seu-projeto.git
cd seu-projeto
python -m venv venv
source venv/bin/activate  # ou venv\Scripts\activate no Windows
pip install -r requirements.txt
```

---

## 📺 Executando com Streamlit

Este projeto também inclui uma interface web feita com **[Streamlit](https://streamlit.io/)** para facilitar a análise de vídeos do YouTube com poucos cliques.

### ▶️ Como usar:

1. **Certifique-se de ter o Streamlit instalado** (já está no `requirements.txt`, mas caso precise):
   ```bash
   pip install streamlit
   ```

2. **Execute o aplicativo com o comando:**
   ```bash
   streamlit run src/app.py
   ```

3. **Acesse no navegador:**  
   O Streamlit abrirá automaticamente o navegador em `http://localhost:8501`

---

### 💡 Funcionalidades na Interface Web

- Campo para colar a URL de um vídeo do YouTube
- Escolha do tipo de resumo: estruturado, tópicos ou parágrafo
- Definição do idioma da transcrição (opcional)
- Exibição:
  - Informações do vídeo (título, canal, visualizações)
  - Transcrição completa
  - Resumo gerado por IA
  - Análise detalhada do conteúdo
- Resultados salvos na pasta `output/` do projeto
- Mensagens de progresso interativo (com `st.spinner` e `st.info`)

---

## 🔑 Configuração da API (Google Gemini)

Para utilizar este projeto, você precisará de uma chave da API Gemini (Google Generative AI). Por motivos de segurança, o arquivo `.env` com a chave real **não está incluído** no repositório.

### ▶️ Passos para configurar:

1. **Crie um arquivo chamado `.env` na raiz do projeto** e adicione a seguinte linha:

   ```env
   GOOGLE_API_KEY=sua_chave_aqui
   ```

   > Substitua `sua_chave_aqui` pela sua chave pessoal da API do Gemini (obtida no [Google Cloud Console](https://console.cloud.google.com/)).

2. **Exemplo de estrutura (`.env.example`)**:
   
   ```env
   GOOGLE_API_KEY=coloque_sua_chave_aqui
   ```

3. **Importante:**
   - O arquivo `.env` está listado no `.gitignore`, portanto **não será enviado ao GitHub**.
   - **Nunca compartilhe sua chave diretamente no código-fonte.**

### 💡 Como carregar a variável no código Python:

```bash
pip install python-dotenv
```

```python
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
```

---

## 📏 Limitações e Capacidade do Projeto

### 1. Limite de Duração de Vídeos (Tempo Máximo)
- **Limite de 20MB** para arquivos enviados ao Gemini (transcriber.py):
  ```python
  if file_size_mb > 20:  # Gemini tem limite de ~20MB
      print("⚠️ Arquivo muito grande (>20MB). Considere dividir o áudio.")
      return None
  ```
- **Estimativa de duração máxima**:
  - MP3 (128kbps mono): ~21 min
  - WAV (16-bit 16kHz mono): ~18 min
  - FLAC: ~30-45 min (compressão variável)

### 2. Limites Gerais do Projeto

| Componente              | Limite                        | Localização               |
|------------------------|-------------------------------|---------------------------|
| **Transcrição Gemini** | 20MB por arquivo              | transcriber.py            |
| **Resumos Gemini**     | 30.000 caracteres de entrada  | summarizer.py (`max_chars`) |
| **Tamanho de Texto**   | Até 5000 caracteres para análise | summarizer.py (`text[:5000]`) |
| **Taxa de Requisições**| 60/min (limite gratuito Gemini) | main.py                  |
| **Tipos de Resumo**    | 3 opções                      | main.py                   |
| **Idiomas Suportados** | pt, en, es                    | main.py / transcriber.py  |
| **Formatos de Áudio**  | MP3, WAV, FLAC                | converter.py              |

### 3. Limites de Testes

1. **Limites da API Gemini**:
   - 60 requisições/min (gratuito)
   - Limite diário variável
   - Até ~60.000 caracteres/min

2. **Recursos Locais**:
   - Espaço em disco (temp_files/)
   - Conversão e memória dependem do dispositivo

### 4. Otimizações para Vídeos Longos

- **Compressão automática** (converter.py):
  ```python
  stream = ffmpeg.output(..., audio_bitrate='128k', ac=1, ar=22050)
  ```

- **Truncagem de texto** (summarizer.py):
  ```python
  if len(text) > max_chars:
      text = text[:max_chars] + "\n\n[...texto truncado...]"
  ```

### 5. Recomendações para Uso

- Para vídeos longos (>20 min): use compressão ou divida o áudio
- Monitore o uso da API: https://aistudio.google.com/app/apikey
- Vídeos ideais: 5-15 min
- Priorize áudio MP3 e defina idioma (ex: `language='pt'`)

**Resumo dos Limites**:
- 🎯 Duração Máxima Prática: 15-20 minutos
- ⚠️ Limite Absoluto: 20MB (~21 min MP3)
- 🔁 Testes por minuto: ~2-3 análises completas
- 📊 Texto Processável: ~30 páginas por requisição

Para expandir os limites:
1. Dividir áudios longos automaticamente
2. Controle de taxa da API
3. Usar Gemini Pro para contextos maiores

---

## 📂 Estrutura de Pastas

```
📁 seu-projeto/
├── .env.example
├── main.py
├── app.py
├── requirements.txt
├── utils/
│   └── audio_handler.py
├── outputs/
└── README.md
```

---

## 📄 Licença

Este projeto está licenciado sob a [MIT License](LICENSE).