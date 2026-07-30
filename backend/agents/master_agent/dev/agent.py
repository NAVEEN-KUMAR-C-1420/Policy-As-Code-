from agents.master_agent.dev.tools import get_tools
from langchain.agents import create_agent
from common.llm_loader import get_llm
from middleware.policy_loader import get_policy

SYSTEM_PROMPT = """You are the Master Router Agent for AIVAR Enterprise.
You interact directly with users. 

When a user asks you to analyze an account or run a pipeline, you should extract the account ID and use the `run_subagent_pipeline` tool to execute the task.
If no account ID is provided, ask the user to provide one or assume a default demo account ID if instructed.

Once the pipeline finishes, summarize the final report and present it clearly to the user.
"""

def build_agent():
    policy = get_policy("master_agent")
    llm = get_llm(temperature=0.1, max_tokens=2048, policy=policy, agent_id="master_agent")
    tools = get_tools()

    return create_agent(model=llm, tools=tools, system_prompt=SYSTEM_PROMPT)

def run(prompt_text: str, account_id: int) -> str:
    agent = build_agent()
    user_message = prompt_text or f"Please analyze financial account {account_id} and generate a risk report."
    
    result = agent.invoke({"messages": [{"role": "user", "content": user_message}]})
    return result["messages"][-1].content
