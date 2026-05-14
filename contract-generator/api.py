from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import os

from models.party import Endereco, Parte
from models.clause import carregar_clausulas_padrao
from models.contract import Contrato
from generators.pdf_generator import PDFGenerator
from generators.docx_generator import DocxGenerator
from services.cep_service import buscar_cep
from services.cnpj_service import buscar_cnpj
from routers import govbr

app = FastAPI(title="Gerador de Contratos API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(govbr.router)

@app.get("/api/cep/{cep}")
def get_cep(cep: str):
    try:
        dados = buscar_cep(cep)
        return dados
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/cnpj/{cnpj}")
def get_cnpj(cnpj: str):
    try:
        dados = buscar_cnpj(cnpj)
        return dados
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

class EnderecoInput(BaseModel):
    logradouro: str
    numero: str
    complemento: Optional[str] = ""
    bairro: str
    cidade: str
    estado: str
    cep: str

class ParteInput(BaseModel):
    name: str
    document: str
    type: str
    endereco: EnderecoInput
    email: str

class ContratoInput(BaseModel):
    titulo: str = "CONTRATO DE PRESTAÇÃO DE SERVIÇOS"
    contratante: ParteInput
    contratado: ParteInput
    valor: float
    moeda: str = "R$"
    metodo_pagamento: str
    tipo_contrato: str = "servico"
    formato_saida: str = "pdf" # 'pdf' ou 'docx'

@app.post("/api/gerar-contrato")
def gerar_contrato(dados: ContratoInput):
    try:
        endereco_contratante = Endereco(
            logradouro=dados.contratante.endereco.logradouro,
            numero=dados.contratante.endereco.numero,
            complemento=dados.contratante.endereco.complemento,
            bairro=dados.contratante.endereco.bairro,
            cidade=dados.contratante.endereco.cidade,
            estado=dados.contratante.endereco.estado,
            cep=dados.contratante.endereco.cep
        )
        
        endereco_contratado = Endereco(
            logradouro=dados.contratado.endereco.logradouro,
            numero=dados.contratado.endereco.numero,
            complemento=dados.contratado.endereco.complemento,
            bairro=dados.contratado.endereco.bairro,
            cidade=dados.contratado.endereco.cidade,
            estado=dados.contratado.endereco.estado,
            cep=dados.contratado.endereco.cep
        )
        
        contratante = Parte(
            name=dados.contratante.name,
            document=dados.contratante.document,
            type=dados.contratante.type,
            endereco=endereco_contratante,
            email=dados.contratante.email
        )
        
        contratado = Parte(
            name=dados.contratado.name,
            document=dados.contratado.document,
            type=dados.contratado.type,
            endereco=endereco_contratado,
            email=dados.contratado.email
        )
        
        contratante.validar()
        contratado.validar()
        
        clausulas = carregar_clausulas_padrao(dados.tipo_contrato)
        
        contrato = Contrato(
            titulo=dados.titulo,
            contratante=contratante,
            contratado=contratado,
            data_hora_criacao=datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            valor=dados.valor,
            moeda=dados.moeda,
            metodo_pagamento=dados.metodo_pagamento,
            endereco=endereco_contratante
        )
        contrato.clausulas = clausulas
        contrato.validar()
        
        output_dir = os.path.join(os.path.dirname(__file__), "output")
        os.makedirs(output_dir, exist_ok=True)
        
        if dados.formato_saida.lower() == "docx":
            file_path = os.path.join(output_dir, "contrato.docx")
            docx_gen = DocxGenerator()
            docx_gen.gerar(contrato, file_path)
            media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            filename = "contrato.docx"
        else:
            file_path = os.path.join(output_dir, "contrato.pdf")
            pdf_gen = PDFGenerator()
            pdf_gen.gerar(contrato, file_path)
            media_type = "application/pdf"
            filename = "contrato.pdf"
            
        return FileResponse(path=file_path, filename=filename, media_type=media_type)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Montar a pasta do frontend para servir os arquivos estáticos (HTML, CSS, JS) na raiz
app.mount("/", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "frontend"), html=True), name="frontend")
