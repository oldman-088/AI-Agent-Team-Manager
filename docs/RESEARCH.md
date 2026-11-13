# Phase 0 research

Snapshot: 2026-11-13 UTC. Sources: linked repository metadata and README via GitHub API. “Recent” means the repository's `pushed_at` on this date, not an independent security audit or guarantee of support. Licenses are GitHub's repository-level detection, not a transitive dependency review. No candidate has been adopted yet; evaluate exact versions, licenses, releases, threat model and platform support before use. Risks include prompt injection, tool access, credential leakage, untrusted web content and supply-chain compromise across all agent frameworks.

| Candidate | Architecture / integration | Maintenance / license snapshot | Assessment |
|---|---|---|---|
| [OpenHands](https://github.com/OpenHands/OpenHands) | Agent Canvas control center for coding agents; service/agent integration | Recent; MIT | Overlaps AATM's control plane; investigate isolated worker integration, not wholesale adoption. Container/workspace and credential isolation are essential; integration complexity high. |
| [LangGraph](https://github.com/langchain-ai/langgraph) | Python library for stateful agent graphs | Recent; MIT | Candidate for durable orchestration; adds graph and checkpoint semantics; evaluate retries, persistence and dependency weight against a smaller scheduler. Never grant graph nodes unrestricted tools. |
| [CrewAI](https://github.com/crewAIInc/crewAI) | Python multi-agent role orchestration framework | Recent; MIT | Fits role-based teams, but overlaps manager responsibilities and may couple execution models. Evaluate behind a worker adapter against LangGraph. |
| [Microsoft Agent Framework](https://github.com/microsoft/agent-framework) | Python/.NET agent and workflow framework | Recent; MIT | Candidate workflow SDK; evaluate stability and ecosystem integration before selection. External tool and cloud permissions require isolation. |
| [MetaGPT](https://github.com/FoundationAgents/MetaGPT) | Role-based multi-agent framework | Last push Jan 2026; MIT | Relevant role model; less recent activity than alternatives. High integration and dependency risk; research only. |
| [Browser Use](https://github.com/browser-use/browser-use) | Python browser-agent library and hosted service | Recent; MIT | Higher-level AI browser control than Playwright; LLM-driven navigation and hosted option increase data exposure. Defer until policy and local isolation are defined. |
| [Playwright](https://github.com/microsoft/playwright) | Browser automation library with Chromium support | Recent; Apache-2.0 | Preferred candidate for browser automation and E2E tests; mature API but browser processes, profiles and downloads require sandboxing and lifecycle controls. Verify Python package and browser binaries on both OSes. |
| [SWE-agent](https://github.com/SWE-agent/SWE-agent) | GitHub-issue-driven coding agent | Recent; MIT | Candidate isolated execution worker, not control plane. Runs potentially dangerous code; requires strong workspace and process isolation. Higher integration complexity. |
| [mini-SWE-agent](https://github.com/SWE-agent/mini-swe-agent) | Minimal coding agent | Recent; MIT | Candidate worker for simpler experiments; small surface does not replace sandboxing. Compare against SWE-agent before adoption. |
| [LiteLLM](https://github.com/BerriAI/litellm) | Python SDK or gateway for multiple model APIs | Recent; GitHub license detection NOASSERTION | Defer: investigate exact distribution and component licenses and supply-chain history first. A gateway expands credential and data trust boundaries; official SDKs behind an AATM interface are safer initially. |
| [AutoGen](https://github.com/microsoft/autogen) | Multi-agent framework | Recent repository push; README describes project as archived and recommends Microsoft Agent Framework; repository license detection CC-BY-4.0 | Do not select for new work without checking package-level licenses and migration guidance; prefer its successor. |

## Other decisions still requiring research

Official model-provider SDKs and PostgreSQL access/migration libraries will be assessed against exact supported releases before implementation. Provider capabilities, pricing and credential handling vary; no undocumented Arena Local Bridge API is assumed. No third-party runtime integrations are implemented or validated in this phase.

## Provider SDK review (2026-11-13)

GitHub repository metadata and READMEs were reviewed. All three repositories were non-archived and pushed within three days of this snapshot; dates do not guarantee long-term maintenance. Repository-level Apache-2.0 identifiers are preliminary and do not substitute for a transitive license or security audit.

| Official SDK | Architecture / tradeoff | Decision |
|---|---|---|
| [openai-python](https://github.com/openai/openai-python) | Async Python client and Responses API; remote data and paid requests, SDK dependencies and rate limits cross a trust boundary. | Adopt behind a narrow AATM interface for text-only requests. Tests use a mock transport; no live credentials or requests verified. No retries, tools, streaming, cost estimates or automatic execution. |
| [anthropic-sdk-python](https://github.com/anthropics/anthropic-sdk-python) | Official Python messages API; repository README notes license history differs across versions. | Defer pending exact-version and transitive license review and independent adapter tests. |
| [python-genai](https://github.com/googleapis/python-genai) | Official Google Gen AI SDK with synchronous and asynchronous model APIs. | Defer; assess API modes, authentication, data handling and dependency licensing before adoption. |

Even `store=false` is not a guarantee that a provider retains no data for every operational or legal purpose. Never send secrets or private project content without appropriate consent and policy. Provider credentials must not be stored in agent configuration or logs. Public network calls have not been executed or validated here.
