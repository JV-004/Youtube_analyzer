"""
Arquivo: transcriber.py 
Função: Transcreve áudio usando Google Gemini com suporte a tradução
"""

import google.generativeai as genai
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

class AudioTranscriber:
    def __init__(self, api_key=None):
        """
        Inicializa o transcritor com Gemini
        Args:
            api_key (str): Chave da API Google
        """
        if api_key:
            self.api_key = api_key
        else:
            self.api_key = os.getenv('GOOGLE_API_KEY')
        
        if not self.api_key:
            raise ValueError("❌ API Key do Google não fornecida. Use .env ou passe como parâmetro")
        
        # Configura Gemini
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        print("🤖 Gemini configurado com sucesso!")
    
    def transcribe_audio(self, audio_path, language=None, source_language=None):
        """
        Transcreve arquivo de áudio usando Gemini
        Args:
            audio_path (str): Caminho do arquivo de áudio
            language (str): Idioma de SAÍDA desejado (pt, en, es, fr)
            source_language (str): Idioma do áudio original (opcional)
        Returns:
            dict: Resultado da transcrição
        """
        try:
            audio_file = Path(audio_path)
            if not audio_file.exists():
                print(f"❌ Arquivo não encontrado: {audio_path}")
                return None
            
            print(f"🎤 Iniciando transcrição com Gemini...")
            print(f"📁 Arquivo: {audio_file.name}")
            
            # Verifica tamanho do arquivo
            file_size_mb = audio_file.stat().st_size / 1024 / 1024
            print(f"📏 Tamanho: {file_size_mb:.1f} MB")
            
            if file_size_mb > 20:  # Gemini tem limite de ~20MB
                print("⚠️ Arquivo muito grande (>20MB). Considere dividir o áudio.")
                return None
            
            print("🔄 Enviando áudio para Gemini...")
            
            # Upload do arquivo para Gemini
            audio_file_obj = genai.upload_file(path=str(audio_path), display_name="audio_to_transcribe")
            
            # Constrói prompt baseado no idioma desejado
            prompt = self._build_transcription_prompt(language, source_language)
            
            # Gera transcrição
            response = self.model.generate_content([prompt, audio_file_obj])
            
            # Limpa o arquivo temporário do Gemini
            genai.delete_file(audio_file_obj.name)
            
            transcript_text = response.text
            
            result = {
                'text': transcript_text,
                'file_path': str(audio_path),
                'file_size_mb': file_size_mb,
                'language': language or 'auto-detectado',
                'source_language': source_language,
                'model_used': 'gemini-1.5-flash'
            }
            
            print("✅ Transcrição concluída!")
            print(f"📝 Texto gerado: {len(transcript_text)} caracteres")
            print(f"🌐 Idioma de saída: {language or 'original'}")
            
            return result
            
        except Exception as e:
            print(f"❌ Erro na transcrição: {e}")
            return None
    
    def _build_transcription_prompt(self, target_language, source_language):
        """
        Constrói prompt de transcrição baseado nos idiomas
        """
        # Mapeamento de idiomas
        lang_names = {
            'pt': 'português brasileiro',
            'en': 'inglês',
            'es': 'espanhol',
            'fr': 'francês'
        }
        
        # Se não especificou idioma de saída, apenas transcreve
        if not target_language:
            return """
            Transcreva este áudio de forma completa e precisa no idioma original.
            
            Instruções:
            - Mantenha o idioma original do áudio
            - Inclua toda a fala de forma literal
            - Use pontuação natural
            - Não adicione comentários ou interpretações
            
            Retorne apenas o texto transcrito:
            """
        
        # Se especificou idioma de saída diferente
        target_lang_name = lang_names.get(target_language, target_language)
        
        if source_language:
            source_lang_name = lang_names.get(source_language, source_language)
            language_context = f"O áudio está em {source_lang_name} e deve ser traduzido para {target_lang_name}."
        else:
            language_context = f"Transcreva e traduza o conteúdo para {target_lang_name}."
        
        return f"""
        {language_context}
        
        Instruções importantes:
        1. Primeiro, transcreva completamente o que está sendo dito
        2. Se o áudio não estiver em {target_lang_name}, traduza o conteúdo fiel e naturalmente
        3. Mantenha o sentido e contexto original
        4. Use linguagem natural em {target_lang_name}
        5. Preserve nomes próprios, termos técnicos quando apropriado
        6. Não adicione comentários ou interpretações próprias
        
        Retorne apenas o texto final em {target_lang_name}:
        """
    
    def save_transcript(self, transcript_data, output_path):
        """
        Salva transcrição em arquivo de texto
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("=== TRANSCRIÇÃO DE ÁUDIO - GEMINI ===\n\n")
                f.write(f"Arquivo: {transcript_data.get('file_path', 'N/A')}\n")
                f.write(f"Tamanho: {transcript_data.get('file_size_mb', 'N/A'):.1f} MB\n")
                f.write(f"Idioma de saída: {transcript_data.get('language', 'Auto-detectado')}\n")
                if transcript_data.get('source_language'):
                    f.write(f"Idioma original: {transcript_data.get('source_language')}\n")
                f.write(f"Modelo: {transcript_data.get('model_used', 'gemini-1.5-flash')}\n")
                f.write("\n" + "="*50 + "\n\n")
                f.write(transcript_data['text'])
            
            print(f"💾 Transcrição salva em: {output_path}")
            return True
        except Exception as e:
            print(f"❌ Erro ao salvar transcrição: {e}")
            return False