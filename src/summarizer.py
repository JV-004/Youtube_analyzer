"""
Arquivo: summarizer.py 
Função: Gera resumos estruturados usando Google Gemini com suporte a idiomas
"""

import google.generativeai as genai
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

class TextSummarizer:
    def __init__(self, api_key=None, model='gemini-1.5-flash'):
        """
        Inicializa o gerador de resumos com Gemini
        Args:
            api_key (str): Chave da API Google
            model (str): Modelo Gemini a usar
        """
        if api_key:
            self.api_key = api_key
        else:
            self.api_key = os.getenv('GOOGLE_API_KEY')
        
        if not self.api_key:
            raise ValueError("❌ API Key do Google não fornecida")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(model)
        self.model_name = model
        
        print(f"🤖 Modelo Gemini configurado: {self.model_name}")
    
    def create_summary(self, text, summary_type='structured', target_language=None):
        """
        Gera resumo do texto usando Gemini
        Args:
            text (str): Texto para resumir
            summary_type (str): Tipo de resumo
            target_language (str): Idioma desejado para o resumo
        Returns:
            dict: Resultado do resumo
        """
        try:
            if len(text.strip()) < 50:
                print("⚠️ Texto muito curto para resumir")
                return None
            
            print(f"📝 Gerando resumo com Gemini...")
            print(f"📏 Tamanho do texto: {len(text)} caracteres")
            print(f"🎯 Tipo de resumo: {summary_type}")
            if target_language:
                print(f"🌐 Idioma do resumo: {target_language}")
            
            # Seleciona prompt baseado no tipo e idioma
            system_prompt = self._get_system_prompt(summary_type, target_language)
            
            # Limita tamanho do texto
            max_chars = 30000  # Gemini suporta mais tokens
            if len(text) > max_chars:
                text = text[:max_chars] + "\n\n[...texto truncado...]"
                print(f"⚠️ Texto truncado para {max_chars} caracteres")
            
            # Combina prompt e texto
            full_prompt = f"{system_prompt}\n\nTexto para resumir:\n\n{text}"
            
            print("🔄 Processando com Gemini...")
            
            # Gera resumo
            response = self.model.generate_content(full_prompt)
            summary = response.text
            
            result = {
                'summary': summary,
                'original_length': len(text),
                'summary_length': len(summary),
                'compression_ratio': len(summary) / len(text),
                'model_used': self.model_name,
                'summary_type': summary_type,
                'target_language': target_language or 'original'
            }
            
            print("✅ Resumo gerado com sucesso!")
            print(f"📊 Taxa de compressão: {result['compression_ratio']:.2%}")
            
            return result
            
        except Exception as e:
            print(f"❌ Erro ao gerar resumo: {e}")
            return None
    
    def _get_system_prompt(self, summary_type, target_language):
        """
        Retorna prompt baseado no tipo de resumo e idioma
        """
        # Instruções de idioma
        lang_instruction = ""
        if target_language:
            lang_names = {
                'pt': 'português brasileiro',
                'en': 'inglês',
                'es': 'espanhol',
                'fr': 'francês'
            }
            lang_name = lang_names.get(target_language, target_language)
            lang_instruction = f"\n\n**IMPORTANTE: Gere todo o resumo em {lang_name}, independente do idioma do texto original.**"
        
        prompts = {
            'structured': f"""
Você é um especialista em análise de conteúdo. Crie um resumo estruturado e organizado do texto fornecido.{lang_instruction}

Formato desejado:
## 🎯 Resumo Executivo
[Resumo em 2-3 frases do conteúdo principal]

## 📋 Principais Tópicos
- [Tópico 1 com breve descrição]
- [Tópico 2 com breve descrição]
- [Tópico 3 com breve descrição]

## 💡 Insights Importantes
- [Insight ou informação relevante 1]
- [Insight ou informação relevante 2]

## 🎯 Conclusões
[Principais conclusões do conteúdo]

Seja conciso, objetivo e mantenha as informações mais importantes.
            """,
            
            'bullet_points': f"""
Crie um resumo em tópicos do texto fornecido. Use bullet points claros e concisos.{lang_instruction}
Organize as informações em ordem de importância.
Máximo de 10 bullet points.
Cada ponto deve ser autocontido e informativo.
            """,
            
            'paragraph': f"""
Crie um resumo em formato de parágrafo do texto fornecido.{lang_instruction}
O resumo deve ter entre 150-300 palavras.
Mantenha as informações mais importantes e preserve o contexto.
Use linguagem clara e objetiva.
            """
        }
        
        return prompts.get(summary_type, prompts['structured'])
    
    def analyze_content(self, text, target_language=None):
        """
        Análise avançada do conteúdo com suporte a idioma
        """
        try:
            # Instrução de idioma
            lang_instruction = ""
            if target_language:
                lang_names = {
                    'pt': 'português brasileiro',
                    'en': 'inglês',
                    'es': 'espanhol',
                    'fr': 'francês'
                }
                lang_name = lang_names.get(target_language, target_language)
                lang_instruction = f"\n\n**IMPORTANTE: Gere toda a análise em {lang_name}.**"
            
            system_prompt = f"""
Analise o conteúdo fornecido e retorne uma análise estruturada:{lang_instruction}

## 📂 Categoria
[Categoria do conteúdo: educacional, entretenimento, negócios, tecnologia, etc.]

## 🎯 Público-Alvo
[Para quem o conteúdo é direcionado]

## 📊 Tom/Sentimento
[Tom do conteúdo: formal, informal, técnico, didático, etc.]

## ⏱️ Tempo Estimado de Leitura
[Estimativa de tempo para ler o conteúdo original]

## 🔍 Palavras-Chave
[5-7 palavras-chave principais]

## 📈 Nível de Complexidade
[Básico, Intermediário ou Avançado]
            """
            
            prompt = f"{system_prompt}\n\nConteúdo para analisar:\n\n{text[:5000]}"
            
            response = self.model.generate_content(prompt)
            analysis = response.text
            
            return {
                'analysis': analysis,
                'model_used': self.model_name,
                'target_language': target_language or 'original'
            }
            
        except Exception as e:
            print(f"❌ Erro na análise: {e}")
            return None
    
    def save_summary(self, summary_data, output_path, include_analysis=False):
        """
        Salva resumo em arquivo
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("# 📋 RESUMO GERADO POR IA - GOOGLE GEMINI\n\n")
                f.write(f"**Modelo usado:** {summary_data.get('model_used', 'N/A')}\n")
                f.write(f"**Tipo de resumo:** {summary_data.get('summary_type', 'N/A')}\n")
                f.write(f"**Idioma do resumo:** {summary_data.get('target_language', 'original')}\n")
                f.write(f"**Taxa de compressão:** {summary_data.get('compression_ratio', 0):.1%}\n")
                f.write(f"**Tamanho original:** {summary_data.get('original_length', 0)} caracteres\n")
                f.write(f"**Tamanho do resumo:** {summary_data.get('summary_length', 0)} caracteres\n\n")
                f.write("---\n\n")
                f.write(summary_data['summary'])
                
                if include_analysis and 'analysis' in summary_data:
                    f.write("\n\n---\n\n")
                    f.write("# 🔍 ANÁLISE DETALHADA\n\n")
                    f.write(summary_data['analysis'])
            
            print(f"💾 Resumo salvo em: {output_path}")
            return True
        except Exception as e:
            print(f"❌ Erro ao salvar resumo: {e}")
            return False