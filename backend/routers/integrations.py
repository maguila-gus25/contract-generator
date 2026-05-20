from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from .. import database, auth, models
import httpx
import re

router = APIRouter(
    prefix="/integrations",
    tags=["integrations"],
    dependencies=[Depends(auth.get_current_user)]
)

@router.get("/cep/{cep}")
async def get_cep(cep: str):
    cep_limpo = re.sub(r"\D", "", cep)
    if len(cep_limpo) != 8:
        raise HTTPException(status_code=400, detail="CEP inválido. Deve conter 8 dígitos.")
    
    url = f"https://viacep.com.br/ws/{cep_limpo}/json/"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=10.0)
            response.raise_for_status()
            data = response.json()
            
            if "erro" in data:
                raise HTTPException(status_code=404, detail="CEP não encontrado.")
                
            return {
                "logradouro": data.get("logradouro", ""),
                "bairro": data.get("bairro", ""),
                "cidade": data.get("localidade", ""),
                "estado": data.get("uf", ""),
                "cep": data.get("cep", "")
            }
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"Erro ao acessar ViaCEP: {str(e)}")

@router.get("/cnpj/{cnpj}")
async def get_cnpj(cnpj: str):
    cnpj_limpo = re.sub(r"\D", "", cnpj)
    if len(cnpj_limpo) != 14:
        raise HTTPException(status_code=400, detail="CNPJ inválido. Deve conter 14 dígitos.")
        
    url = f"https://brasilapi.com.br/api/cnpj/v1/{cnpj_limpo}"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=10.0)
            if response.status_code == 404:
                raise HTTPException(status_code=404, detail="CNPJ não encontrado.")
            response.raise_for_status()
            data = response.json()
            
            return {
                "razao_social": data.get("razao_social", ""),
                "nome_fantasia": data.get("nome_fantasia", ""),
                "logradouro": data.get("logradouro", ""),
                "numero": str(data.get("numero", "")),
                "complemento": data.get("complemento", ""),
                "bairro": data.get("bairro", ""),
                "cidade": data.get("municipio", ""),
                "estado": data.get("uf", ""),
                "cep": data.get("cep", "")
            }
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"Erro ao acessar BrasilAPI: {str(e)}")
