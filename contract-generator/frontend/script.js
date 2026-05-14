const API_BASE_URL = 'http://localhost:8000/api';

// Live preview updates
document.getElementById('contract-title').addEventListener('input', (e) => {
    document.getElementById('preview-title').textContent = e.target.value + ' - ' + document.getElementById('contratado-name').value;
});

document.getElementById('contratante-name').addEventListener('input', (e) => {
    document.getElementById('preview-contractor').textContent = e.target.value || 'Contractor';
});

document.getElementById('contratado-name').addEventListener('input', (e) => {
    document.getElementById('preview-contractee').textContent = e.target.value || 'Contractee';
    document.getElementById('preview-title').textContent = document.getElementById('contract-title').value + ' - ' + e.target.value;
});

async function buscarCep(prefix) {
    const cepInput = document.getElementById(`${prefix}-cep`);
    const cep = cepInput.value.replace(/\D/g, '');
    
    if (cep.length !== 8) {
        alert("CEP deve conter 8 dígitos.");
        return;
    }

    try {
        const btn = cepInput.nextElementSibling;
        const originalText = btn.textContent;
        btn.textContent = "...";
        
        const response = await fetch(`${API_BASE_URL}/cep/${cep}`);
        if (!response.ok) throw new Error("Erro ao buscar CEP");
        
        const data = await response.json();
        
        document.getElementById(`${prefix}-address`).value = data.logradouro || '';
        document.getElementById(`${prefix}-bairro`).value = data.bairro || '';
        document.getElementById(`${prefix}-city`).value = `${data.cidade}/${data.estado}`;
        
    } catch (error) {
        alert(error.message);
    } finally {
        const btn = cepInput.nextElementSibling;
        btn.textContent = "Search";
    }
}

async function buscarCnpj(prefix) {
    const docInput = document.getElementById(`${prefix}-doc`);
    const cnpj = docInput.value.replace(/\D/g, '');
    
    if (cnpj.length !== 14) {
        alert("CNPJ deve conter 14 dígitos.");
        return;
    }

    try {
        const btn = docInput.nextElementSibling;
        const originalText = btn.textContent;
        btn.textContent = "...";
        
        const response = await fetch(`${API_BASE_URL}/cnpj/${cnpj}`);
        if (!response.ok) throw new Error("Erro ao buscar CNPJ");
        
        const data = await response.json();
        
        document.getElementById(`${prefix}-name`).value = data.razao_social || '';
        
        if (data.cep) {
            document.getElementById(`${prefix}-cep`).value = data.cep;
            document.getElementById(`${prefix}-address`).value = data.logradouro || '';
            document.getElementById(`${prefix}-num`).value = data.numero || '';
            document.getElementById(`${prefix}-comp`).value = data.complemento || '';
            document.getElementById(`${prefix}-bairro`).value = data.bairro || '';
            document.getElementById(`${prefix}-city`).value = `${data.cidade}/${data.estado}`;
        }
        
        // Trigger input event to update preview
        document.getElementById(`${prefix}-name`).dispatchEvent(new Event('input'));
        
    } catch (error) {
        alert(error.message);
    } finally {
        const btn = docInput.nextElementSibling;
        btn.textContent = "Search";
    }
}

async function gerarContrato(formato) {
    const form = document.getElementById('contract-form');
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }

    const parseCityState = (cityState) => {
        const parts = cityState.split('/');
        return {
            cidade: parts[0] ? parts[0].trim() : '',
            estado: parts[1] ? parts[1].trim() : ''
        };
    };

    const contratanteCityState = parseCityState(document.getElementById('contratante-city').value);
    const contratadoCityState = parseCityState(document.getElementById('contratado-city').value);

    const payload = {
        titulo: document.getElementById('contract-title').value,
        contratante: {
            name: document.getElementById('contratante-name').value,
            document: document.getElementById('contratante-doc').value.replace(/\D/g, ''),
            type: document.getElementById('contratante-type').value,
            email: document.getElementById('contratante-email').value,
            endereco: {
                logradouro: document.getElementById('contratante-address').value,
                numero: document.getElementById('contratante-num').value,
                complemento: document.getElementById('contratante-comp').value,
                bairro: document.getElementById('contratante-bairro').value,
                cidade: contratanteCityState.cidade,
                estado: contratanteCityState.estado,
                cep: document.getElementById('contratante-cep').value.replace(/\D/g, '')
            }
        },
        contratado: {
            name: document.getElementById('contratado-name').value,
            document: document.getElementById('contratado-doc').value.replace(/\D/g, ''),
            type: document.getElementById('contratado-type').value,
            email: document.getElementById('contratado-email').value,
            endereco: {
                logradouro: document.getElementById('contratado-address').value,
                numero: document.getElementById('contratado-num').value,
                complemento: document.getElementById('contratado-comp').value,
                bairro: document.getElementById('contratado-bairro').value,
                cidade: contratadoCityState.cidade,
                estado: contratadoCityState.estado,
                cep: document.getElementById('contratado-cep').value.replace(/\D/g, '')
            }
        },
        valor: parseFloat(document.getElementById('contract-value').value),
        moeda: "R$",
        metodo_pagamento: document.getElementById('contract-payment').value,
        tipo_contrato: document.getElementById('contract-type').value,
        formato_saida: formato
    };

    const statusMsg = document.getElementById('status-message');
    statusMsg.classList.remove('hidden');

    try {
        const response = await fetch(`${API_BASE_URL}/gerar-contrato`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Erro ao gerar contrato');
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `contrato.${formato}`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        a.remove();
        
        alert("Contrato gerado com sucesso!");

    } catch (error) {
        alert("Erro: " + error.message);
    } finally {
        statusMsg.classList.add('hidden');
    }
}
