"""
Arquivo: converter.py (VERSÃO UNIFICADA)
Função: Converte áudio para formatos compatíveis com diferentes APIs de IA
"""

import ffmpeg
from pathlib import Path
import os

class AudioConverter:
    def __init__(self, output_dir='temp_files'):
        """
        Inicializa o conversor
        Args:
            output_dir (str): Diretório para arquivos convertidos
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def convert_to_wav(self, input_path, target_sample_rate=16000):
        """
        Converte áudio para WAV com taxa de amostragem específica
        Args:
            input_path (str): Caminho do arquivo original
            target_sample_rate (int): Taxa de amostragem desejada
        Returns:
            str: Caminho do arquivo convertido ou None se erro
        """
        try:
            input_file = Path(input_path)
            if not input_file.exists():
                print(f"❌ Arquivo não encontrado: {input_path}")
                return None
            
            # Nome do arquivo de saída
            output_filename = f"{input_file.stem}_converted.wav"
            output_path = self.output_dir / output_filename
            
            print(f"🔄 Convertendo para WAV...")
            print(f"📂 Entrada: {input_file.name}")
            print(f"📁 Saída: {output_filename}")
            print(f"🎵 Taxa de amostragem: {target_sample_rate} Hz")
            
            # Configuração do ffmpeg
            stream = ffmpeg.input(str(input_file))
            stream = ffmpeg.output(
                stream,
                str(output_path),
                acodec='pcm_s16le',  # Codec PCM 16-bit
                ac=1,                # Mono (1 canal)
                ar=target_sample_rate,  # Taxa de amostragem
                loglevel='error'     # Reduz logs do ffmpeg
            )
            
            # Executa conversão (sobrescreve se arquivo existir)
            ffmpeg.run(stream, overwrite_output=True, quiet=True)
            
            # Verifica se conversão foi bem-sucedida
            if output_path.exists():
                file_size = output_path.stat().st_size / 1024 / 1024
                print(f"✅ Conversão concluída!")
                print(f"📏 Tamanho do arquivo: {file_size:.1f} MB")
                return str(output_path)
            else:
                print("❌ Falha na conversão - arquivo não foi criado")
                return None
                
        except ffmpeg.Error as e:
            print(f"❌ Erro do FFmpeg: {e}")
            if hasattr(e, 'stderr') and e.stderr:
                print(f"Detalhes: {e.stderr.decode('utf-8')}")
            return None
        except Exception as e:
            print(f"❌ Erro na conversão: {e}")
            return None
    
    def get_audio_info(self, file_path):
        """
        Obtém informações do arquivo de áudio
        Args:
            file_path (str): Caminho do arquivo
        Returns:
            dict: Informações do áudio
        """
        try:
            probe = ffmpeg.probe(file_path)
            audio_stream = next(
                (stream for stream in probe['streams'] 
                if stream['codec_type'] == 'audio'), None
            )
            
            if not audio_stream:
                return None
            
            info = {
                'duration': float(audio_stream.get('duration', 0)),
                'sample_rate': int(audio_stream.get('sample_rate', 0)),
                'channels': int(audio_stream.get('channels', 0)),
                'codec': audio_stream.get('codec_name', 'unknown'),
                'bitrate': int(audio_stream.get('bit_rate', 0)) if audio_stream.get('bit_rate') else 0
            }
            
            return info
            
        except Exception as e:
            print(f"❌ Erro ao obter informações do áudio: {e}")
            return None
    
    def optimize_for_whisper(self, input_path, target_ai='whisper'):
        """
        MÉTODO UNIFICADO: Otimiza áudio para diferentes APIs de IA
        Args:
            input_path (str): Caminho do arquivo original
            target_ai (str): 'whisper' ou 'gemini' para otimizações específicas
        Returns:
            str: Caminho do arquivo otimizado
        """
        try:
            print(f"🔄 Otimizando áudio para {target_ai.upper()}...")
            
            input_file = Path(input_path)
            if not input_file.exists():
                print(f"❌ Arquivo não encontrado: {input_path}")
                return None
            
            # Verifica tamanho do arquivo
            file_size_mb = input_file.stat().st_size / 1024 / 1024
            print(f"📏 Tamanho original: {file_size_mb:.1f} MB")
            
            if target_ai.lower() == 'gemini':
                return self._optimize_for_gemini_internal(input_path, input_file, file_size_mb)
            else:
                return self._optimize_for_whisper_internal(input_path, input_file)
                
        except Exception as e:
            print(f"❌ Erro na otimização: {e}")
            return str(input_path)  # Fallback para arquivo original
    
    def _optimize_for_whisper_internal(self, input_path, input_file):
        """
        Otimização específica para Whisper API
        - 16kHz de sample rate
        - Mono (1 canal)  
        - Formato WAV
        """
        print("🎯 Aplicando otimizações para Whisper...")
        return self.convert_to_wav(input_path, target_sample_rate=16000)
    
    def _optimize_for_gemini_internal(self, input_path, input_file, file_size_mb):
        """
        Otimização específica para Google Gemini
        - MP3, WAV, FLAC aceitos
        - Máximo ~20MB
        - Taxa de amostragem até 48kHz
        """
        print("🎯 Aplicando otimizações para Gemini...")
        
        # Se arquivo já está em formato adequado e tamanho OK, retorna o original
        if input_file.suffix.lower() in ['.mp3', '.wav', '.flac'] and file_size_mb <= 18:
            print("✅ Arquivo já está otimizado para Gemini")
            return str(input_path)
        
        # Caso contrário, converte para MP3 com compressão
        output_filename = f"{input_file.stem}_gemini_optimized.mp3"
        output_path = self.output_dir / output_filename
        
        print(f"🔄 Convertendo para MP3 otimizado...")
        
        try:
            # Configuração para MP3 otimizado
            stream = ffmpeg.input(str(input_file))
            stream = ffmpeg.output(
                stream,
                str(output_path),
                acodec='mp3',           # Codec MP3
                audio_bitrate='128k',   # Bitrate moderado
                ac=1,                   # Mono para reduzir tamanho
                ar=22050,              # Sample rate otimizado para Gemini
                loglevel='error'
            )
            
            # Executa conversão
            ffmpeg.run(stream, overwrite_output=True, quiet=True)
            
            if output_path.exists():
                new_size_mb = output_path.stat().st_size / 1024 / 1024
                print(f"✅ Otimização concluída!")
                print(f"📏 Novo tamanho: {new_size_mb:.1f} MB")
                print(f"📉 Redução: {((file_size_mb - new_size_mb) / file_size_mb * 100):.1f}%")
                return str(output_path)
            else:
                print("❌ Falha na otimização")
                return str(input_path)  # Retorna original como fallback
                
        except Exception as e:
            print(f"❌ Erro na conversão: {e}")
            return str(input_path)
    
    def optimize_for_gemini(self, input_path):
        """
        MÉTODO DE COMPATIBILIDADE: Chama optimize_for_whisper com target='gemini'
        Mantém compatibilidade com código existente que chama este método
        """
        return self.optimize_for_whisper(input_path, target_ai='gemini')
    
    def convert_for_compatibility(self, input_path, target_format='mp3'):
        """
        Converte para formato específico
        Args:
            input_path (str): Arquivo original
            target_format (str): Formato desejado (mp3, wav, flac)
        Returns:
            str: Caminho do arquivo convertido
        """
        try:
            input_file = Path(input_path)
            output_filename = f"{input_file.stem}_converted.{target_format}"
            output_path = self.output_dir / output_filename
            
            print(f"🔄 Convertendo para {target_format.upper()}...")
            
            stream = ffmpeg.input(str(input_file))
            
            if target_format == 'mp3':
                stream = ffmpeg.output(
                    stream, str(output_path),
                    acodec='mp3', audio_bitrate='128k',
                    loglevel='error'
                )
            elif target_format == 'wav':
                stream = ffmpeg.output(
                    stream, str(output_path),
                    acodec='pcm_s16le', ar=16000, ac=1,
                    loglevel='error'
                )
            elif target_format == 'flac':
                stream = ffmpeg.output(
                    stream, str(output_path),
                    acodec='flac',
                    loglevel='error'
                )
            
            ffmpeg.run(stream, overwrite_output=True, quiet=True)
            
            if output_path.exists():
                print(f"✅ Conversão para {target_format.upper()} concluída!")
                return str(output_path)
            else:
                return str(input_path)
                
        except Exception as e:
            print(f"❌ Erro na conversão: {e}")
            return str(input_path)