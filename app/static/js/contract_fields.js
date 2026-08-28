// Mostra os parâmetros declarados pelo template do tipo de contrato escolhido
// (horas, entrada, prazos, multas...) e esconde os dos demais tipos.
//
// Os inputs escondidos ficam `disabled` para não irem no POST — assim o
// servidor só recebe os campos do tipo realmente selecionado.
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

  seletorTipo.addEventListener("change", alternarSecoes);
  alternarSecoes();

  // --- Entrada e saldo -----------------------------------------------------
  // Convenção dos templates: quando existem os campos `valor_entrada` e
  // `valor_saldo`, eles se dividem no valor total do contrato. A entrada é
  // sugerida como metade e o saldo é o que sobra — ambos continuam editáveis.
  var campoValor = document.querySelector('input[name="value"]');
  var entrada = document.querySelector('input[data-campo="valor_entrada"]');
  var saldo = document.querySelector('input[data-campo="valor_saldo"]');
  if (!campoValor || !entrada || !saldo) {
    return;
  }

  var entradaEditadaPeloUsuario = entrada.value.trim() !== "";

  function arredondar(numero) {
    return Math.round(numero * 100) / 100;
  }

  function recalcular() {
    var total = parseFloat(campoValor.value);
    if (isNaN(total)) {
      return;
    }
    if (!entradaEditadaPeloUsuario) {
      entrada.value = arredondar(total / 2);
    }
    var pago = parseFloat(entrada.value);
    saldo.value = arredondar(isNaN(pago) ? total : Math.max(total - pago, 0));
  }

  campoValor.addEventListener("input", recalcular);
  entrada.addEventListener("input", function () {
    entradaEditadaPeloUsuario = entrada.value.trim() !== "";
    recalcular();
  });
  recalcular();
})();
