import { useEffect, useState } from 'react';
import { apiFetch } from './api';
import type { Agent } from './agents';
import { messages, type Locale } from './i18n/messages';

interface Claim {
  agent_id: number; claim_status: 'none' | 'running' | 'uncertain'; run_id: number | null;
  task_id: number | null; heartbeat_state: 'fresh' | 'stale' | 'unknown' | 'not_running' | null;
}

export function AgentClaim({agents, locale}: {agents: Agent[]; locale: Locale}) {
  const [selected, setSelected] = useState('');
  const [claim, setClaim] = useState<Claim | null>(null);
  const [failed, setFailed] = useState(false);
  const t = messages[locale];
  // Clear the selected configuration if the loaded list changes (including token changes).
  const agent = agents.find(item => String(item.id) === selected);
  useEffect(() => {
    let active = true;
    setClaim(null); setFailed(false);
    if (agent) {
      apiFetch(`/api/agents/${agent.id}/claim`).then(response => {
        if (!response.ok) throw new Error('Unable to inspect claim');
        return response.json();
      }).then(data => { if (active) setClaim(data); }).catch(() => { if (active) setFailed(true); });
    }
    return () => { active = false; };
  }, [agent, agents]);
  const states = {fresh: t.heartbeatFresh, stale: t.heartbeatStale, unknown: t.heartbeatUnknown, not_running: t.heartbeatNotRunning};
  return <div><h3>{t.agentClaim}</h3><p>{t.agentClaimHelp}</p>
    <label>{t.agentClaimSelect}<select value={agent ? selected : ''} onChange={e => setSelected(e.target.value)}><option value="">{t.agentClaimChoose}</option>{agents.map(item => <option key={item.id} value={item.id}>{item.name} (#{item.id})</option>)}</select></label>
    {agent && (failed ? <p role="alert">{t.agentClaimError}</p> : !claim ? <p>{t.loadingDetails}</p> : claim.claim_status === 'none' ? <p>{t.agentClaimNone}</p> : <p>{claim.claim_status === 'running' ? t.runRunning : t.runUncertain} · {t.taskId} <bdi>#{claim.task_id}</bdi> · {t.agentRunId} <bdi>#{claim.run_id}</bdi> · {claim.heartbeat_state ? states[claim.heartbeat_state] : t.heartbeatUnknown}</p>)}
  </div>;
}
