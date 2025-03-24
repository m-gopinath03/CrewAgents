from pymongo import MongoClient
import os
from dotenv import load_dotenv
from bson import ObjectId

load_dotenv()

def get_agent_config(agent_id, db):
    """Fetch agent configuration from database"""
    return db.agents.find_one({"_id": ObjectId(agent_id)})

def get_task_config(task_id, db):
    """Fetch task configuration from database"""
    return db.tasks.find_one({"_id": ObjectId(task_id)})

def get_tool_config(tool_id, db):
    print("tool_id: ", tool_id)
    """Fetch tool configuration from database"""
    return db.tools.find_one({"_id": ObjectId(tool_id)})

def get_tools_for_agent(agent_id, db):
    """Get tools associated with an agent"""
    agent_config = get_agent_config(agent_id, db)
    tool_ids = agent_config.get("tools", [])
    
    # tools = []
    # for tool_id in tool_ids:
    #     tool_config = get_tool_config(tool_id, db)
    #     if tool_config:
    #         tools.append(tool_config)
    
    return tool_ids