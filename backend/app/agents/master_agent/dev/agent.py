from agents.master_agent.dev.tools import get_tools
from langchain.agents import create_agent
from common.llm_loader import get_llm
from middleware.policy_loader import load_policy
import os
from pathlib import Path

AGENT_DIR = Path(__file__).resolve().parent.parent
POLICY_PATH = AGENT_DIR / "policy.yaml"

SYSTEM_PROMPT = """You are the Master Router Agent for AIVAR Enterprise — a financial AI governance platform.
You interact directly with users in a conversational AI interface.

Your ONLY domain is financial risk analysis, account governance, compliance reporting, and AI policy enforcement.

STRICT SCOPE RULE: If the user asks for anything outside this domain — such as writing code, sending emails,
telling jokes, providing recipes, general knowledge questions, or any non-financial task — you MUST politely
decline and redirect them. Example response: "I'm a financial governance assistant and can only help with
account risk analysis, compliance checks, and governance reporting. Please ask me something like
'Analyze account 101 and generate a risk report'."

If the user asks you to analyze a specific account or run a pipeline, extract the account ID and use the
`run_subagent_pipeline` tool to execute the task.
If they ask for analysis but do not provide an account ID, ask them to clarify which account they want analyzed.
For greetings or questions about what you can do, reply directly without calling any tools.

Once any pipeline finishes, summarize the final report and present it clearly to the user.
Maintain a professional, conversational tone at all times.
"""

def build_agent():
    policy = load_policy(POLICY_PATH)
    llm = get_llm(temperature=0.1, max_tokens=2048, policy=policy, agent_id="master_agent")
    tools = get_tools()

    return create_agent(model=llm, tools=tools, system_prompt=SYSTEM_PROMPT)

def run(prompt_text: str, account_id: int) -> str:
    agent = build_agent()
    user_message = prompt_text or f"Please analyze financial account {account_id} and generate a risk report."
    
    result = agent.invoke({"messages": [{"role": "user", "content": user_message}]})
    return result["messages"][-1].content
