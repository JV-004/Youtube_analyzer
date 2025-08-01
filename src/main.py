import os
import sys
from pathlib import Path
from datetime import datetime

# Importa nossas classes
from downloader import YouTubeDownloader
from converter import AudioConverter
from transcriber import AudioTranscriber
from summarizer import TextSummarizer
from utils import (
    create_directories, 
    validate_youtube_url, 
    cleanup_temp_files,
    sanitize_filename
)

class YouTubeAnalyzer:
    def __init__(self, google_api_key=None):
        """
        Classe principal que coordena todo o processo
        Args:
            google_api_key (str): Chave da API Google
        """
        print("🚀 Inicializando Analisador de Vídeos do YouTube com Google Gemini...")
        
        create_directories()
        
        self.downloader = YouTubeDownloader()
        self.converter = AudioConverter()
        
        try:
            self.transcriber = AudioTranscriber(google_api_key)
            self.summarizer = TextSummarizer(google_api_key)
            print("✅ Componentes inicializados com sucesso!")
        except ValueError as e:
            print(f"❌ Erro na configuração: {e}")
            print("💡 Dica: Configure sua API Key do Google Gemini")
            sys.exit(1)
    
    def analyze_video(self, youtube_url, summary_type='structured', target_language=None, source_language=None):
        """
        Executa análise completa do vídeo com suporte a tradução
        Args:
            youtube_url (str): URL do vídeo do YouTube
            summary_type (str): Tipo de resumo (structured, bullet_points, paragraph)
            target_language (str): Idioma desejado para saída (pt, en, es, fr)
            source_language (str): Idioma original do áudio (opcional)
        """
        print("\n" + "="*60)
        print("🎬 INICIANDO ANÁLISE DE VÍDEO - POWERED BY GEMINI")
        if target_language:
            print(f"🌐 IDIOMA DE SAÍDA: {target_language.upper()}")
        print("="*60)
        
        if not validate_youtube_url(youtube_url):
            print("❌ URL do YouTube inválida")
            return None
        
        try:
            # Passo 1: Obter informações do vídeo
            print("\n📋 PASSO 1: Obtendo informações do vídeo...")
            video_info = self.downloader.get_video_info(youtube_url)
            if not video_info:
                return None
            
            # Passo 2: Download do áudio
            print("\n⬇️ PASSO 2: Fazendo download do áudio...")
            audio_path = self.downloader.download_audio(youtube_url)
            if not audio_path:
                return None
            
            # Passo 3: Conversão do áudio
            print("\n🔄 PASSO 3: Convertendo áudio para formato otimizado...")
            converted_path = self.converter.optimize_for_gemini(audio_path)
            if not converted_path:
                print("❌ Falha na conversão do áudio")
                return None
            
            # Passo 4: Transcrição com Gemini (COM TRADUÇÃO)
            translation_msg = f" e traduzindo para {target_language}" if target_language else ""
            print(f"\n🎤 PASSO 4: Transcrevendo áudio{translation_msg} com Gemini...")
            
            transcript_data = self.transcriber.transcribe_audio(
                converted_path, 
                language=target_language,
                source_language=source_language
            )
            if not transcript_data:
                return None
            
            # Passo 5: Geração do resumo com Gemini (NO IDIOMA ESCOLHIDO)
            print(f"\n📝 PASSO 5: Gerando resumo com Gemini...")
            if target_language:
                print(f"🌐 Resumo será gerado em: {target_language}")
                
            summary_data = self.summarizer.create_summary(
                transcript_data['text'], 
                summary_type,
                target_language=target_language
            )
            if not summary_data:
                return None
            
            # Passo 6: Análise adicional (NO IDIOMA ESCOLHIDO)
            print("\n🔍 PASSO 6: Executando análise detalhada...")
            analysis_data = self.summarizer.analyze_content(
                transcript_data['text'],
                target_language=target_language
            )
            
            # Combina todos os resultados
            final_result = {
                'video_info': video_info,
                'transcript': transcript_data,
                'summary': summary_data,
                'analysis': analysis_data,
                'processing_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'ai_provider': 'Google Gemini',
                'language_settings': {
                    'source_language': source_language,
                    'target_language': target_language
                },
                'files_processed': {
                    'original_audio': audio_path,
                    'converted_audio': converted_path
                }
            }
            
            # Passo 7: Salvar resultados
            print("\n💾 PASSO 7: Salvando resultados...")
            self._save_results(final_result, video_info['title'])
            
            print("\n" + "="*60)
            print("✅ ANÁLISE CONCLUÍDA COM SUCESSO! 🤖 GEMINI")
            if target_language:
                print(f"🌐 CONTEÚDO GERADO EM: {target_language.upper()}")
            print("="*60)
            
            return final_result
            
        except Exception as e:
            print(f"\n❌ Erro durante análise: {e}")
            print(f"\n🔍 Detalhes do erro: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            return None
        finally:
            print("\n🧹 Limpando arquivos temporários...")
            cleanup_temp_files()
    
    def _save_results(self, result_data, video_title):
        """Salva todos os resultados em arquivos"""
        try:
            safe_title = sanitize_filename(video_title)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Adiciona sufixo de idioma se tradução foi aplicada
            language_suffix = ""
            if result_data['language_settings']['target_language']:
                language_suffix = f"_{result_data['language_settings']['target_language']}"
                
            base_filename = f"{safe_title}_{timestamp}{language_suffix}"
            
            # Cria diretório output se não existir
            output_dir = Path("output")
            output_dir.mkdir(exist_ok=True)
            
            # Salva transcrição
            transcript_path = output_dir / f"{base_filename}_transcricao_gemini.txt"
            self.transcriber.save_transcript(result_data['transcript'], str(transcript_path))
            
            # Salva resumo com análise
            summary_path = output_dir / f"{base_filename}_resumo_gemini.md"
            summary_data_with_analysis = result_data['summary'].copy()
            if result_data['analysis']:
                summary_data_with_analysis['analysis'] = result_data['analysis']['analysis']
            
            self.summarizer.save_summary(
                summary_data_with_analysis, 
                str(summary_path), 
                include_analysis=True
            )
            
            # Salva relatório completo
            report_path = output_dir / f"{base_filename}_relatorio_completo_gemini.md"
            self._create_full_report(result_data, str(report_path))
            
            print(f"📁 Arquivos salvos com prefixo: {base_filename}")
            
        except Exception as e:
            print(f"❌ Erro ao salvar resultados: {e}")
    
    def _create_full_report(self, data, output_path):
        """Cria relatório completo"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("# 🎬 RELATÓRIO COMPLETO - ANÁLISE COM GOOGLE GEMINI\n\n")
                
                # Informações do vídeo
                f.write("## 📺 Informações do Vídeo\n\n")
                video_info = data['video_info']
                f.write(f"**Título:** {video_info['title']}\n")
                f.write(f"**Canal:** {video_info['author']}\n")
                f.write(f"**Duração:** {video_info['duration_formatted']}\n")
                f.write(f"**Visualizações:** {video_info['views']:,}\n")
                f.write(f"**Descrição:** {video_info['description']}\n\n")
                
                # Configurações de idioma
                f.write("## 🌐 Configurações de Idioma\n\n")
                lang_settings = data['language_settings']
                source_lang = lang_settings.get('source_language', 'Auto-detectado')
                target_lang = lang_settings.get('target_language', 'Original')
                f.write(f"**Idioma do áudio:** {source_lang}\n")
                f.write(f"**Idioma de saída:** {target_lang}\n")
                if target_lang != 'Original' and source_lang != target_lang:
                    f.write("**✨ Tradução aplicada:** Sim\n")
                f.write("\n")
                
                # Dados técnicos
                f.write("## ⚙️ Dados Técnicos\n\n")
                f.write(f"**Data do processamento:** {data['processing_time']}\n")
                f.write(f"**Provedor de IA:** {data['ai_provider']}\n")
                f.write(f"**Modelo de transcrição:** {data['transcript']['model_used']}\n")
                f.write(f"**Modelo de resumo:** {data['summary']['model_used']}\n")
                f.write(f"**Taxa de compressão:** {data['summary']['compression_ratio']:.1%}\n\n")
                
                # Análise detalhada
                if data['analysis']:
                    f.write("## 🔍 Análise Detalhada\n\n")
                    f.write(data['analysis']['analysis'])
                    f.write("\n\n")
                
                # Resumo
                f.write("## 📋 Resumo\n\n")
                f.write(data['summary']['summary'])
                f.write("\n\n")
                
                # Transcrição completa
                f.write("## 📝 Transcrição Completa\n\n")
                f.write(data['transcript']['text'])
            
            print(f"📊 Relatório completo salvo: {output_path}")
        except Exception as e:
            print(f"❌ Erro ao criar relatório: {e}")

def main():
    """Função principal - interface de linha de comando"""
    print("🎯 ANALISADOR DE VÍDEOS DO YOUTUBE - GOOGLE GEMINI")
    print("="*60)
    
    # Verificar API Key do Google
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("🔑 Configure sua API Key do Google Gemini:")
        print("   1. Acesse: https://aistudio.google.com/app/apikey")
        print("   2. Crie uma nova API Key")
        print("   3. Crie arquivo .env na pasta do projeto")
        print("   4. Adicione: GOOGLE_API_KEY=sua_chave_aqui")
        print("   OU")
        api_key = input("   Digite sua API Key agora: ").strip()
        
        if not api_key:
            print("❌ API Key é obrigatória!")
            sys.exit(1)
    
    # Inicializa analisador
    try:
        analyzer = YouTubeAnalyzer(api_key)
    except Exception as e:
        print(f"❌ Erro na inicialização: {e}")
        sys.exit(1)
    
    # Interface de usuário
    while True:
        print("\n" + "-"*60)
        print("📋 MENU DE OPÇÕES - POWERED BY GEMINI:")
        print("1. 🎬 Analisar vídeo do YouTube")
        print("2. 📊 Ver informações da API")
        print("3. ❌ Sair")
        
        choice = input("\nEscolha uma opção: ").strip()
        
        if choice == '1':
            # Coleta informações do usuário
            url = input("\n🔗 Cole a URL do YouTube: ").strip()
            
            if not url:
                print("❌ URL não pode estar vazia!")
                continue
            
            # Opções de idioma
            print("\n🌐 CONFIGURAÇÃO DE IDIOMAS:")
            print("💡 Dica: Você pode transcrever E traduzir ao mesmo tempo!")
            
            # Idioma do áudio (opcional)
            print("\n🎤 Idioma do áudio original:")
            print("1. Auto-detectar (padrão)")
            print("2. Português")
            print("3. Inglês")
            print("4. Espanhol")
            print("5. Francês")
            
            source_choice = input("Escolha (1-5, Enter para auto): ").strip()
            source_languages = {
                '2': 'pt', '3': 'en', '4': 'es', '5': 'fr'
            }
            source_language = source_languages.get(source_choice)
            
            # Idioma de saída
            print("\n📝 Idioma para transcrição e resumo:")
            print("1. Mesmo do áudio")
            print("2. Português")
            print("3. Inglês")
            print("4. Espanhol")
            print("5. Francês")
            
            target_choice = input("Escolha (1-5): ").strip()
            target_languages = {
                '2': 'pt', '3': 'en', '4': 'es', '5': 'fr'
            }
            target_language = target_languages.get(target_choice)
            
            # Mostra configuração escolhida
            if target_language:
                lang_names = {'pt': 'Português', 'en': 'Inglês', 'es': 'Espanhol', 'fr': 'Francês'}
                print(f"\n✨ Saída será em: {lang_names[target_language]}")
                if source_language and source_language != target_language:
                    print(f"🔄 Tradução: {lang_names[source_language]} → {lang_names[target_language]}")
            
            # Opções de resumo
            print("\n📝 Tipos de resumo disponíveis:")
            print("1. Estruturado (padrão)")
            print("2. Lista de tópicos")
            print("3. Parágrafo único")
            
            summary_choice = input("Escolha o tipo (1-3, Enter para padrão): ").strip()
            summary_types = {
                '1': 'structured',
                '2': 'bullet_points', 
                '3': 'paragraph'
            }
            summary_type = summary_types.get(summary_choice, 'structured')
            
            # Executa análise
            print(f"\n🚀 Iniciando análise com Google Gemini...")
            result = analyzer.analyze_video(
                url, 
                summary_type, 
                target_language=target_language,
                source_language=source_language
            )
            
            if result:
                print("\n🎉 Análise concluída! Verifique a pasta 'output' para os resultados.")
                
                # Mostra preview do resumo
                print("\n📋 PREVIEW DO RESUMO:")
                print("-" * 50)
                preview = result['summary']['summary'][:500]
                print(preview + "..." if len(result['summary']['summary']) > 500 else preview)
                print("-" * 50)
                
                # Estatísticas
                print(f"\n📊 ESTATÍSTICAS:")
                print(f"🎯 Provedor: {result['ai_provider']}")
                if result['language_settings']['target_language']:
                    print(f"🌐 Idioma de saída: {result['language_settings']['target_language']}")
                print(f"📝 Caracteres transcritos: {len(result['transcript']['text']):,}")
                print(f"📋 Caracteres do resumo: {len(result['summary']['summary']):,}")
                print(f"📉 Taxa de compressão: {result['summary']['compression_ratio']:.1%}")
            else:
                print("\n❌ Falha na análise. Verifique os logs acima.")
        
        elif choice == '2':
            print("\n📊 INFORMAÇÕES DA API GOOGLE GEMINI:")
            print("🔗 Dashboard: https://aistudio.google.com/")
            print("💰 Preços: https://ai.google.dev/pricing")
            print("📚 Documentação: https://ai.google.dev/docs")
            print("\n✅ VANTAGENS DO GEMINI:")
            print("• API gratuita mais generosa")
            print("• 60 requisições por minuto (gratuito)")
            print("• Suporte nativo a áudio")
            print("• Modelos multimodais")
            print("• Sem cobrança por tokens de entrada")
            print("\n🌐 IDIOMAS SUPORTADOS:")
            print("• Português, Inglês, Espanhol, Francês")
            print("• Tradução automática entre idiomas")
            print("• Detecção automática do idioma do áudio")
        
        elif choice == '3':
            print("\n👋 Até logo! Obrigado por usar o Analisador com Gemini!")
            break
        else:
            print("❌ Opção inválida!")

if __name__ == "__main__":
    main()