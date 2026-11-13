export type Health = 'checking' | 'ready' | 'not-ready';
export async function fetchHealth(fetcher: typeof fetch = fetch): Promise<Health> {
  try {
    const response = await fetcher('/health/ready');
    return response.ok ? 'ready' : 'not-ready';
  } catch {
    return 'not-ready';
  }
}
