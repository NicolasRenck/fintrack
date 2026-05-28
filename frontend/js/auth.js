function isAuthenticated() {
    return !!localStorage.getItem('access_token')
}

function requireAuth() {
    if (!isAuthenticated()) {
        window.location.href = '/frontend/index.html'
    }
}

function logout() {
    localStorage.clear()
    window.location.href = '/frontend/index.html'
}

async function login(username, password) {
    const response = await fetch('https://fintrack-api-flqh.onrender.com', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
    })

    if (response.ok) {
        const data = await response.json()
        localStorage.setItem('access_token', data.access)
        localStorage.setItem('refresh_token', data.refresh)
        window.location.href = '/frontend/dashboard.html'
    } else {
        return false
    }
}