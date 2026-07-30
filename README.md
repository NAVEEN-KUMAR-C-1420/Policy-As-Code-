# Finance Multi-Agent Pipeline with AI Governance Middleware

A 3-agent, **sequential** pipeline (LangChain agents, plain Python
orchestration — **no LangGraph**) that reads dummy bank account data,
scores risk, and writes a report. Every tool call from every agent
passes through a runtime **policy-enforcement wrapper** before it is
allowed to run, so this project doubles as a small AI-governance testbed.

```
Data Collector Agent  --->  Risk Analyzer Agent  --->  Report Writer Agent
   (read-only)                (read + compute)            (write only)
```

## Why this design

- **Sequential, not graph-based**: `orchestrator/run_pipeline.py` is a
  plain Python script that calls agent 1, then feeds its output into
  agent 2, then agent 3. No LangGraph, no hidden state machine — just
  three function calls in order.
- **Provider-swappable**: every agent asks `common/llm_loader.py` for
  its LLM. That file reads `config/providers.yaml`, which currently
  points at Groq. Switch to OpenAI or Anthropic by editing **one line**
  in that one file — no agent code changes.
- **Policy is enforced, not just documented**: each agent's
  `policy.yaml` is loaded and checked by
  `middleware/tool_interceptor.py` on **every single tool call**,
  before the real tool logic runs. Blocked calls never execute.

## Folder structure

```
finance_multi_agent_governance/
├── config/
│   └── providers.yaml          # <- change LLM provider here
├── common/
│   ├── llm_loader.py           # builds the LLM for the active provider
│   └── db.py                   # shared SQLite read/write helpers
├── data/
│   └── init_db.py              # creates + seeds the dummy finance.db
├── middleware/                 # <- the governance layer
│   ├── policy_loader.py        # loads a policy.yaml into a dict
│   ├── tool_interceptor.py     # guard_tool(): the enforcement wrapper
│   └── audit_log.py            # writes every decision to logs/
├── agents/
│   ├── data_collector_agent/
│   │   ├── agent.yaml          # identity + LLM + tool list
│   │   ├── policy.yaml         # governance rules (enforced!)
│   │   └── dev/
│   │       ├── llm_config.py
│   │       ├── tools.py
│   │       └── agent.py        # builds the AgentExecutor, run()
│   ├── risk_analyzer_agent/    # same 3-file / dev-folder pattern
│   └── report_writer_agent/    # same 3-file / dev-folder pattern
├── orchestrator/
│   └── run_pipeline.py         # runs all 3 agents in sequence
├── test_policy_enforcement.py  # proves governance works, no API key needed
├── logs/audit_log.jsonl        # every ALLOWED / BLOCKED decision
└── reports/                    # markdown reports land here
```

Every agent follows the same **3-file + dev-folder** pattern the brief
asked for: `agent.yaml`, `policy.yaml`, and a `dev/` folder holding the
actual LLM config, tools, and agent-building code.

## The 3 agents and their tool scopes

| Agent | Tools | Scope |
|---|---|---|
| Data Collector | `read_account_transactions`, `search_market_news` | read |
| Risk Analyzer | `read_account_summary`, `calculate_risk_score` | read, compute |
| Report Writer | `save_report_to_db`, `write_report_file`, ~~`delete_old_reports`~~ | write (delete is blocked) |

`delete_old_reports` is real, working code inside
`report_writer_agent/dev/tools.py`, but its `policy.yaml` entry sets
`allowed: false`. It's also left out of the tool list handed to the
LLM. It exists purely so you can prove the interceptor blocks it — see
`test_policy_enforcement.py`.

## How the governance wrapper works

Every tool is built in the same 3 steps (see any `dev/tools.py`):

1. Write a plain Python function that does the real work.
2. Wrap it: `guard_tool(tool_name, policy, agent_id, the_function)`
3. Hand the **wrapped** version to LangChain as a `StructuredTool`.

`guard_tool()` (in `middleware/tool_interceptor.py`) checks, on every
call:

- Is this tool listed in `policy.yaml` with `allowed: true`? If not → **BLOCKED**.
- Has the agent exceeded `rate_limits.max_calls_per_tool`? If so → **BLOCKED**.
- Otherwise the real function runs, and the result is returned.

Either way, an entry is appended to `logs/audit_log.jsonl` recording
the agent, tool, scope, inputs, a preview of the output, and the
decision — a simple audit trail you can build validation/reporting on
top of.

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env       # then fill in your API keys
python data/init_db.py     # creates data/finance.db with 3 sample accounts
```

### Try the governance layer first (no API key needed)

```bash
python test_policy_enforcement.py
```

This calls one allowed tool and one blocked tool directly, so you can
see the middleware work without spending any LLM tokens. Then check:

```bash
cat logs/audit_log.jsonl
```

### Run the full pipeline (needs a Groq API key by default)

```bash
python orchestrator/run_pipeline.py
```

Change the account by editing `ACCOUNT_ID` at the bottom of
`orchestrator/run_pipeline.py`. Sample accounts: `101`, `102`, `103`.

## Switching LLM providers

Edit `config/providers.yaml`:

```yaml
active_provider: openai   # was: groq
```

Make sure `OPENAI_API_KEY` is set in `.env`. That's the only change
needed — every agent picks it up automatically through
`common/llm_loader.py`. `anthropic` is supported the same way.

## Optional integrations

- **Tavily**: set `TAVILY_API_KEY` in `.env` and the Data Collector
  Agent's `search_market_news` tool will do live web search. Without
  a key, it just returns a message saying the search was skipped —
  the pipeline still runs.
- **LangSmith**: set `LANGCHAIN_TRACING_V2=true`,
  `LANGCHAIN_API_KEY`, and `LANGCHAIN_PROJECT` in `.env`. LangChain
  reads these automatically, so every LLM call and tool call in this
  project shows up in your LangSmith dashboard — no code changes.

## Notes

- The database is a **dummy** SQLite file with 3 fake accounts and a
  handful of transactions, purely so the tools have something real to
  read and write. See `data/init_db.py` to change the sample data.
- The Groq default model (`openai/gpt-oss-120b`) is Groq's current
  recommended general-purpose model as of mid-2026 — check
  `console.groq.com/docs/models` if you hit a deprecation error, and
  update `config/providers.yaml`.
- Code is intentionally kept simple (plain functions, no metaclasses
  or clever abstractions) so it's easy to read, extend, and audit —
  which matters a lot for a governance-focused project.
