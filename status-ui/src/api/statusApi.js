const STATUS_ENDPOINT = '/api/status/'
const HISTORY_ENDPOINT = '/api/status/history/?limit=100'

export class ApiError extends Error {
  constructor(status, message) {
    super(message)
    this.status = status
  }
}

async function fetchJson(url) {
  const response = await fetch(url)
  if (!response.ok) {
    throw new ApiError(response.status, `Request failed: ${response.status}`)
  }
  return response.json()
}

export function getStatus() {
  return fetchJson(STATUS_ENDPOINT)
}

export function getHistory() {
  return fetchJson(HISTORY_ENDPOINT)
}
