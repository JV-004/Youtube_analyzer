# app.py (VERSÃO CORRIGIDA COM TRADUÇÃO)
import streamlit as st
import os
import sys
from pathlib import Path

# Adiciona o diretório raiz do projeto ao sys.path para que os módulos possam ser encontrados
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from main import YouTubeAnalyzer  # Importa a classe principal do seu projeto
from utils import cleanup_temp_files, validate_youtube_url # Importa funções úteis

# Configurações iniciais do Streamlit
st.set_page_config(
    page_title="Analisador de Vídeos YouTube com Gemini",
    page_icon="🤖",
    layout="centered"
)

# --- Título e Descrição do Aplicativo ---
st.title("🎬 Analisador de Vídeos do YouTube com Google Gemini")
st.markdown("""
Este aplicativo utiliza a IA Gemini do Google para:
- Baixar o áudio de vídeos do YouTube.
- Transcrever e traduzir o áudio para texto.
- Gerar resumos detalhados e análises do conteúdo em qualquer idioma.
""")
st.info("💡 **Atenção:** Certifique-se de que sua `GOOGLE_API_KEY` esteja configurada como uma variável de ambiente ou inserida abaixo.")

# --- Entrada da API Key (se não estiver em .env) ---
api_key_env = os.getenv('GOOGLE_API_KEY')
if api_key_env:
    st.sidebar.success("✅ `GOOGLE_API_KEY` encontrada como variável de ambiente!")
    google_api_key = api_key_env
else:
    st.sidebar.warning("⚠️ `GOOGLE_API_KEY` não encontrada como variável de ambiente.")
    google_api_key = st.sidebar.text_input("Cole sua Google API Key aqui:", type="password")
    if not google_api_key:
        st.sidebar.error("Por favor, insira sua API Key para continuar.")
        st.stop() # Para a execução se a API Key não for fornecida

# --- Inicialização do Analisador ---
@st.cache_resource # Cacheia a inicialização para não recriar a classe a cada rerun
def get_youtube_analyzer(api_key):
    try:
        return YouTubeAnalyzer(google_api_key=api_key)
    except ValueError as e:
        st.error(f"❌ Erro na inicialização do Analisador: {e}")
        st.warning("Verifique sua Google API Key e tente novamente.")
        return None

analyzer = get_youtube_analyzer(google_api_key)

if not analyzer:
    st.stop() # Para se o analisador não puder ser inicializado

# --- Formulário Principal ---
st.header("Analisar Novo Vídeo")

youtube_url = st.text_input("🔗 Cole a URL do Vídeo do YouTube aqui:", placeholder="Ex: https://www.youtube.com/watch?v=xxxxxxxx")

# Configurações de idioma
st.subheader("🌐 Configurações de Idioma")

col1, col2 = st.columns(2)

with col1:
    source_language_options = {
        "Auto-detectar": None,
        "Português": "pt",
        "Inglês": "en",
        "Espanhol": "es",
        "Francês": "fr"
    }
    selected_source_language_display = st.selectbox(
        "🎤 Idioma do áudio (original):",
        list(source_language_options.keys()),
        help="Idioma em que o vídeo está falado"
    )
    source_language = source_language_options[selected_source_language_display]

with col2:
    target_language_options = {
        "Mesmo do áudio": None,
        "Português": "pt",
        "Inglês": "en", 
        "Espanhol": "es",
        "Francês": "fr"
    }
    selected_target_language_display = st.selectbox(
        "📝 Idioma da transcrição/resumo:",
        list(target_language_options.keys()),
        index=1,  # Padrão para Português
        help="Idioma em que você quer receber a transcrição e resumo"
    )
    target_language = target_language_options[selected_target_language_display]

# Mostra info sobre tradução
if source_language and target_language and source_language != target_language:
    st.success(f"✨ **Tradução ativada:** {selected_source_language_display} → {selected_target_language_display}")
elif target_language:
    st.info(f"🔄 **Transcrição em:** {selected_target_language_display}")

# Opções de resumo
st.subheader("📝 Opções de Resumo")
summary_type_options = {
    "Estruturado (Padrão)": "structured",
    "Lista de Tópicos": "bullet_points",
    "Parágrafo Único": "paragraph"
}
selected_summary_type_display = st.selectbox(
    "📋 Escolha o tipo de resumo:",
    list(summary_type_options.keys())
)
summary_type = summary_type_options[selected_summary_type_display]

if st.button("🚀 Iniciar Análise", type="primary"):
    if not youtube_url:
        st.error("Por favor, insira uma URL do YouTube.")
    elif not validate_youtube_url(youtube_url):
        st.error("URL do YouTube inválida. Verifique o formato.")
    else:
        st.markdown("---")
        st.write("Iniciando análise...")
        
        # Usar st.empty() para atualizar mensagens de progresso
        status_message = st.empty()
        progress_bar = st.progress(0)
        
        try:
            # Chama o método analyze_video da sua classe YouTubeAnalyzer
            with st.spinner("Processando... Isso pode levar alguns minutos."):
                
                # Passo 1: Informações do vídeo
                status_message.info("📋 Obtendo informações do vídeo...")
                progress_bar.progress(10)
                
                video_info = analyzer.downloader.get_video_info(youtube_url)
                if not video_info:
                    st.error("❌ Não foi possível obter informações do vídeo.")
                    st.stop()
                
                # Passo 2: Download
                status_message.info("⬇️ Baixando áudio do YouTube...")
                progress_bar.progress(25)
                
                audio_path = analyzer.downloader.download_audio(youtube_url)
                if not audio_path:
                    st.error("❌ Falha no download do áudio.")
                    st.stop()

                # Passo 3: Conversão
                status_message.info("🔄 Convertendo e otimizando áudio para Gemini...")
                progress_bar.progress(40)
                
                converted_path = analyzer.converter.optimize_for_gemini(audio_path)
                if not converted_path:
                    st.error("❌ Falha na conversão do áudio para o formato Gemini.")
                    st.stop()

                # Passo 4: Transcrição/Tradução
                translation_msg = f" e traduzindo para {selected_target_language_display}" if target_language else ""
                status_message.info(f"🎤 Transcrevendo áudio{translation_msg} com Google Gemini...")
                progress_bar.progress(60)
                
                # CHAMA MÉTODO CORRIGIDO COM PARÂMETROS DE IDIOMA
                transcript_data = analyzer.transcriber.transcribe_audio(
                    converted_path, 
                    language=target_language,
                    source_language=source_language
                )
                if not transcript_data:
                    st.error("❌ Falha na transcrição do áudio.")
                    st.stop()

                # Passo 5: Resumo
                status_message.info("📝 Gerando resumo e análise com Google Gemini...")
                progress_bar.progress(80)
                
                # CHAMA MÉTODO CORRIGIDO COM IDIOMA
                summary_data = analyzer.summarizer.create_summary(
                    transcript_data['text'], 
                    summary_type,
                    target_language=target_language
                )
                
                # ANÁLISE TAMBÉM COM IDIOMA
                analysis_data = analyzer.summarizer.analyze_content(
                    transcript_data['text'],
                    target_language=target_language
                )

                # Combina e exibe os resultados
                final_result = {
                    'video_info': video_info,
                    'transcript': transcript_data,
                    'summary': summary_data,
                    'analysis': analysis_data,
                    'ai_provider': 'Google Gemini',
                    'language_settings': {
                        'source_language': source_language,
                        'target_language': target_language
                    }
                }
                
                progress_bar.progress(100)

            status_message.success("✅ Análise concluída com sucesso!")
            
            st.subheader("📊 Resultados da Análise")

            # Info do vídeo
            if final_result['video_info']:
                st.markdown("### 📺 Informações do Vídeo")
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Título:** {final_result['video_info']['title']}")
                    st.write(f"**Canal:** {final_result['video_info']['author']}")
                with col2:
                    st.write(f"**Duração:** {final_result['video_info']['duration_formatted']}")
                    st.write(f"**Visualizações:** {final_result['video_info']['views']:,}")
                    
                with st.expander("Ver Descrição Original"):
                    st.write(final_result['video_info']['description'])
            
            # Info de idioma
            st.markdown("### 🌐 Configurações de Idioma")
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Idioma do áudio:** {selected_source_language_display}")
            with col2:
                st.write(f"**Idioma de saída:** {selected_target_language_display}")
            
            if source_language and target_language and source_language != target_language:
                st.success("✨ **Tradução aplicada com sucesso!**")
            
            # Resumo
            if final_result['summary']:
                st.markdown("### 📋 Resumo Gerado por IA")
                st.markdown(final_result['summary']['summary'])
                
                st.markdown("---")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write(f"**Modelo:** {final_result['summary']['model_used']}")
                with col2:
                    st.write(f"**Tipo:** {final_result['summary']['summary_type'].replace('_', ' ').title()}")
                with col3:
                    st.write(f"**Compressão:** {final_result['summary']['compression_ratio']:.1%}")

            # Análise detalhada
            if final_result['analysis'] and final_result['analysis']['analysis']:
                st.markdown("### 🔍 Análise Detalhada (Gerada por IA)")
                st.markdown(final_result['analysis']['analysis'])
                st.write(f"**Modelo de Análise:** {final_result['analysis']['model_used']}")

            # Transcrição completa
            if final_result['transcript']:
                with st.expander("Ver Transcrição Completa"):
                    st.markdown("### 📝 Transcrição Completa")
                    st.text_area(
                        "Transcrição:",
                        final_result['transcript']['text'],
                        height=300,
                        disabled=True,
                        label_visibility="collapsed"
                    )
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Caracteres:** {len(final_result['transcript']['text']):,}")
                    with col2:
                        st.write(f"**Idioma:** {final_result['transcript'].get('language', 'Auto-detectado')}")

            st.markdown("---")
            st.success("✅ Processo concluído! Os arquivos de saída também foram salvos na pasta `output/` do projeto.")

        except Exception as e:
            st.error(f"❌ Ocorreu um erro durante a análise: {e}")
            st.exception(e) # Exibe o traceback completo para depuração
        finally:
            st.write("🧹 Limpando arquivos temporários...")
            cleanup_temp_files()
            st.write("✅ Limpeza concluída.")

# --- Informações da API na barra lateral ---
st.sidebar.markdown("---")
st.sidebar.header("📊 Informações da API Google Gemini")
st.sidebar.markdown("""
- **Dashboard:** [aistudio.google.com](https://aistudio.google.com/)
- **Preços:** [ai.google.dev/pricing](https://ai.google.dev/pricing)
- **Documentação:** [ai.google.dev/docs](https://ai.google.dev/docs)
""")

st.sidebar.markdown("---")
st.sidebar.header("🌐 Idiomas Suportados")
st.sidebar.markdown("""
**Transcrição + Tradução:**
- 🇧🇷 Português
- 🇺🇸 Inglês
- 🇪🇸 Espanhol
- 🇫🇷 Francês

**Outros idiomas:** O Gemini pode processar mais idiomas automaticamente.
""")

st.sidebar.markdown("---")
st.sidebar.markdown("Feito com ❤️ e Google Gemini")