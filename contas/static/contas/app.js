function openModal(mostrarEscopo = false) {
    document.getElementById('modalLancamento').style.display = 'flex';
    const grupoEscopo = document.getElementById("grupoEscopo");

    if (grupoEscopo) {
        grupoEscopo.style.display = mostrarEscopo ? "block" : "none";
    }
}

function closeModal() {
    const modal = document.getElementById('modalLancamento');
    const form = document.querySelector("#modalLancamento form");

    form.reset();

    esconderParcelas(); // 🔥 garante reset correto

    modal.style.display = 'none';
}

function toggleMenu() {
    document.getElementById('navLinks').classList.toggle('aberto');
}

function toggleOpcoes(botao) {
    const nav = botao.closest(".opcoes").querySelector(".nav-opcoes");
    const estavaAberto = nav.classList.contains("aberto");

    document
        .querySelectorAll(".nav-opcoes.aberto")
        .forEach(n => n.classList.remove("aberto"));

    if (!estavaAberto) {
        nav.classList.add("aberto");
    }
}


// 🔥 CONTROLE CENTRAL DAS PARCELAS
function atualizarParcelas() {
    const fixo = document.getElementById("fixo").value;
    const grupo = document.getElementById("grupoParcelas");
    const inputParcelas = document.getElementById("parcelas");

    if (fixo === "PARCELADO") {
        grupo.style.display = "block";
    } else {
        grupo.style.display = "none";
        inputParcelas.value = 0; // 🔥 regra importante
    }
}


// 🔥 helper para fechar/reset
function esconderParcelas() {
    const grupo = document.getElementById("grupoParcelas");
    const inputParcelas = document.getElementById("parcelas");

    if (grupo) grupo.style.display = "none";
    if (inputParcelas) inputParcelas.value = 0;
}


// 🔥 EDITAR LANÇAMENTO
function openEditModal(id, data, descricao, valor, natureza, fixo, parcelas, pago) {
    const form = document.querySelector('#modalLancamento form');

    form.action = `/update/${id}/`;

    document.getElementById("data").value = data;
    document.getElementById("descricao").value = descricao;
    document.getElementById("valor").value = parseFloat(valor.toString().replace(',', '.'));
    document.getElementById("natureza").value = natureza;
    document.getElementById("fixo").value = fixo || "NAO";
    document.getElementById("parcelas").value = parcelas || 0;
    document.getElementById("pago").checked = (pago === 'True' || pago === true);

    document.getElementById("grupoEscopo").style.display = "block";

    // 🔥 aplica regra visual
    atualizarParcelas();

    document.getElementById('modalTitulo').innerText = 'Editar Lançamento';

    openModal(true);
}


// 🔥 EVENTO GLOBAL (o mais importante)
document.addEventListener("DOMContentLoaded", function () {
    const selectFixo = document.getElementById("fixo");

    if (selectFixo) {
        selectFixo.addEventListener("change", atualizarParcelas);
    }

    // 🔥 garante estado inicial correto ao abrir página
    atualizarParcelas();
});


// 🔥 PAGAR FATURA
function openModalFatura(fatura_id, valor_pago, data_pagamento) {
    document.getElementById('modalPagarFatura').style.display = 'flex';
    const form = document.querySelector('#modalPagarFatura form');

    form.fatura_id.value = fatura_id;
    form.valor_pago.value = parseFloat(valor_pago.replace(',', '.'));
    form.data_pagamento.value = data_pagamento;
}

function closeModalFatura() {
    const form = document.querySelector("#modalPagarFatura form");
    form.reset();
    document.getElementById('modalPagarFatura').style.display = 'none';
}


// 🔥 EDITAR CARTÃO
function openEditModalCartao(id, descricao, limite, fechamento, vencimento) {
    const form = document.querySelector('#modalLancamento form');

    form.action = `/cartoes/${id}/edit/`;

    form.descricao.value = descricao;
    form.limite.value = parseFloat(limite.replace(',', '.'));
    form.fechamento.value = fechamento;
    form.vencimento.value = vencimento;

    document.getElementById('modalTitulo').innerText = 'Editar Cartão';

    openModal();
}