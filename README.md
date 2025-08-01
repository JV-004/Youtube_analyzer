# 🎬 Analisador de Vídeos do YouTube com Google Gemini

Este projeto utiliza a inteligência artificial **Google Gemini** para:

- 🔊 Baixar o áudio de vídeos do YouTube
- ✍️ Transcrever e (opcionalmente) traduzir o conteúdo
- 🧠 Gerar resumos e análises com IA
- 🌐 Suporte a múltiplos idiomas (PT, EN, ES, FR)

---

## 🚀 Como executar

1. **Clone o repositório:**
```bash
git clone https://github.com/seu-usuario/youtube-analyzer-gemini.git
cd youtube-analyzer-gemini
````

2. **Crie o arquivo `.env` com sua chave da API Gemini:**

```env
GOOGLE_API_KEY=sua_chave_aqui
```

3. **Instale as dependências:**

```bash
pip install -r requirements.txt
```

4. **Execute o aplicativo:**

```bash
streamlit run src/app.py
```

---

## 📂 Estrutura

* `src/`: Código-fonte principal
* `tools/`: Utilitários e componentes auxiliares
* `output/`: Arquivos gerados (resumos, transcrições)
* `.env`: Chave da API (não incluída no repositório)
* `.gitignore`: Ignora pastas como `env/`, `__pycache__/`, etc.

---

## 📌 Tecnologias

* [Streamlit](https://streamlit.io/)
* [pytubefix](https://pypi.org/project/pytubefix/)
* [ffmpeg-python](https://github.com/kkroening/ffmpeg-python)
* [google-generativeai](https://ai.google.dev/)
