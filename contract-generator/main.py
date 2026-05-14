import os
from datetime import datetime

from models.party import Endereco, Parte
from models.clause import carregar_clausulas_padrao
from models.contract import Contrato
from generators.pdf_generator import PDFGenerator
from generators.docx_generator import DocxGenerator
from services.cep_service import buscar_cep
from services.cnpj_service import buscar_cnpj

def main():
    print("--- Gerador de Contratos Automático ---")
    
    # 1. Obter dados via API (Exemplo com serviços)
    print("\n[1] Buscando endereço do Contratante pelo CEP...")
    cep_dados = buscar_cep("01001-000") # Praça da Sé, SP
    endereco_contratante = Endereco(
        logradouro=cep_dados['logradouro'],
        numero="100",
        complemento="Sala 2",
        bairro=cep_dados['bairro'],
        cidade=cep_dados['cidade'],
        estado=cep_dados['estado'],
        cep=cep_dados['cep']
    )
    
    print("[2] Buscando dados do Contratado pelo CNPJ...")
    # Usando CNPJ do Google Brasil como exemplo válido
    cnpj_dados = buscar_cnpj("06990590000123") 
    endereco_contratado = Endereco(
        logradouro=cnpj_dados['logradouro'],
        numero=cnpj_dados['numero'],
        complemento=cnpj_dados['complemento'],
        bairro=cnpj_dados['bairro'],
        cidade=cnpj_dados['cidade'],
        estado=cnpj_dados['estado'],
        cep=cnpj_dados['cep']
    )
    
    # 2. Criar as Partes
    contratante = Parte(
        name="João da Silva",
        document="12345678901", # CPF fictício
        type="CONTRATANTE",
        endereco=endereco_contratante,
        email="joao@email.com"
    )
    
    contratado = Parte(
        name=cnpj_dados['razao_social'],
        document="06990590000123",
        type="CONTRATADA",
        endereco=endereco_contratado,
        email="contato@google.com"
    )
    
    # Valida as partes
    contratante.validar()
    contratado.validar()
    print("[+] Partes criadas e validadas com sucesso.")
    
    # 3. Carregar Cláusulas do Template
    tipo_contrato = "servico"
    print(f"\n[3] Carregando cláusulas do template '{tipo_contrato}'...")
    clausulas = carregar_clausulas_padrao(tipo_contrato)
    
    # 4. Criar o Contrato
    contrato = Contrato(
        titulo="CONTRATO DE PRESTAÇÃO DE SERVIÇOS",
        contratante=contratante,
        contratado=contratado,
        data_hora_criacao=datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        valor=15000.00,
        moeda="R$",
        metodo_pagamento="Transferência Bancária (PIX)",
        endereco=endereco_contratante # Endereço do foro
    )
    contrato.clausulas = clausulas
    contrato.validar()
    print("[+] Contrato montado e validado.")
    
    # 5. Gerar Documentos
    print("\n[4] Gerando arquivos do contrato...")
    
    # Cria pasta output se não existir
    output_dir = os.path.join(os.path.dirname(__file__), "output")
    os.makedirs(output_dir, exist_ok=True)
    
    # Gerar PDF
    pdf_path = os.path.join(output_dir, "contrato.pdf")
    pdf_gen = PDFGenerator()
    pdf_gen.gerar(contrato, pdf_path)
    print(f"[+] PDF gerado em: {pdf_path}")
    
    # Gerar DOCX
    docx_path = os.path.join(output_dir, "contrato.docx")
    docx_gen = DocxGenerator()
    docx_gen.gerar(contrato, docx_path)
    print(f"[+] DOCX gerado em: {docx_path}")
    
    print("\nSucesso! Processo finalizado.")

if __name__ == "__main__":
    main()
