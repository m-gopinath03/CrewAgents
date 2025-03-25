from crewai import Task
from config import get_task_config
from agents import create_agent
from tools import get_tool_class


def create_task(task_id, db, inputs):
    """Create a task from stored configuration"""

    # Get task configuration from database
    task_config = get_task_config(task_id, db)
    
    if not task_config:
        raise ValueError(f"Task configuration not found for {task_id}")
    
    # Get the agent
    agent_id = task_config.get("agent_id")
    agent = create_agent(agent_id, db, inputs)
    
    human_input = task_config.get("human_input", False)
    
    context_task_id = task_config.get("task_id", None)

    # Create the context task if it exists
    context = [create_task(context_task_id, db, inputs)] if context_task_id else None

    output_json_name = task_config.get("output_json", None)
    print('output json: ', output_json_name)
    if output_json_name:
        tool_class = get_tool_class(output_json_name)
    else:
        tool_class = None

    # Create the task instance
    return Task(
        description=task_config.get("description"),
        expected_output=task_config.get("expected_output"),
        agent=agent,
        human_input=human_input,
        context=context,
        output_json=tool_class
    )

