import unicodedata
from fpdf import FPDF
from models.contract import Contrato
from .base import BaseGenerator

def remover_acentos(texto: str) -> str:
    return unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('ASCII')

class PDFGenerator(BaseGenerator):
    def gerar(self, contrato: Contrato, caminho_saida: str):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        
        pdf.set_font("Helvetica", style="B", size=16)
        
        texto_completo = contrato.gerar_texto_completo()
        
        for linha in texto_completo.split('\n'):
            if not linha.strip():
                pdf.ln(5)
                continue
                
            if "DO VALOR" in linha or "Firmam o presente" in linha or "Por este instrumento" in linha:
                pdf.set_font("Helvetica", style="B", size=12)
            elif linha.startswith("CLÁUSULA"):
                pdf.set_font("Helvetica", style="B", size=12)
            else:
                pdf.set_font("Helvetica", size=12)
            
            linha_limpa = remover_acentos(linha)
            try:
                pdf.write(h=8, text=linha_limpa)
                pdf.ln(8)
            except Exception as e:
                print(f"ERRO FPDF NA LINHA: {repr(linha_limpa)}")
                raise
            
        pdf.output(caminho_saida)
