"""
Arquivo: utils.py
Função: Contém funções auxiliares usadas em todo o projeto
"""
import os
import re
from pathlib import Path

def create_directories():
    """
    Cria diretórios necessários para o projeto
    """
    directories = ['temp_files', 'output']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Diretório '{directory}' criado/verificado")
        

def sanitize_filename(filename):
    """
    Remove caracteres inválidos do nome do arquivo
    Args:
        filename (str): Nome do arquivo original
    Returns:
        str: Nome do arquivo limpo
    """
    # Remove caracteres especiais e substitui por underscore
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove espaços extras e limita tamanho
    sanitized = re.sub(r'\s+', ' ', sanitized).strip()[:100]
    return sanitized

def format_duration(seconds):
    """
    Converte segundos em formato legível (HH:MM:SS)
    Args:
        seconds (int): Duração em segundos
    Returns:
        str: Duração formatada
    """
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    else:
        return f"{minutes:02d}:{seconds:02d}"
    
def cleanup_temp_files():
    """
    Remove arquivos temporários após processamento
    """
    temp_dir = Path('temp_files')
    if temp_dir.exists():
        for file in temp_dir.glob('*'):
            try:
                file.unlink()
                print(f"🗑️ Arquivo temporário removido: {file.name}")
            except Exception as e:
                print(f"⚠️ Erro ao remover {file.name}: {e}")
                
def validate_youtube_url(url):
    """
    Valida se a URL é do YouTube
    Args:
        url (str): URL para validar
    Returns:
        bool: True se válida, False caso contrário
    """
    youtube_patterns = [
        r'youtube\.com/watch\?v=',
        r'youtu\.be/',
        r'youtube\.com/embed/',
        r'youtube\.com/v/'
    ]
    
    return any(re.search(pattern, url) for pattern in youtube_patterns)