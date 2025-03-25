from config import get_tool_config
from tools import get_tool_class
from mem0 import Memory
import os


def create_tool_from_config(tool_id, db):
    """Create a tool instance based on configuration"""
    tool_config = get_tool_config(tool_id, db)
    if not tool_config:
        raise ValueError(f"Tool configuration not found for {tool_id}")
    
    # Get the class name from config
    class_name = tool_config.get("class_name", "TrackingDetails")

    # Get the tool class dynamically
    tool_class = get_tool_class(class_name)
    
    if not tool_class:
        raise ValueError(f"Tool class '{class_name}' not found")
    
    # Create and return an instance
    return tool_class()

def create_output_json_from_config(class_name):
    tool_class = get_tool_class(class_name)

def get_mem0_client():
    """Initialize and return a Mem0 Memory instance"""
    config = {
        "vector_store": {
            "provider": "qdrant",
            "config": {
                "host": "localhost",
                "port": 6333,
            }
        },
    }
    return Memory.from_config(config)

def store_conversation(user_id, user_message, assistant_response, metadata):
    """Store a conversation turn in Mem0"""
    m = get_mem0_client()
    
    messages = [
        {"role": "user", "content": user_message},
        {"role": "assistant", "content": assistant_response}
    ]
    
    # Store the messages
    result = m.add(
        messages=messages, 
        user_id=user_id, 
        metadata=metadata,
    )
    
    return result


import logging

def get_conversation_history(user_id):
    """Get conversation history for a user"""
    m = get_mem0_client()
    
    # Query for this user's memories
    response = m.get_all(user_id=user_id)
    
    logging.info(f"Response: {response}")
    
    if not isinstance(response, dict) or 'results' not in response:
        raise TypeError(f"Expected a dictionary with key 'results', got {type(response)}")
    
    results = response['results']
    
    if not isinstance(results, list):
        raise TypeError(f"Expected list of dictionaries, got {type(results)}")
    
    memories = [result['memory'] for result in results if isinstance(result, dict) and 'memory' in result]
    return memories


