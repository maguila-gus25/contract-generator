// Autocompleta o endereço a partir do CEP (ViaCEP via endpoint /api/cep).
// Funciona para os dois blocos do formulário: contratante e contratado.
(function () {
  "use strict";

  function preencher(prefixo) {
    var campoCep = document.querySelector('input[name="' + prefixo + '_cep"]');
    if (!campoCep) {
      return;
    }

    campoCep.addEventListener("blur", function () {
      var cep = campoCep.value.replace(/\D/g, "");
      if (cep.length !== 8) {
        return;
      }

      campoCep.classList.remove("is-invalid");
      campoCep.disabled = true;

      fetch("/api/cep/" + cep)
        .then(function (resp) {
          if (!resp.ok) {
            throw new Error("CEP não encontrado");
          }
          return resp.json();
        })
        .then(function (dados) {
          var mapa = {
            logradouro: dados.logradouro,
            bairro: dados.bairro,
            cidade: dados.cidade,
            estado: dados.estado,
          };
          Object.keys(mapa).forEach(function (campo) {
            var input = document.querySelector(
              'input[name="' + prefixo + "_" + campo + '"]'
            );
            if (input && mapa[campo]) {
              input.value = mapa[campo];
            }
          });
          var numero = document.querySelector(
            'input[name="' + prefixo + '_numero"]'
          );
          if (numero) {
            numero.focus();
          }
        })
        .catch(function () {
          campoCep.classList.add("is-invalid");
        })
        .finally(function () {
          campoCep.disabled = false;
        });
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    ["contratante", "contratado"].forEach(preencher);
  });
})();
