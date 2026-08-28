"""Leitura dos templates de contrato e dos campos que eles parametrizam.

Um template é um JSON em ``contract_generator/templates/<tipo>.json``. Aceita
dois formatos:

- lista de cláusulas (formato original);
- objeto com ``campos`` (parâmetros extras do tipo) e ``clausulas``.

Os ``campos`` descrevem valores que variam de contrato para contrato mas não
existem no formulário padrão — horas de trabalho, entrada, prazos, multas.
Cada um vira um input no formulário e um placeholder disponível para as
cláusulas daquele tipo.
"""

import json
import os

from .formatters import formatar_moeda, formatar_percentual

PASTA_TEMPLATES = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "templates")
)

TIPOS_DE_CAMPO = ("texto", "numero", "inteiro", "moeda", "percentual")


class CampoExtra:
    """Parâmetro declarado por um template de contrato."""

    def __init__(self, nome: str, label: str, tipo: str = "texto",
                 padrao: str = "", ajuda: str = "", obrigatorio: bool = True,
                 padrao_de: str = ""):
        self.nome = nome
        self.label = label
        self.tipo = tipo
        self.padrao = padrao
        self.ajuda = ajuda
        self.obrigatorio = obrigatorio
        # Nome de um campo do formulário padrão (ex: "contratante_cidade")
        # aproveitado quando o usuário deixa este campo em branco.
        self.padrao_de = padrao_de
        self.validar()

    def validar(self) -> None:
        if not self.nome or not self.nome.strip():
            raise ValueError("Campo extra precisa de um nome.")
        if not self.label or not self.label.strip():
            raise ValueError(f"Campo extra '{self.nome}' precisa de um label.")
        if self.tipo not in TIPOS_DE_CAMPO:
            raise ValueError(
                f"Tipo '{self.tipo}' inválido para o campo '{self.nome}'. "
                f"Tipos aceitos: {', '.join(TIPOS_DE_CAMPO)}"
            )

    def formatar(self, valor) -> str:
        """Converte o valor cru do formulário no texto que vai na cláusula."""
        if valor is None or str(valor).strip() == "":
            return ""
        try:
            if self.tipo == "moeda":
                return formatar_moeda(valor)
            if self.tipo == "percentual":
                return formatar_percentual(valor)
            if self.tipo == "inteiro":
                return str(int(float(valor)))
        except (TypeError, ValueError):
            # Valor não numérico num campo numérico: preserva o que veio para
            # não engolir o dado do usuário no meio do contrato.
            return str(valor).strip()
        return str(valor).strip()

    def to_dict(self) -> dict:
        return {
            "nome": self.nome,
            "label": self.label,
            "tipo": self.tipo,
            "padrao": self.padrao,
            "ajuda": self.ajuda,
            "obrigatorio": self.obrigatorio,
            "padrao_de": self.padrao_de,
        }

    def __repr__(self) -> str:
        return f"CampoExtra(nome={self.nome!r}, tipo={self.tipo!r})"


def caminho_do_template(tipo_contrato: str) -> str:
    return os.path.normpath(
        os.path.join(PASTA_TEMPLATES, f"{tipo_contrato}.json")
    )


def listar_tipos_disponiveis() -> list:
    """Retorna os tipos de contrato com template cadastrado."""
    if not os.path.exists(PASTA_TEMPLATES):
        return []
    return sorted(
        os.path.splitext(f)[0]
        for f in os.listdir(PASTA_TEMPLATES)
        if f.endswith(".json")
    )


def ler_template(tipo_contrato: str) -> dict:
    """Lê o JSON do tipo e devolve sempre ``{"campos": [...], "clausulas": [...]}``.

    Raises:
        FileNotFoundError: se não existir template para o tipo informado.
        ValueError: se o JSON estiver mal formatado.
    """
    caminho = caminho_do_template(tipo_contrato)
    if not os.path.exists(caminho):
        raise FileNotFoundError(
            f"Template '{tipo_contrato}' não encontrado. "
            f"Tipos disponíveis: {listar_tipos_disponiveis()}"
        )

    with open(caminho, encoding="utf-8") as arquivo:
        try:
            dados = json.load(arquivo)
        except json.JSONDecodeError as e:
            raise ValueError(f"Erro ao ler o template '{tipo_contrato}': {e}")

    if isinstance(dados, list):
        return {"campos": [], "clausulas": dados}
    return {
        "campos": dados.get("campos", []),
        "clausulas": dados.get("clausulas", []),
    }


def carregar_campos_extras(tipo_contrato: str) -> list:
    """Retorna os CampoExtra declarados pelo template do tipo."""
    return [CampoExtra(**item) for item in ler_template(tipo_contrato)["campos"]]


def campos_extras_por_tipo() -> dict:
    """Mapa ``{tipo: [campo.to_dict(), ...]}`` para todos os tipos.

    Usado pelo formulário para montar os campos de cada tipo no navegador.
    """
    mapa = {}
    for tipo in listar_tipos_disponiveis():
        mapa[tipo] = [campo.to_dict() for campo in carregar_campos_extras(tipo)]
    return mapa
