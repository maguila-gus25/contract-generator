from fpdf import FPDF
from .base import GeradorBase


class PdfGenerator(GeradorBase):
    def gerar(self, contrato, caminho_saida: str) -> str:
        caminho = self._preparar_caminho(caminho_saida, "pdf")
        pdf = FPDF()
        pdf.set_margins(left=25, top=20, right=25)
        pdf.set_auto_page_break(auto=True, margin=20)
        pdf.add_page()
        self._adicionar_cabecalho(pdf, contrato)
        self._adicionar_qualificacao(pdf, contrato)
        self._adicionar_clausulas(pdf, contrato)
        self._adicionar_rodape(pdf, contrato)
        pdf.output(caminho)
        return caminho

    def _w(self, pdf: FPDF) -> float:
        return pdf.w - pdf.l_margin - pdf.r_margin

    def _linha(self, pdf: FPDF, texto: str, altura: float = 7,
               bold: bool = False, size: int = 11, align: str = "L") -> None:
        pdf.set_font("Helvetica", style="B" if bold else "", size=size)
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(self._w(pdf), altura, texto, align=align)

    def _adicionar_cabecalho(self, pdf: FPDF, contrato) -> None:
        dados = contrato.to_dict()
        tipo_label = "PRESTACAO DE SERVICOS" if contrato.tipo == "servico" else "LOCACAO DE IMOVEL"
        self._linha(pdf, f"CONTRATO DE {tipo_label}", altura=10, bold=True, size=15, align="C")
        pdf.ln(2)
        pdf.set_font("Helvetica", size=10)
        pdf.set_text_color(85, 85, 85)
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(self._w(pdf), 7,
                       f"Contrato no {dados['numero']}  |  Data: {dados['data_criacao']}",
                       align="C")
        pdf.set_text_color(0, 0, 0)
        pdf.ln(8)

    def _adicionar_qualificacao(self, pdf: FPDF, contrato) -> None:
        dados = contrato.to_dict()
        self._linha(pdf, "PARTES", bold=True, size=13)
        pdf.ln(2)

        linha_c = (f"CONTRATANTE: {dados['contratante_nome']}, "
                   f"{dados['contratante_tipo_documento']} no {dados['contratante_documento']}")
        if dados["contratante_email"]:
            linha_c += f", e-mail: {dados['contratante_email']}"
        if dados["contratante_endereco"]:
            linha_c += f", endereco: {dados['contratante_endereco']}"
        linha_c += "."
        self._linha(pdf, linha_c)
        pdf.ln(2)

        linha_cd = (f"CONTRATADO: {dados['contratado_nome']}, "
                    f"{dados['contratado_tipo_documento']} no {dados['contratado_documento']}")
        if dados["contratado_email"]:
            linha_cd += f", e-mail: {dados['contratado_email']}"
        if dados["contratado_endereco"]:
            linha_cd += f", endereco: {dados['contratado_endereco']}"
        linha_cd += "."
        self._linha(pdf, linha_cd)
        pdf.ln(4)

        self._linha(pdf,
                    "As partes acima identificadas celebram o presente contrato, "
                    "que se regera pelas clausulas e condicoes a seguir:")
        pdf.ln(6)

    def _adicionar_clausulas(self, pdf: FPDF, contrato) -> None:
        dados = contrato.to_dict()
        self._linha(pdf, "CLAUSULAS", bold=True, size=13)
        pdf.ln(2)

        for clausula in contrato.clausulas:
            conteudo = clausula.conteudo
            try:
                conteudo = conteudo.format(**dados)
            except KeyError:
                pass
            # Remove newlines from interpolated values to keep layout stable
            conteudo = conteudo.replace("\n", " ")

            self._linha(pdf, f"CLAUSULA {clausula.numero}a - {clausula.titulo.upper()}",
                        bold=True)
            self._linha(pdf, conteudo)
            pdf.ln(4)

    def _adicionar_rodape(self, pdf: FPDF, contrato) -> None:
        dados = contrato.to_dict()
        pdf.ln(4)
        pdf.set_font("Helvetica", size=10)
        pdf.set_text_color(85, 85, 85)
        pdf.set_x(pdf.l_margin)
        rodape = (f"Vigencia: {dados['data_inicio']} a {dados['data_fim']}  |  "
                  f"Valor: {dados['valor']}  |  Pagamento: {dados['forma_pagamento']}")
        pdf.multi_cell(self._w(pdf), 7, rodape, align="C")
        pdf.set_text_color(0, 0, 0)
        pdf.ln(12)

        w = self._w(pdf)
        col = (w - 10) / 2
        y = pdf.get_y()

        pdf.set_font("Helvetica", size=11)
        pdf.set_xy(pdf.l_margin, y)
        pdf.cell(col, 7, "_" * 38, align="C")
        pdf.set_xy(pdf.l_margin + col + 10, y)
        pdf.cell(col, 7, "_" * 38, align="C")

        pdf.set_xy(pdf.l_margin, y + 8)
        pdf.cell(col, 7, dados["contratante_nome"][:30], align="C")
        pdf.set_xy(pdf.l_margin + col + 10, y + 8)
        pdf.cell(col, 7, dados["contratado_nome"][:30], align="C")

        pdf.set_font("Helvetica", size=9)
        pdf.set_xy(pdf.l_margin, y + 15)
        pdf.cell(col, 7, "CONTRATANTE", align="C")
        pdf.set_xy(pdf.l_margin + col + 10, y + 15)
        pdf.cell(col, 7, "CONTRATADO", align="C")
