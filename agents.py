from crewai import Agent, LLM
from datetime import datetime
from  config import get_agent_config, get_tools_for_agent
from helpers import create_tool_from_config
import json

def create_agent(agent_id, db, message_content, payload):
    """Create an agent from stored configuration"""
    # Get agent configuration from database
    agent_config = get_agent_config(agent_id=agent_id, db=db)
    
    if not agent_config:
        raise ValueError(f"Agent configuration not found for {agent_id}")
    
    # Get associated tools
    tool_ids = get_tools_for_agent(agent_id=agent_id, db=db)
    tools = [create_tool_from_config(tool_id, db) for tool_id in tool_ids]
    
    # Apply any dynamic placeholders in the configuration
    backstory = agent_config.get("backstory", "")
    backstory += f"Todays Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    goal = agent_config.get("goal")
    goal = goal.replace("{user_input}", message_content)

    # Before inserting payload into goal string, escape its curly braces
    escaped_payload = str(payload).replace("{", "{{").replace("}", "}}")
    goal = goal.replace("{payload}", escaped_payload)

    # goal += f" user_input : {message_content}"
    print('goalllllllllllllllllllllllllllllllllll: ', goal)
    # Use provided LLM or create a default one
    llm_config = agent_config.get("llm", {"model": "gpt-4o-mini", "temperature": 0.5})
    llm = LLM(model=llm_config.get("model"), temperature=llm_config.get("temperature"))

    # Create the agent instance
    return Agent(
        role=agent_config.get("role"),
        goal=goal,
        backstory=backstory,
        verbose=agent_config.get("verbose", True),
        allow_delegation=agent_config.get("allow_delegation", False),
        tools=tools,
        llm=llm,
        max_iter=3,
    )