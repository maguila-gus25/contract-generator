from .template import ler_template


ROMANOS = [(1000, "M"), (900, "CM"), (500, "D"), (400, "CD"), (100, "C"),
           (90, "XC"), (50, "L"), (40, "XL"), (10, "X"), (9, "IX"),
           (5, "V"), (4, "IV"), (1, "I")]


def romano(numero: int) -> str:
    """Converte um inteiro positivo em algarismo romano: 4 -> 'IV'."""
    if numero <= 0:
        raise ValueError("Só há algarismo romano para inteiro positivo.")
    saida = []
    for valor, simbolo in ROMANOS:
        while numero >= valor:
            saida.append(simbolo)
            numero -= valor
    return "".join(saida)


def letra(indice: int) -> str:
    """Rótulo de subitem a partir do índice zero-based: 0 -> 'a'."""
    return chr(ord("a") + indice)


class Item:
    """Item enumerado de uma cláusula, com no máximo um nível de subitens.

    A numeração não fica no texto: o primeiro nível é romano minúsculo e o
    segundo, letra — o gerador é quem monta o rótulo, então reordenar os
    itens no JSON não deixa a numeração para trás.
    """

    def __init__(self, texto: str, subitens: list = None):
        self.texto = texto
        self.subitens = list(subitens or [])
        self.validar()

    def validar(self) -> None:
        if not self.texto or not str(self.texto).strip():
            raise ValueError("Item de cláusula não pode ter texto vazio.")
        for subitem in self.subitens:
            if not isinstance(subitem, str) or not subitem.strip():
                raise ValueError("Subitem de cláusula não pode ser vazio.")

    def rotulo(self, indice: int) -> str:
        return romano(indice + 1).lower()

    def __repr__(self) -> str:
        return f"Item(texto={self.texto[:30]!r}, subitens={len(self.subitens)})"


class Clausula:
    """Representa uma cláusula individual de um contrato."""

    def __init__(self, numero: int, titulo: str, conteudo: str,
                 obrigatoria: bool = True, itens: list = None,
                 desdobramentos: list = None):
        self.numero = numero
        self.titulo = titulo
        self.conteudo = conteudo
        self.obrigatoria = obrigatoria
        # Enumeração opcional, entre o caput e os desdobramentos.
        self.itens = [i if isinstance(i, Item) else Item(**i)
                      for i in (itens or [])]
        # Prosa que vem depois: os "Parágrafo primeiro:" do contrato original
        # continuam sendo texto corrido, não viram itens. O gerador os recua
        # em relação ao caput.
        self.desdobramentos = list(desdobramentos or [])
        self.validar()

    def validar(self) -> None:
        """Verifica se os dados da cláusula estão corretos."""
        if not isinstance(self.numero, int) or self.numero <= 0:
            raise ValueError("Número da cláusula deve ser um inteiro positivo.")
        if not self.titulo or not self.titulo.strip():
            raise ValueError("Título da cláusula não pode ser vazio.")
        if not self.conteudo or not self.conteudo.strip():
            raise ValueError("Conteúdo da cláusula não pode ser vazio.")

    def cabecalho(self) -> str:
        """`CLÁUSULA VI – DAS HIPÓTESES DE CANCELAMENTO`."""
        return f"CLÁUSULA {romano(self.numero)} – {self.titulo.upper()}"

    def caput(self, dados: dict = None) -> str:
        """O parágrafo de abertura da cláusula, já interpolado."""
        return self._interpolar(self.conteudo, dados)

    def desdobramentos_formatados(self, dados: dict = None) -> list:
        """Os parágrafos que vêm depois do caput e dos itens, interpolados."""
        return [self._interpolar(texto, dados)
                for texto in self.desdobramentos if texto and texto.strip()]

    def itens_formatados(self, dados: dict = None) -> list:
        """Itens como ``(rótulo, texto, [(rótulo, texto), ...])``.

        O rótulo é calculado aqui — romano minúsculo no primeiro nível, letra
        no segundo — para os geradores não repetirem a regra de numeração.
        """
        formatados = []
        for indice, item in enumerate(self.itens):
            subitens = [(f"{letra(pos)})", self._interpolar(texto, dados))
                        for pos, texto in enumerate(item.subitens)]
            formatados.append((f"{item.rotulo(indice)}.",
                               self._interpolar(item.texto, dados), subitens))
        return formatados

    @staticmethod
    def _interpolar(texto: str, dados: dict = None) -> str:
        if not dados:
            return texto
        try:
            return texto.format(**dados)
        except (KeyError, IndexError):
            # Um placeholder sem origem sai cru, mas não derruba o documento.
            return texto

    def formatada(self) -> str:
        """Retorna a cláusula como string pronta para inserir no documento."""
        linhas = [self.cabecalho(), "", self.conteudo]
        for rotulo, texto, subitens in self.itens_formatados():
            linhas.append(f"{rotulo} {texto}")
            linhas.extend(f"    {sub_rotulo} {sub_texto}"
                          for sub_rotulo, sub_texto in subitens)
        linhas.extend(self.desdobramentos)
        return "\n".join(linhas)

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
            itens=item.get("itens", []),
            desdobramentos=item.get("desdobramentos", []),
        ))
    return clausulas
