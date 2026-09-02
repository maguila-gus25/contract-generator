// Ajusta o formulário ao tipo de contrato escolhido.
//
// Governa duas coisas: os parâmetros que o template do tipo declara (a seção
// "Condições do Contrato") e os campos fixos que mudam de forma ou de rótulo
// — data de fim, rótulo da data de início, forma de pagamento e descrição.
//
// Tudo que fica escondido também fica `disabled`, para não ir no POST: o
// servidor só recebe o que vale para o tipo realmente selecionado.
(function () {
  "use strict";

  var seletorTipo = document.querySelector('select[name="contract_type"]');
  var secoes = document.querySelectorAll(".campos-do-tipo");
  if (!seletorTipo || !secoes.length) {
    return;
  }

  function alternarSecoes() {
    var tipo = seletorTipo.value;
    secoes.forEach(function (secao) {
      var ativa = secao.dataset.tipo === tipo;
      secao.hidden = !ativa;
      secao.querySelectorAll("input").forEach(function (input) {
        input.disabled = !ativa;
      });
    });
  }

  // --- Campos fixos que mudam com o tipo -----------------------------------
  // A fotografia é um ensaio de um dia só, pago por um meio conhecido: não
  // tem data de fim, a data de início é a data do ensaio e o pagamento vira
  // uma lista em vez de texto livre.
  var REGRAS = {
    fotografia: {
      dataFim: false,
      rotuloDataInicio: "Data do ensaio",
      pagamentoEmLista: true,
    },
  };
  var PADRAO = {
    dataFim: true,
    rotuloDataInicio: "Data de Início",
    pagamentoEmLista: false,
  };

  var campoDataFim = document.getElementById("campo-data-fim");
  var rotuloDataInicio = document.getElementById("rotulo-data-inicio");
  var pagamentoLivre = document.getElementById("pagamento-livre");
  var pagamentoMeios = document.getElementById("pagamento-meios");
  var descricao = document.querySelector('textarea[name="description"]');

  function lerJson(id) {
    var script = document.getElementById(id);
    try {
      return script ? JSON.parse(script.textContent) || {} : {};
    } catch (e) {
      return {};
    }
  }

  var descricoesPadrao = lerJson("descricoes-padrao");

  function mostrar(elemento, visivel) {
    if (!elemento) {
      return;
    }
    elemento.hidden = !visivel;
    elemento.disabled = !visivel;
  }

  function ehPadraoDeAlgumTipo(texto) {
    return Object.keys(descricoesPadrao).some(function (tipo) {
      return descricoesPadrao[tipo] && descricoesPadrao[tipo] === texto;
    });
  }

  function ajustarCamposFixos() {
    var regra = REGRAS[seletorTipo.value] || PADRAO;

    if (campoDataFim) {
      campoDataFim.hidden = !regra.dataFim;
      campoDataFim.querySelectorAll("input").forEach(function (input) {
        input.disabled = !regra.dataFim;
      });
    }
    if (rotuloDataInicio) {
      rotuloDataInicio.textContent = regra.rotuloDataInicio;
    }
    mostrar(pagamentoLivre, !regra.pagamentoEmLista);
    mostrar(pagamentoMeios, regra.pagamentoEmLista);

    // A descrição só é sobrescrita quando está vazia ou ainda tem o padrão
    // de outro tipo — o que o usuário escreveu nunca se perde.
    var padrao = descricoesPadrao[seletorTipo.value] || "";
    if (descricao && (descricao.value.trim() === ""
                      || ehPadraoDeAlgumTipo(descricao.value.trim()))) {
      descricao.value = padrao;
    }
  }

  function ajustar() {
    alternarSecoes();
    ajustarCamposFixos();
  }

  seletorTipo.addEventListener("change", ajustar);
  ajustar();
})();
