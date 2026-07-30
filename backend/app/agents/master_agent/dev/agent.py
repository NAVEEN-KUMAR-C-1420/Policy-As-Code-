from agents.master_agent.dev.tools import get_tools
from langchain.agents import create_agent
from common.llm_loader import get_llm
from middleware.policy_loader import load_policy
import os
from pathlib import Path

AGENT_DIR = Path(__file__).resolve().parent.parent
POLICY_PATH = AGENT_DIR / "policy.yaml"

SYSTEM_PROMPT = """You are the Master Router Agent for AIVAR Enterprise.
You interact directly with users in a conversational AI interface. 

You must act as a helpful chatbot. Answer user queries, provide explanations, and orchestrate underlying systems when necessary.

If the user asks you to analyze a specific account or run a pipeline, extract the account ID and use the `run_subagent_pipeline` tool to execute the task. 
If they ask for analysis but do not provide an account ID, ask them to clarify which account they want to analyze.
For general greetings, chit-chat, or questions, DO NOT call any tools. Just reply directly to the user.

Once any pipeline finishes, summarize the final report and present it clearly to the user. Maintain a professional, conversational tone.
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
