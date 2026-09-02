"""Geração do PDF do contrato.

O layout é o do documento jurídico impresso: corpo em serifada justificada,
títulos de cláusula em condensada caixa-alta, e hierarquia dada por recuo e
espaçamento — caput na margem, desdobramentos e itens recuados, e mais ar
entre cláusulas do que entre parágrafos da mesma cláusula.

As fontes são embutidas (`../assets/fonts`, ambas SIL OFL) porque as fontes
core do PDF não cobrem os acentuados do português.
"""

import os

from fpdf import FPDF
from fpdf.enums import XPos, YPos

from ..models.formatters import data_por_extenso
from .base import GeradorBase, rotulo_tipo

PASTA_FONTES = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "assets", "fonts")
)

TITULOS = "Barlow"
CORPO = "SourceSerif"

FONTES = [
    (TITULOS, "", "BarlowCondensed-Regular.ttf"),
    (TITULOS, "B", "BarlowCondensed-SemiBold.ttf"),
    (CORPO, "", "SourceSerif4-Regular.ttf"),
    (CORPO, "B", "SourceSerif4-Bold.ttf"),
    (CORPO, "I", "SourceSerif4-It.ttf"),
]

# Margens em mm, na ordem topo/direita/base/esquerda.
MARGEM_TOPO, MARGEM_DIREITA, MARGEM_BASE, MARGEM_ESQUERDA = 25, 20, 25, 20

CORPO_PT = 11
# Entrelinha de ~1.45: 11pt valem 3.88mm, e a linha do corpo fica em 5.6mm.
ALTURA_LINHA = 5.6
# Recuo de um nível de hierarquia.
RECUO = 8
# Espaço reservado ao rótulo do item, com 2 mm de folga antes do texto: o
# rótulo é alinhado à direita para "i.", "ii." e "iii." abrirem o texto na
# mesma coluna.
LARGURA_ROTULO = 9
FOLGA_ROTULO = 2
ESPACO_ENTRE_PARAGRAFOS = 2.0
ESPACO_ENTRE_CLAUSULAS = 6.0

PREAMBULO = (
    "As partes acima identificadas têm, entre si, justo e acertado o presente "
    "Contrato, que se regerá pelas cláusulas e condições a seguir descritas."
)


class _Documento(FPDF):
    """FPDF com o rodapé de paginação em todas as páginas."""

    def footer(self) -> None:
        self.set_y(-(MARGEM_BASE - 10))
        self.set_font(CORPO, size=8)
        self.set_text_color(130, 130, 130)
        self.cell(0, 6, f"Página {self.page_no()} de {{nb}}", align="C")
        self.set_text_color(0, 0, 0)


class PdfGenerator(GeradorBase):
    def gerar(self, contrato, caminho_saida: str) -> str:
        caminho = self._preparar_caminho(caminho_saida, "pdf")

        pdf = _Documento(format="A4")
        self._registrar_fontes(pdf)
        pdf.set_margins(left=MARGEM_ESQUERDA, top=MARGEM_TOPO,
                        right=MARGEM_DIREITA)
        pdf.set_auto_page_break(auto=True, margin=MARGEM_BASE)
        pdf.alias_nb_pages()
        pdf.add_page()

        dados = contrato.to_dict()
        self._titulo(pdf, contrato)
        self._qualificacao(pdf, contrato)
        self._clausulas(pdf, contrato, dados)
        self._fecho(pdf, contrato, dados)

        pdf.output(caminho)
        return caminho

    # --- Infraestrutura ----------------------------------------------------

    def _registrar_fontes(self, pdf: FPDF) -> None:
        for familia, estilo, arquivo in FONTES:
            pdf.add_font(familia, style=estilo,
                         fname=os.path.join(PASTA_FONTES, arquivo))

    def _largura_util(self, pdf: FPDF, recuo: float = 0) -> float:
        return pdf.w - MARGEM_ESQUERDA - MARGEM_DIREITA - recuo

    def _paragrafo(self, pdf: FPDF, texto: str, recuo: float = 0,
                   rotulo: str = "", largura_rotulo: float = 0,
                   align: str = "J", markdown: bool = False) -> None:
        """Escreve um parágrafo justificado, recuado e com rótulo opcional.

        O rótulo (`i.`, `a)`) fica pendurado à esquerda e o texto alinha em
        bloco à direita dele, inclusive nas linhas seguintes — daí mexer na
        margem esquerda em vez de só no `x`.
        """
        esquerda = MARGEM_ESQUERDA + recuo
        if rotulo:
            pdf.set_xy(esquerda, pdf.get_y())
            pdf.cell(largura_rotulo - FOLGA_ROTULO, ALTURA_LINHA, rotulo,
                     align="R", new_x=XPos.LEFT, new_y=YPos.TOP)
            esquerda += largura_rotulo

        pdf.set_left_margin(esquerda)
        pdf.set_x(esquerda)
        pdf.multi_cell(pdf.w - esquerda - MARGEM_DIREITA, ALTURA_LINHA, texto,
                       align=align, markdown=markdown)
        pdf.set_left_margin(MARGEM_ESQUERDA)

    # --- Blocos do documento -----------------------------------------------

    def _titulo(self, pdf: FPDF, contrato) -> None:
        """Título centralizado — só na primeira página."""
        pdf.set_font(TITULOS, style="B", size=20)
        pdf.set_char_spacing(1.2)
        pdf.set_x(MARGEM_ESQUERDA)
        pdf.multi_cell(self._largura_util(pdf), 9,
                       f"CONTRATO DE {rotulo_tipo(contrato.tipo)}", align="C")
        pdf.set_char_spacing(0)
        pdf.ln(8)

    def _qualificacao(self, pdf: FPDF, contrato) -> None:
        pdf.set_font(CORPO, size=CORPO_PT)
        for papel, parte in (("CONTRATANTE", contrato.contratante),
                             ("CONTRATADO", contrato.contratado)):
            self._paragrafo(pdf, f"**{papel}**: {parte.qualificacao()}",
                            markdown=True)
            pdf.ln(ESPACO_ENTRE_PARAGRAFOS)

        pdf.ln(ESPACO_ENTRE_PARAGRAFOS)
        self._paragrafo(pdf, PREAMBULO)
        pdf.ln(ESPACO_ENTRE_CLAUSULAS)

    def _clausulas(self, pdf: FPDF, contrato, dados: dict) -> None:
        for indice, clausula in enumerate(contrato.clausulas):
            if indice:
                pdf.ln(ESPACO_ENTRE_CLAUSULAS)

            pdf.set_font(TITULOS, style="B", size=12.5)
            pdf.set_char_spacing(1.0)
            self._paragrafo(pdf, clausula.cabecalho(), align="L")
            pdf.set_char_spacing(0)
            pdf.ln(1.5)

            pdf.set_font(CORPO, size=CORPO_PT)
            self._paragrafo(pdf, clausula.caput(dados))

            for rotulo, texto, subitens in clausula.itens_formatados(dados):
                pdf.ln(ESPACO_ENTRE_PARAGRAFOS)
                self._paragrafo(pdf, texto, recuo=RECUO, rotulo=rotulo,
                                largura_rotulo=LARGURA_ROTULO)
                for sub_rotulo, sub_texto in subitens:
                    pdf.ln(1.0)
                    self._paragrafo(pdf, sub_texto, recuo=RECUO * 2,
                                    rotulo=sub_rotulo,
                                    largura_rotulo=LARGURA_ROTULO)

            for texto in clausula.desdobramentos_formatados(dados):
                pdf.ln(ESPACO_ENTRE_PARAGRAFOS)
                self._paragrafo(pdf, texto, recuo=RECUO)

    def _fecho(self, pdf: FPDF, contrato, dados: dict) -> None:
        """Local e data por extenso, seguidos das duas assinaturas."""
        # O bloco de assinatura não pode ficar órfão numa página só dele nem
        # partido ao meio: se não couber inteiro, começa na página seguinte.
        if pdf.get_y() + 55 > pdf.h - MARGEM_BASE:
            pdf.add_page()
        else:
            pdf.ln(ESPACO_ENTRE_CLAUSULAS * 2)

        cidade = dados["contratado_cidade"] or dados["contratante_cidade"]
        local_e_data = data_por_extenso(contrato.data_criacao)
        if cidade:
            local_e_data = f"{cidade}, {local_e_data}"

        pdf.set_font(CORPO, size=CORPO_PT)
        self._paragrafo(pdf, local_e_data, align="R")
        pdf.ln(18)

        largura = self._largura_util(pdf)
        coluna = (largura - 12) / 2
        base_y = pdf.get_y()

        assinaturas = (
            ("CONTRATANTE", dados["contratante_nome"],
             f"{dados['contratante_tipo_documento']} "
             f"{dados['contratante_documento']}"),
            ("CONTRATADO", dados["contratado_nome"],
             f"{dados['contratado_tipo_documento']} "
             f"{dados['contratado_documento']}"),
        )
        for indice, (papel, nome, documento) in enumerate(assinaturas):
            x = MARGEM_ESQUERDA + indice * (coluna + 12)

            pdf.set_draw_color(60, 60, 60)
            pdf.line(x, base_y, x + coluna, base_y)

            pdf.set_xy(x, base_y + 1.5)
            pdf.set_font(CORPO, size=10.5)
            pdf.cell(coluna, 5.5, nome, align="C",
                     new_x=XPos.LEFT, new_y=YPos.NEXT)

            pdf.set_x(x)
            pdf.set_font(CORPO, size=9.5)
            pdf.set_text_color(90, 90, 90)
            pdf.cell(coluna, 5, documento, align="C",
                     new_x=XPos.LEFT, new_y=YPos.NEXT)

            pdf.set_x(x)
            pdf.set_font(TITULOS, style="B", size=9)
            pdf.set_char_spacing(0.6)
            pdf.cell(coluna, 5, papel, align="C")
            pdf.set_char_spacing(0)
            pdf.set_text_color(0, 0, 0)
