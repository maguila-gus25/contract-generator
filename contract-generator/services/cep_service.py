import requests

def buscar_cep(cep: str) -> dict:
    """
    Busca o endereço a partir do CEP usando a API ViaCEP.
    """
    cep_limpo = "".join(filter(str.isdigit, cep))
    if len(cep_limpo) != 8:
        raise ValueError("CEP deve conter 8 dígitos.")
        
    url = f"https://viacep.com.br/ws/{cep_limpo}/json/"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if "erro" in data:
            raise ValueError("CEP não encontrado.")
            
        return {
            "logradouro": data.get("logradouro", ""),
            "bairro": data.get("bairro", ""),
            "cidade": data.get("localidade", ""),
            "estado": data.get("uf", ""),
            "cep": data.get("cep", "")
        }
    except requests.RequestException as e:
        raise ConnectionError(f"Erro ao buscar CEP: {str(e)}")
