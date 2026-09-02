// Preenche os campos do contratante a partir da agenda de clientes.
//
// Os campos continuam editáveis: uma correção feita aqui vira um upsert na
// agenda quando o contrato é gerado, então o dado se conserta sozinho.
(function () {
  "use strict";

  var CAMPOS = [
    "nome", "documento", "tipo_documento", "email", "telefone", "cep",
    "logradouro", "numero", "complemento", "bairro", "cidade", "estado",
  ];

  function lerAgenda() {
    var script = document.getElementById("agenda-de-clientes");
    if (!script) {
      return [];
    }
    try {
      return JSON.parse(script.textContent) || [];
    } catch (e) {
      return [];
    }
  }

  document.addEventListener("DOMContentLoaded", function () {
    var seletor = document.getElementById("seletor-cliente");
    if (!seletor) {
      return;
    }

    var porId = {};
    lerAgenda().forEach(function (cliente) {
      porId[String(cliente.id)] = cliente;
    });

    // Contato e endereço ficam recolhidos num collapse. Se o cliente escolhido
    // tem algum desses dados, abrimos o bloco — preencher campo invisível
    // esconde do usuário o que foi para o contrato.
    var OPCIONAIS = ["email", "telefone", "cep", "logradouro", "numero",
                     "complemento", "bairro", "cidade", "estado"];

    function abrirOpcionais() {
      var bloco = document.getElementById("extra-contratante");
      if (bloco && !bloco.classList.contains("show")) {
        bloco.classList.add("show");
      }
    }

    seletor.addEventListener("change", function () {
      var cliente = porId[seletor.value];
      CAMPOS.forEach(function (campo) {
        var input = document.querySelector(
          '[name="contratante_' + campo + '"]'
        );
        if (input) {
          // "Novo cliente" limpa o bloco em vez de deixar o resto do anterior.
          input.value = cliente ? cliente[campo] || "" : "";
        }
      });

      var temOpcional = cliente && OPCIONAIS.some(function (campo) {
        return cliente[campo];
      });
      if (temOpcional) {
        abrirOpcionais();
      }
    });
  });
})();
