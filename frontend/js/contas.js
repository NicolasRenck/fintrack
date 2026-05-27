requireAuth()

let categorias = []

async function carregarCategorias() {
    const response = await request('/categorias/')
    if (!response.ok) return
    categorias = await response.json()
    const select = document.getElementById('categoria')
    select.innerHTML = ''
    categorias.forEach(c => {
        const opt = document.createElement('option')
        opt.value = c.id
        opt.textContent = c.nome
        select.appendChild(opt)
    })
}

function formatBRL(value) {
    return Number(value).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
}

async function carregarContas() {
    const response = await request('/contas/')
    if (!response.ok) return
    let data = await response.json()

    const status = document.getElementById('filtro-status').value
    const tipo = document.getElementById('filtro-tipo').value

    if (status !== '') data = data.filter(c => String(c.paga) === status)
    if (tipo !== '') data = data.filter(c => c.tipo === tipo)

    const tbody = document.getElementById('tabela-body')

    if (data.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" class="empty">Nenhuma conta encontrada.</td></tr>'
        return
    }

    const hoje = new Date().toISOString().slice(0, 10)

    tbody.innerHTML = data.map(c => {
        const venc = new Date(c.vencimento + 'T00:00:00').toLocaleDateString('pt-BR')
        const vencida = !c.paga && c.vencimento < hoje
        const catNome = categorias.find(cat => cat.id === c.categoria)?.nome || '—'

        return `
        <tr class="${vencida ? 'row-vencida' : ''}">
            <td>
                ${c.descricao}
                ${c.recorrente ? '<i class="fa-solid fa-rotate" title="Recorrente" style="color: var(--accent); font-size: 11px; margin-left: 6px;"></i>' : ''}
            </td>
            <td>${catNome}</td>
            <td>${venc} ${vencida ? '<span class="badge-vencida">Vencida</span>' : ''}</td>
            <td><span class="badge ${c.tipo}">${c.tipo}</span></td>
            <td class="${c.tipo === 'receita' ? 'green' : 'red'}">${formatBRL(c.valor)}</td>
            <td>
                <button class="btn-pagar ${c.paga ? 'pago' : ''}" onclick="togglePaga(${c.id}, ${c.paga})">
                    <i class="fa-solid ${c.paga ? 'fa-circle-check' : 'fa-circle'}"></i>
                    ${c.paga ? 'Pago' : 'Pendente'}
                </button>
            </td>
            <td class="acoes">
                <button class="btn-icon" onclick="editarConta(${c.id})" title="Editar">
                    <i class="fa-solid fa-pen"></i>
                </button>
                <button class="btn-icon danger" onclick="deletarConta(${c.id})" title="Deletar">
                    <i class="fa-solid fa-trash"></i>
                </button>
            </td>
        </tr>`
    }).join('')
}

async function togglePaga(id, paga) {
    const response = await request(`/contas/${id}/`, 'PATCH', { paga: !paga })
    if (response.ok) carregarContas()
}

function abrirModal() {
    document.getElementById('modal-title').textContent = 'Nova conta'
    document.getElementById('conta-id').value = ''
    document.getElementById('descricao').value = ''
    document.getElementById('valor').value = ''
    document.getElementById('tipo').value = 'despesa'
    document.getElementById('vencimento').value = ''
    document.getElementById('recorrente').value = 'false'
    document.getElementById('modal-error').textContent = ''
    document.getElementById('modal').style.display = 'flex'
}

function fecharModal() {
    document.getElementById('modal').style.display = 'none'
}

function fecharModalFora(e) {
    if (e.target.id === 'modal') fecharModal()
}

async function editarConta(id) {
    const response = await request(`/contas/${id}/`)
    if (!response.ok) return
    const c = await response.json()
    document.getElementById('modal-title').textContent = 'Editar conta'
    document.getElementById('conta-id').value = c.id
    document.getElementById('descricao').value = c.descricao
    document.getElementById('valor').value = c.valor
    document.getElementById('tipo').value = c.tipo
    document.getElementById('categoria').value = c.categoria
    document.getElementById('vencimento').value = c.vencimento
    document.getElementById('recorrente').value = String(c.recorrente)
    document.getElementById('modal-error').textContent = ''
    document.getElementById('modal').style.display = 'flex'
}

async function salvarConta() {
    const id = document.getElementById('conta-id').value
    const body = {
        descricao: document.getElementById('descricao').value,
        valor: document.getElementById('valor').value,
        tipo: document.getElementById('tipo').value,
        categoria: document.getElementById('categoria').value,
        vencimento: document.getElementById('vencimento').value,
        recorrente: document.getElementById('recorrente').value === 'true',
    }

    const method = id ? 'PATCH' : 'POST'
    const url = id ? `/contas/${id}/` : '/contas/'
    const response = await request(url, method, body)

    if (response.ok) {
        fecharModal()
        carregarContas()
    } else {
        document.getElementById('modal-error').textContent = 'Erro ao salvar. Verifique os campos.'
    }
}

async function deletarConta(id) {
    if (!confirm('Deletar esta conta?')) return
    const response = await request(`/contas/${id}/`, 'DELETE')
    if (response.ok) carregarContas()
}

document.getElementById('filtro-status').addEventListener('change', carregarContas)
document.getElementById('filtro-tipo').addEventListener('change', carregarContas)

carregarCategorias().then(() => carregarContas())