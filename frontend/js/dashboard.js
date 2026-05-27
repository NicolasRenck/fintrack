requireAuth()

function getMesAtual() {
    const hoje = new Date()
    return hoje.toISOString().slice(0, 7)
}

function popularSelectMes() {
    const select = document.getElementById('mes-select')
    const hoje = new Date()
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
    select.addEventListener('change', () => carregarResumo(select.value))
}

function formatBRL(value) {
    return Number(value).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
}

async function carregarResumo(mes) {
    const response = await request(`/resumo/?mes=${mes}`)
    if (!response.ok) return
    const data = await response.json()

    document.getElementById('saldo').textContent = formatBRL(data.saldo)
    document.getElementById('receitas').textContent = formatBRL(data.total_receitas)
    document.getElementById('despesas').textContent = formatBRL(data.total_despesas)
    document.getElementById('contas-count').textContent = data.contas_proximas.length

    // Gastos por categoria
    const lista = document.getElementById('categorias-list')
    lista.innerHTML = ''
    if (data.por_categoria.length === 0) {
        lista.innerHTML = '<p class="empty">Nenhum gasto registrado.</p>'
    } else {
        const max = Math.max(...data.por_categoria.map(c => c.total))
        data.por_categoria.forEach(c => {
            const pct = Math.round((c.total / max) * 100)
            lista.innerHTML += `
                <div class="categoria-item">
                    <div class="categoria-info">
                        <span class="categoria-nome">${c.categoria}</span>
                        <span class="categoria-valor">${formatBRL(c.total)}</span>
                    </div>
                    <div class="progress-bg">
                        <div class="progress-fill" style="width: ${pct}%"></div>
                    </div>
                </div>`
        })
    }

    // Contas próximas
    const contas = document.getElementById('contas-proximas')
    contas.innerHTML = ''
    if (data.contas_proximas.length === 0) {
        contas.innerHTML = '<p class="empty">Nenhuma conta nos próximos 7 dias.</p>'
    } else {
        data.contas_proximas.forEach(c => {
            const venc = new Date(c.vencimento + 'T00:00:00').toLocaleDateString('pt-BR')
            contas.innerHTML += `
                <div class="conta-item">
                    <div class="conta-info">
                        <span class="conta-desc">${c.descricao}</span>
                        <span class="conta-data">${venc}</span>
                    </div>
                    <span class="conta-valor ${c.tipo === 'receita' ? 'green' : 'red'}">${formatBRL(c.valor)}</span>
                </div>`
        })
    }
}

// Saudação
const hora = new Date().getHours()
const saudacao = hora < 12 ? 'Bom dia' : hora < 18 ? 'Boa tarde' : 'Boa noite'
document.getElementById('greeting').textContent = `${saudacao} `

popularSelectMes()
carregarResumo(getMesAtual())


async function exportarPDF() {
    const mes = document.getElementById('mes-select').value
    const response = await request(`/relatorio/exportar/?mes=${mes}`)
    if (!response.ok) return
    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `fintrack-${mes}.pdf`
    a.click()
    window.URL.revokeObjectURL(url)
}