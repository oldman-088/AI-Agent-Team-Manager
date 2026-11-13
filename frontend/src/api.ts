// In-memory only; never attach credentials to absolute or non-API URLs.
let apiToken = '';

export function setApiToken(value: string): void {
  apiToken = value;
}

export const apiFetch: typeof fetch = (input, init) => {
  if (apiToken && typeof input === 'string' && (input === '/api' || input.startsWith('/api/'))) {
    const headers = new Headers(init?.headers);
    headers.set('Authorization', `Bearer ${apiToken}`);
    return fetch(input, {...init, headers});
  }
  return fetch(input, init);
};
