requireAuth()

let categorias = []

function popularSelectMes() {
    const select = document.getElementById('filtro-mes')
    const hoje = new Date()
    const optTodos = document.createElement('option')
    optTodos.value = ''
    optTodos.textContent = 'Todos os meses'
    select.appendChild(optTodos)
    for (let i = 0; i < 12; i++) {
        const d = new Date(hoje.getFullYear(), hoje.getMonth() - i, 1)
        const value = d.toISOString().slice(0, 7)
        const label = d.toLocaleDateString('pt-BR', { month: 'long', year: 'numeric' })
        const option = document.createElement('option')
        option.value = value
        option.textContent = label
        if (i === 0) option.selected = true
        select.appendChild(option)
    }
    select.addEventListener('change', carregarTransacoes)
    document.getElementById('filtro-tipo').addEventListener('change', carregarTransacoes)
}

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

async function carregarTransacoes() {
    const mes = document.getElementById('filtro-mes').value
    const tipo = document.getElementById('filtro-tipo').value
    let url = '/transacoes/?'
    if (mes) url += `mes=${mes}&`
    if (tipo) url += `tipo=${tipo}`

    const response = await request(url)
    if (!response.ok) return
    const data = await response.json()

    const tbody = document.getElementById('tabela-body')
    if (data.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="empty">Nenhuma transação encontrada.</td></tr>'
        return
    }

    tbody.innerHTML = data.map(t => `
        <tr>
            <td>${t.descricao}</td>
            <td>${t.categoria_nome || '—'}</td>
            <td>${new Date(t.data + 'T00:00:00').toLocaleDateString('pt-BR')}</td>
            <td><span class="badge ${t.tipo}">${t.tipo}</span></td>
            <td class="${t.tipo === 'receita' ? 'green' : 'red'}">${formatBRL(t.valor)}</td>
            <td class="acoes">
                <button class="btn-icon" onclick="editarTransacao(${t.id})" title="Editar">
                    <i class="fa-solid fa-pen"></i>
                </button>
                <button class="btn-icon danger" onclick="deletarTransacao(${t.id})" title="Deletar">
                    <i class="fa-solid fa-trash"></i>
                </button>
            </td>
        </tr>
    `).join('')
}

function abrirModal() {
    document.getElementById('modal-title').textContent = 'Nova transação'
    document.getElementById('transacao-id').value = ''
    document.getElementById('descricao').value = ''
    document.getElementById('valor').value = ''
    document.getElementById('tipo').value = 'despesa'
    document.getElementById('data').value = new Date().toISOString().slice(0, 10)
    document.getElementById('modal-error').textContent = ''
    document.getElementById('modal').style.display = 'flex'
}

function fecharModal() {
    document.getElementById('modal').style.display = 'none'
}

function fecharModalFora(e) {
    if (e.target.id === 'modal') fecharModal()
}

async function editarTransacao(id) {
    const response = await request(`/transacoes/${id}/`)
    if (!response.ok) return
    const t = await response.json()
    document.getElementById('modal-title').textContent = 'Editar transação'
    document.getElementById('transacao-id').value = t.id
    document.getElementById('descricao').value = t.descricao
    document.getElementById('valor').value = t.valor
    document.getElementById('tipo').value = t.tipo
    document.getElementById('categoria').value = t.categoria
    document.getElementById('data').value = t.data
    document.getElementById('modal-error').textContent = ''
    document.getElementById('modal').style.display = 'flex'
}

async function salvarTransacao() {
    const id = document.getElementById('transacao-id').value
    const body = {
        descricao: document.getElementById('descricao').value,
        valor: document.getElementById('valor').value,
        tipo: document.getElementById('tipo').value,
        categoria: document.getElementById('categoria').value,
        data: document.getElementById('data').value,
    }

    const method = id ? 'PATCH' : 'POST'
    const url = id ? `/transacoes/${id}/` : '/transacoes/'
    const response = await request(url, method, body)

    if (response.ok) {
        fecharModal()
        carregarTransacoes()
    } else {
        document.getElementById('modal-error').textContent = 'Erro ao salvar. Verifique os campos.'
    }
}

async function deletarTransacao(id) {
    if (!confirm('Deletar esta transação?')) return
    const response = await request(`/transacoes/${id}/`, 'DELETE')
    if (response.ok) carregarTransacoes()
}

popularSelectMes()
carregarCategorias()
carregarTransacoes()