"""
Arquivo: downloader.py
Função: Baixa áudio de vídeos do YouTube usando pytubefix
"""

from pytubefix import YouTube
from pathlib import Path
import os
from utils import sanitize_filename, format_duration

class YouTubeDownloader:
    def __init__(self, output_dir='temp_files'):
        """
        Inicializa o downloader
        Args:
            output_dir (str): Diretório para salvar arquivos
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
    def get_video_info(self, url):
        """
        Obtém informações do vídeo sem baixar
        Args:
            url (str): URL do vídeo YouTube
        Returns:
            dict: Informações do vídeo
        """
        try:
            yt = YouTube(url)
            
            info = {
                'title': yt.title,
                'duration': yt.length,
                'duration_formatted': format_duration(yt.length),
                'author': yt.author,
                'views': yt.views,
                'description': yt.description[:200] + '...' if len(yt.description) > 200 else yt.description
            }
            
            print(f"📺 Título: {info['title']}")
            print(f"⏱️ Duração: {info['duration_formatted']}")
            print(f"👤 Canal: {info['author']}")
            print(f"👁️ Visualizações: {info['views']:,}")
            
            return info
            
        except Exception as e:
            print(f"❌ Erro ao obter informações do vídeo: {e}")
            return None
        
    def download_audio(self, url):
        """
        Baixa apenas o áudio do vídeo
        Args:
            url (str): URL do vídeo YouTube
        Returns:
            str: Caminho do arquivo baixado ou None se erro
        """
        try:
            print("🔄 Iniciando download...")
            yt = YouTube(url)
            
            # Seleciona stream de áudio apenas (mais eficiente)
            audio_stream = yt.streams.filter(only_audio=True).first()
            
            if not audio_stream:
                print("❌ Nenhum stream de áudio encontrado")
                return None
            
            # Nome do arquivo limpo
            filename = sanitize_filename(yt.title)
            
            print(f"⬇️ Baixando: {yt.title}")
            print(f"📁 Formato: {audio_stream.mime_type}")
            print(f"📏 Tamanho: {audio_stream.filesize / 1024 / 1024:.1f} MB")
            
            # Download do arquivo
            output_path = audio_stream.download(
                output_path=self.output_dir,
                filename=f"{filename}.{audio_stream.subtype}"
            )
            
            print(f"✅ Download concluído: {Path(output_path).name}")
            return output_path
            
        except Exception as e:
            print(f"❌ Erro no download: {e}")
            return None
        
    def download_with_progress(self, url, progress_callback=None):
        """
        Download com callback de progresso (versão avançada)
        Args:
            url (str): URL do vídeo
            progress_callback (function): Função para mostrar progresso
        Returns:
            str: Caminho do arquivo baixado
        """
        def on_progress(stream, chunk, bytes_remaining):
            total_size = stream.filesize
            bytes_downloaded = total_size - bytes_remaining
            percentage = bytes_downloaded / total_size * 100
            
            if progress_callback:
                progress_callback(percentage)
            else:
                print(f"\r📥 Progresso: {percentage:.1f}%", end='', flush=True)
        
        try:
            yt = YouTube(url, on_progress_callback=on_progress)
            audio_stream = yt.streams.filter(only_audio=True).first()
            
            filename = sanitize_filename(yt.title)
            output_path = audio_stream.download(
                output_path=self.output_dir,
                filename=f"{filename}.{audio_stream.subtype}"
            )
            
            print("\n✅ Download concluído com sucesso!")
            return output_path
            
        except Exception as e:
            print(f"\n❌ Erro no download: {e}")
            return None
