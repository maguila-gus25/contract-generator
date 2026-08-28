from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from .base import GeradorBase, rotulo_tipo


class DocxGenerator(GeradorBase):
    def gerar(self, contrato, caminho_saida: str) -> str:
        caminho = self._preparar_caminho(caminho_saida, "docx")
        doc = Document()
        self._aplicar_estilos(doc)
        self._adicionar_cabecalho(doc, contrato)
        self._adicionar_qualificacao(doc, contrato)
        self._adicionar_clausulas(doc, contrato)
        self._adicionar_rodape(doc, contrato)
        doc.save(caminho)
        return caminho

    def _aplicar_estilos(self, doc: Document) -> None:
        estilo = doc.styles["Normal"]
        fonte = estilo.font
        fonte.name = "Arial"
        fonte.size = Pt(12)
        paragrafo = estilo.paragraph_format
        paragrafo.space_after = Pt(6)

    def _adicionar_cabecalho(self, doc: Document, contrato) -> None:
        dados = contrato.to_dict()
        tipo_label = rotulo_tipo(contrato.tipo)
        titulo = doc.add_heading(f"CONTRATO DE {tipo_label}", level=1)
        titulo.alignment = WD_ALIGN_PARAGRAPH.CENTER

        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(f"Contrato nº {dados['numero']}  |  Data: {dados['data_criacao']}")
        run.font.size = Pt(10)
        run.font.color.rgb = RGBColor(0x55, 0x55, 0x55)

        doc.add_paragraph()

    def _adicionar_qualificacao(self, doc: Document, contrato) -> None:
        dados = contrato.to_dict()
        doc.add_heading("PARTES", level=2)

        p = doc.add_paragraph()
        p.add_run("CONTRATANTE: ").bold = True
        p.add_run(
            f"{dados['contratante_nome']}, {dados['contratante_tipo_documento']} "
            f"nº {dados['contratante_documento']}"
        )
        if dados["contratante_endereco"]:
            p.add_run(f", com endereço em {dados['contratante_endereco']}")
        if dados["contratante_email"]:
            p.add_run(f", e-mail: {dados['contratante_email']}")
        p.add_run(".")

        p2 = doc.add_paragraph()
        p2.add_run("CONTRATADO: ").bold = True
        p2.add_run(
            f"{dados['contratado_nome']}, {dados['contratado_tipo_documento']} "
            f"nº {dados['contratado_documento']}"
        )
        if dados["contratado_endereco"]:
            p2.add_run(f", com endereço em {dados['contratado_endereco']}")
        if dados["contratado_email"]:
            p2.add_run(f", e-mail: {dados['contratado_email']}")
        p2.add_run(".")

        doc.add_paragraph(
            "As partes acima identificadas celebram o presente contrato, "
            "que se regerá pelas cláusulas e condições a seguir:"
        )
        doc.add_paragraph()

    def _adicionar_clausulas(self, doc: Document, contrato) -> None:
        dados = contrato.to_dict()
        doc.add_heading("CLÁUSULAS", level=2)

        for clausula in contrato.clausulas:
            conteudo = clausula.conteudo
            try:
                conteudo = conteudo.format(**dados)
            except KeyError:
                pass

            p_titulo = doc.add_paragraph()
            run = p_titulo.add_run(f"CLÁUSULA {clausula.numero}ª - {clausula.titulo.upper()}")
            run.bold = True
            run.font.size = Pt(11)

            doc.add_paragraph(conteudo)

    def _adicionar_rodape(self, doc: Document, contrato) -> None:
        dados = contrato.to_dict()
        doc.add_paragraph()
        doc.add_paragraph(
            f"Vigência: {dados['data_inicio']} a {dados['data_fim']}  |  "
            f"Valor: {dados['valor']}  |  Pagamento: {dados['forma_pagamento']}"
        )

        doc.add_paragraph()
        doc.add_paragraph(f"___________________________________, {dados['data_criacao']}")
        doc.add_paragraph()

        tabela = doc.add_table(rows=3, cols=2)
        tabela.style = "Table Grid"
        tabela.cell(0, 0).text = "CONTRATANTE"
        tabela.cell(0, 1).text = "CONTRATADO"
        tabela.cell(1, 0).text = " " * 50
        tabela.cell(1, 1).text = " " * 50
        tabela.cell(2, 0).text = dados["contratante_nome"]
        tabela.cell(2, 1).text = dados["contratado_nome"]

        for row in tabela.rows:
            for cell in row.cells:
                for para in cell.paragraphs:
                    para.alignment = WD_ALIGN_PARAGRAPH.CENTER
