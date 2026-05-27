const BASE_URL = 'http://127.0.0.1:8000/api'

async function request(endpoint, method = 'GET', body = null) {
    const token = localStorage.getItem('access_token')

    const headers = {
        'Content-Type': 'application/json',
    }

    if (token) {
        headers['Authorization'] = `Bearer ${token}`
    }

    const config = {
        method,
        headers,
    }

    if (body) {
        config.body = JSON.stringify(body)
    }

    const response = await fetch(`${BASE_URL}${endpoint}`, config)

 if (response.status === 401) {
    localStorage.clear()
    window.location.href = '/frontend/index.html'
}   

    return response
}