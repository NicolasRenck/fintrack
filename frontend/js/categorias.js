requireAuth()

async function carregarCategorias() {
    const response = await request('/categorias/')
    if (!response.ok) return
    const data = await response.json()

    const grid = document.getElementById('categorias-grid')

    if (data.length === 0) {
        grid.innerHTML = '<p class="empty">Nenhuma categoria cadastrada.</p>'
        return
    }

    grid.innerHTML = data.map(c => `
        <div class="categoria-card">
            <div class="categoria-card-header">
                <span class="categoria-card-nome">${c.nome}</span>
                <span class="badge ${c.tipo}">${c.tipo}</span>
            </div>
            <div class="categoria-card-acoes">
                <button class="btn-icon" onclick="editarCategoria(${c.id})" title="Editar">
                    <i class="fa-solid fa-pen"></i>
                </button>
                <button class="btn-icon danger" onclick="deletarCategoria(${c.id})" title="Deletar">
                    <i class="fa-solid fa-trash"></i>
                </button>
            </div>
        </div>
    `).join('')
}

function abrirModal() {
    document.getElementById('modal-title').textContent = 'Nova categoria'
    document.getElementById('categoria-id').value = ''
    document.getElementById('nome').value = ''
    document.getElementById('tipo').value = 'despesa'
    document.getElementById('modal-error').textContent = ''
    document.getElementById('modal').style.display = 'flex'
}

function fecharModal() {
    document.getElementById('modal').style.display = 'none'
}

function fecharModalFora(e) {
    if (e.target.id === 'modal') fecharModal()
}

async function editarCategoria(id) {
    const response = await request(`/categorias/${id}/`)
    if (!response.ok) return
    const c = await response.json()
    document.getElementById('modal-title').textContent = 'Editar categoria'
    document.getElementById('categoria-id').value = c.id
    document.getElementById('nome').value = c.nome
    document.getElementById('tipo').value = c.tipo
    document.getElementById('modal-error').textContent = ''
    document.getElementById('modal').style.display = 'flex'
}

async function salvarCategoria() {
    const id = document.getElementById('categoria-id').value
    const body = {
        nome: document.getElementById('nome').value,
        tipo: document.getElementById('tipo').value,
    }

    const method = id ? 'PATCH' : 'POST'
    const url = id ? `/categorias/${id}/` : '/categorias/'
    const response = await request(url, method, body)

    if (response.ok) {
        fecharModal()
        carregarCategorias()
    } else {
        document.getElementById('modal-error').textContent = 'Erro ao salvar. Verifique os campos.'
    }
}

async function deletarCategoria(id) {
    if (!confirm('Deletar esta categoria?')) return
    const response = await request(`/categorias/${id}/`, 'DELETE')
    if (response.ok) carregarCategorias()
}

carregarCategorias()