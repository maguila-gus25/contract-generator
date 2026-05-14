import requests

def buscar_cnpj(cnpj: str) -> dict:
    """
    Busca os dados de uma empresa pelo CNPJ usando a BrasilAPI.
    """
    cnpj_limpo = "".join(filter(str.isdigit, cnpj))
    if len(cnpj_limpo) != 14:
        raise ValueError("CNPJ deve conter 14 dígitos.")
        
    url = f"https://brasilapi.com.br/api/cnpj/v1/{cnpj_limpo}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 404:
            raise ValueError("CNPJ não encontrado.")
            
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
    except requests.RequestException as e:
        raise ConnectionError(f"Erro ao buscar CNPJ: {str(e)}")
