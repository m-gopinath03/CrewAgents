import os
import logging
from crewai import Crew, Process
from agents import create_agent
from tasks import create_task
from dotenv import load_dotenv
from bson import ObjectId

# Load environment variables
load_dotenv()

# Set up logging
logger = logging.getLogger(__name__)

def get_crew_config(crew_id, db):
    """Get crew configuration from the database"""
    
    crew_config = db.crews.find_one({"_id": ObjectId(crew_id)})
    if not crew_config:
        raise ValueError(f"Crew '{crew_id}' not found in database")
    
    return crew_config

def create_crew_from_config(crew_id, db, user_id, message_content):
    """Create a crew based on configuration from the database"""
    logger.info(f"Creating crew: {crew_id}")
    
    # Get crew configuration
    crew_config = get_crew_config(crew_id, db)

    # Create agents
    agents = []
    for agent_id in crew_config["agents"]:
        logger.info(f"Creating agent: {agent_id}")
        agent = create_agent(agent_id, db, message_content)
        agents.append(agent)
    
    # Create tasks
    tasks = []
    for task_id in crew_config["tasks"]:
        logger.info(f"Creating task: {task_id}")
        # Find the corresponding agent for this task
        task = create_task(task_id, db, message_content)
        tasks.append(task)

    memory = crew_config.get("memory", False)
    if memory:
        memory_config = {
            "provider": "mem0",
            "config": {"user_id": user_id},
        }
    else:
        memory_config = None

    # Set up and return the crew
    logger.info("Setting up crew")
    crew = Crew(    
        agents=agents,
        tasks=tasks,
        verbose=True,
        memory=memory,
        memory_config=memory_config,
    )
    
    return crew