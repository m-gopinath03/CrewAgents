# tools/__init__.py
import importlib
import inspect
import os
import sys
from crewai.tools import BaseTool
from pydantic import BaseModel

# Dictionary to store all discovered tool classes
_tool_classes = {}

def _is_tool_class(obj):
    """Check if an object is a tool class (not an instance)"""
    return (
        inspect.isclass(obj) and 
        (issubclass(obj, BaseTool) or issubclass(obj, BaseModel)) and 
        obj != BaseTool and
        not obj.__name__.startswith('_')
    )

# Auto-discover all tool classes in this directory
try:
    for module_file in os.listdir(os.path.dirname(__file__)):
        if module_file.endswith('.py') and not module_file.startswith('_'):
            module_name = module_file[:-3]  # Remove .py extension
            
            try:
                # Import the module
                module = importlib.import_module(f'tools.{module_name}')
                
                # Find all tool classes in the module
                for name, obj in inspect.getmembers(module, _is_tool_class):
                    print('name: ', name)
                    # Add the tool class to our dictionary
                    _tool_classes[name] = obj
                    
                    # Also make it available at the package level
                    globals()[name] = obj
            except Exception as e:
                print(f"Error loading tool module {module_name}: {e}")
except Exception as e:
    print(f"Error discovering tool modules: {e}")

# Make all discovered classes available via __all__
__all__ = list(_tool_classes.keys())

# Function to get a tool class by name
def get_tool_class(class_name):
    """Get a tool class by name"""
    print("tool classes: ",_tool_classes)
    return _tool_classes.get(class_name)