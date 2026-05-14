class Endereco:
    def __init__(self, logradouro: str, numero: str, complemento: str, bairro: str, cidade: str, estado: str, cep: str):
        self.logradouro = logradouro
        self.numero = numero
        self.complemento = complemento
        self.bairro = bairro
        self.cidade = cidade
        self.estado = estado
        self.cep = cep

    def validar(self):
        if not self.logradouro or not str(self.logradouro).strip():
            raise ValueError("Logradouro da parte não pode ser vazio.")
        if not self.numero or not str(self.numero).strip():
            raise ValueError("Número da parte não pode ser vazio.")
        if not self.bairro or not str(self.bairro).strip():
            raise ValueError("Bairro da parte não pode ser vazio.")
        if not self.cidade or not str(self.cidade).strip():
            raise ValueError("Cidade da parte não pode ser vazio.")
        if not self.estado or not str(self.estado).strip():
            raise ValueError("Estado da parte não pode ser vazio.")
        if not self.cep or not str(self.cep).replace("-", "").strip().isdigit() or len(str(self.cep).replace("-", "").strip()) != 8:
            raise ValueError("CEP da parte deve ser um número de 8 dígitos.")
            
    def endereco_completo(self):
        endereco = f"{self.logradouro}, {self.numero}, {self.bairro}, {self.cidade} - {self.estado}, {self.cep}"
        if self.complemento:
            endereco += f" - {self.complemento}"
        return endereco

class Parte:
    def __init__(self, name: str, document: str, type: str, endereco: Endereco, email: str):
        self.name = name
        self.document = document
        self.type = type
        self.endereco = endereco
        self.email = email
        
    def validar(self):
        if not self.name or not str(self.name).strip():
            raise ValueError("Nome da parte não pode ser vazio.")
        
        doc_clean = "".join(filter(str.isdigit, str(self.document)))
        if not doc_clean or len(doc_clean) not in (11, 14):
            raise ValueError("Documento da parte deve ser um CPF (11 dígitos) ou CNPJ (14 dígitos).")
            
        if not self.type or not str(self.type).strip():
            raise ValueError("Tipo da parte não pode ser vazio.")
        if not self.endereco:
            raise ValueError("Endereço da parte não pode ser vazio.")
        if not self.email or not str(self.email).strip() or "@" not in str(self.email):
            raise ValueError("Email da parte é inválido.")
        
    def qualificacao(self):
        return f"{self.name}, inscrito no CPF/CNPJ {self.document}, doravante denominado {self.type}, residente/sediado em {self.endereco.endereco_completo()}, com endereço eletrônico {self.email}."
