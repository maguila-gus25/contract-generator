from .template import ler_template


class Clausula:
    """Representa uma cláusula individual de um contrato."""

    def __init__(self, numero: int, titulo: str, conteudo: str, obrigatoria: bool = True):
        self.numero = numero
        self.titulo = titulo
        self.conteudo = conteudo
        self.obrigatoria = obrigatoria
        self.validar()

    def validar(self) -> None:
        """Verifica se os dados da cláusula estão corretos."""
        if not isinstance(self.numero, int) or self.numero <= 0:
            raise ValueError("Número da cláusula deve ser um inteiro positivo.")
        if not self.titulo or not self.titulo.strip():
            raise ValueError("Título da cláusula não pode ser vazio.")
        if not self.conteudo or not self.conteudo.strip():
            raise ValueError("Conteúdo da cláusula não pode ser vazio.")

    def formatada(self) -> str:
        """Retorna a cláusula como string pronta para inserir no documento.

        Exemplo de retorno:
            CLÁUSULA 1ª - DO OBJETO

            O CONTRATADO se compromete a...
        """
        ordinal = f"{self.numero}ª"
        cabecalho = f"CLÁUSULA {ordinal} - {self.titulo.upper()}"
        return f"{cabecalho}\n\n{self.conteudo}"

    def __repr__(self) -> str:
        return f"Clausula(numero={self.numero}, titulo={self.titulo!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Clausula):
            return False
        return self.numero == other.numero and self.titulo == other.titulo


def carregar_clausulas_padrao(tipo_contrato: str) -> list:
    """Lê o template do tipo de contrato e retorna lista de objetos Clausula.

    Args:
        tipo_contrato: nome do tipo, ex: "servico", "locacao" ou "fotografia"

    Returns:
        Lista de objetos Clausula carregados do template.

    Raises:
        FileNotFoundError: se o template não existir para o tipo informado.
        ValueError: se o JSON do template estiver mal formatado.
    """
    clausulas = []
    for item in ler_template(tipo_contrato)["clausulas"]:
        clausulas.append(Clausula(
            numero=item["numero"],
            titulo=item["titulo"],
            conteudo=item["conteudo"],
            obrigatoria=item.get("obrigatoria", True),
        ))
    return clausulas
