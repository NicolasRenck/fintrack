const BASE_URL = 'https://fintrack-api-flqh.onrender.com'

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
    window.location.href = '/index.html'
}   

    return response
}