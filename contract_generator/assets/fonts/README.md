# Fontes embutidas no PDF

As fontes core do PDF (Helvetica e afins) não cobrem os caracteres acentuados
do português, então o gerador embute estas — todas sob a licença **SIL Open
Font License 1.1**, cujos textos estão nos arquivos `OFL-*.txt` ao lado.

| Arquivo | Uso |
|---|---|
| `BarlowCondensed-Regular.ttf`, `BarlowCondensed-SemiBold.ttf` | título do contrato e cabeçalhos de cláusula |
| `SourceSerif4-Regular.ttf`, `SourceSerif4-Bold.ttf`, `SourceSerif4-It.ttf` | corpo do texto |

O Google Fonts publica o Source Serif 4 apenas como fonte variável, e o fpdf2
precisa de um arquivo por peso. As três faces acima foram instanciadas da
variável com `fontTools.varLib.instancer`, em `opsz=11` (o corpo do contrato)
e `wght` 400 / 700 / 400-itálico.

> Não excluir do bundle: sem estes arquivos o `PdfGenerator` não sobe.
> Ver `.vercelignore`.
