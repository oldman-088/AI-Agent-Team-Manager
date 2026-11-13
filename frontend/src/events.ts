export interface ActivityEvent {
  id: number;
  project_id: number | null;
  task_id: number | null;
  related_task_id: number | null;
  event_type: string;
  created_at: string;
}

export async function listEvents(fetcher: typeof fetch = fetch): Promise<ActivityEvent[]> {
  const response = await fetcher('/api/events');
  if (!response.ok) throw new Error('Could not load activity');
  return response.json();
}
