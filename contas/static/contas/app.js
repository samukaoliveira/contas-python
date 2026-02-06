
    function openModal() {
        document.getElementById('modalLancamento').style.display = 'flex';
    }

    function closeModal() {
        const modal = document.getElementById('modalLancamento');
        const form = document.querySelector("#modalLancamento form");
        form.reset();
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


    function openEditModal(id, data, descricao, valor, natureza, pago, fixo, parcelas) {
        const form = document.querySelector('#modalLancamento form');

        form.action = `/update/${id}/`;

        form.data.value = data;
        form.descricao.value = descricao;
        form.valor.value = parseFloat(valor.replace(',', '.'));
        form.natureza.value = natureza;
        form.fixo.value = fixo;
        form.parcelas.value = parcelas;
        form.pago.checked = pago === 'True' || pago === true;



        document.querySelector('#modalLancamento h2').innerText = 'Editar Lançamento';

        openModal();
    }


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

    function openEditModalCartao(id, descricao, limite, fechamento, vencimento) {
        const form = document.querySelector('#modalLancamento form');

        form.action = `/cartoes/${id}/edit/`;

        form.descricao.value = descricao;
        form.limite.value = parseFloat(limite.replace(',', '.'));
        form.fechamento.value = fechamento;
        form.vencimento.value = vencimento;

        document.querySelector('#modalLancamento h2').innerText = 'Editar Cartão';

        openModal();
    }

