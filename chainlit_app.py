import os
import time
import logging
import chainlit as cl
from dotenv import load_dotenv
from pymongo import MongoClient
from crews import create_crew_from_config
from helpers import get_conversation_history, store_conversation
import chainlit.input_widget as input_widget
from urllib.parse import quote_plus
import ujson
from langfuse import Langfuse

langfuse = Langfuse(
  secret_key="sk-lf-d9d581e7-60ac-499b-949a-fd333c4992d7",
  public_key="pk-lf-0447b70e-334a-4dff-8fbb-0d36ce3059ab",
  host="https://cloud.langfuse.com"
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


@cl.on_chat_start
async def setup():
    logger.info("Starting chat setup")
    try:
        # Initialize MongoDB connection
        logger.info("Connecting to MongoDB")

        # Create a MongoDB client
        client = MongoClient(os.getenv("MONGODB_URI"))
        db = client["crewai_db"]
        logger.info("MongoDB connection established")
        
        # Store client and db in user session
        logger.info("Storing database connection in user session")
        cl.user_session.set("db", db)
        cl.user_session.set("client", client)
        cl.user_session.set("user_id", "default_user")
        
        # Set default crew_id
        cl.user_session.set("crew_id", None)
        
        # Add crew selection as a setting
        logger.info("Setting up chat settings")
        await setup_settings()
        logger.info("Chat setup completed successfully")
    except Exception as e:
        logger.error(f"Error during chat setup: {str(e)}", exc_info=True)
        raise


async def setup_settings():
    logger.info("Setting up chat settings")
    try:
        # Get available crews from database
        db = cl.user_session.get("db")
        logger.info("Fetching crews from database")
        
        crews = list(db["crews"].find({}))
        logger.info(f"Found {len(crews)} crews in database")
        for crew in crews:
            logger.info(f"- ID: {crew['_id']}, Name: {crew.get('name', 'Unknown')}")
        
        # Create crew options
        crew_options = {}
        for crew in crews:
            if '_id' in crew and 'name' in crew:
                crew_options[str(crew["_id"])] = str(crew["_id"])

        # Add default option
        crew_options[""] = "Default Crew"
        logger.info(f"Created {len(crew_options)-1} crew options (plus default)")
        
        logger.info("Sending chat settings")
        await cl.ChatSettings(
            [
                input_widget.Select(
                    id="crew_id",
                    label="Select Crew",
                    description="Choose which crew to work with",
                    initial=cl.user_session.get("crew_id") or "",
                    items=crew_options
                ),
            ]
        ).send()
        logger.info("Chat settings sent successfully")
    except Exception as e:
        logger.error(f"Error setting up chat settings: {str(e)}", exc_info=True)
        raise


@cl.on_settings_update
async def on_settings_update(settings):
    logger.info(f"Updating settings: {settings}")
    try:
        cl.user_session.set("crew_id", settings["crew_id"] if settings["crew_id"] else None)
        logger.info(f"Updated crew_id to: {settings['crew_id'] if settings['crew_id'] else None}")
    except Exception as e:
        logger.error(f"Error updating settings: {str(e)}", exc_info=True)
        raise

@cl.on_message
async def main(message: cl.Message):
    logger.info(f"Received message: {message.content[:50]}...")
    try:
        start_time = time.time()
        user_id = cl.user_session.get("user_id","default_user")
        crew_id = cl.user_session.get("crew_id")
        db = cl.user_session.get("db")
        
        # Create a Langfuse trace for this conversation
        # trace = langfuse.trace(
        #     name="crew_conversation",
        #     user_id=user_id,
        #     metadata={
        #         "crew_id": str(crew_id) if crew_id else "default",
        #         "channel": "chainlit"
        #     }
        # )

        logger.info("Creating thinking message")
        thinking_msg = cl.Message(
            content="Thinking...",
            author="System"
        )
        logger.info("Sending thinking message")
        await thinking_msg.send()
        
        # Create crew from database configuration
        logger.info(f"Creating crew from config with ID: {crew_id}")

        payload = {
            "entry": [{
                "id": "429863360201247",
                "time": 1742802047,
                "changes": [{
                    "value": {
                        "from": {
                            "id": "28266067783040524",
                            "name": "Mohammed Akhnas Gawai"
                        },
                        "post": {
                            "status_type": "added_photos",
                            "is_published": True,
                            "updated_time": "2025-03-24T07:40:44+0000",
                            "permalink_url": "https://www.facebook.com/122141934062468766/posts/pfbid034KQwDd28snHvzsPFiuwQs3QQCt8KgWQbvDe2tK7cxoLNzKegRZkGAvRMohkZG3X5l",
                            "promotion_status": "inactive",
                            "id": "429863360201247_122142193274468766"
                        },
                        "message": "Tracking details",
                        "post_id": "429863360201247_122142193274468766",
                        "comment_id": "122142193274468766_2030811864067732",
                        "created_time": 1742802044,
                        "item": "comment",
                        "parent_id": "429863360201247_122142193274468766",
                        "verb": "add"
                    },
                    "field": "feed"
                }]
            }],
            "object": "page"
        }
        
        # Get conversation history for context
        conversation_context = get_conversation_history(user_id)
        print("#######################", conversation_context)

        message_content =' '.join(conversation_context) + ' ' + message.content
        print("$$$$$$$$$$$$$$$$$$$$$$$$", message_content)

        # # Log the user input in Langfuse
        # trace.generation(
        #     name="user_input",
        #     input=message.content,
        #     metadata={
        #         "with_context": len(conversation_context) > 0,
        #         "context_length": len(conversation_context)
        #     }
        # )

        crew = create_crew_from_config(crew_id, db=db, user_id=user_id, message_content=message_content, payload=str(payload))
        
        # Update the thinking message
        thinking_msg.content = "Running crew agents to process your request..."
        await thinking_msg.update()

        # Execute the crew with the message content
        logger.info("Executing crew with user input")

        # generation_start = time.time()
        result = crew.kickoff(inputs={"user_input": message_content, 
                                      "payload": str(payload),
                                      })


        # generation_end = time.time()

        # # Log the model generation in Langfuse
        # generation = trace.generation(
        #     name="crew_execution",
        #     input=message_content,
        #     output=result.raw,
        #     start_time=generation_start,
        #     end_time=generation_end,
        #     model="crewai",
        #     metadata={
        #         "crew_id": str(crew_id) if crew_id else "default"
        #     }
        # )

        if crew.memory:
            store_conversation(
                user_id=user_id,
                user_message=message_content,
                assistant_response=result.raw,
                metadata={"crew_id": crew_id}
            )

        logger.info("Crew execution completed")

        # Extract text from JSON if applicable
        import json
        try:
            response_data = json.loads(result.raw)
            if isinstance(response_data, dict) and "message" in response_data and "text" in response_data["message"]:
                response_text = response_data["message"]["text"]
            else:
                response_text = result.raw
        except (json.JSONDecodeError, TypeError):
            # If it's not valid JSON or doesn't have the expected structure
            response_text = result.raw
        
        # # Log the final processed response in Langfuse
        # trace.event(
        #     name="processed_response",
        #     value=response_text
        # )

        # Remove the thinking message
        logger.info("Removing thinking message")
        await thinking_msg.remove()
        
        # Send the final response with extracted text
        response_time = time.time() - start_time
        logger.info("Sending final response")
        await cl.Message(
            content=response_text,  # Use the extracted text
            author="Crew"
        ).send()
        
        # Add processing time as a system message
        logger.info("Sending processing time message")
        await cl.Message(
            content=f"Processed in {response_time:.2f} seconds",
            author="System",
            type="system"
        ).send()
                
        # # Add latency metric to Langfuse
        # trace.event(
        #     name="processing_time",
        #     value=response_time,
        #     metadata={"unit": "seconds"}
        # )

    except Exception as e:      
        logger.error(f"Error processing message: {str(e)}", exc_info=True)
        await cl.Message(
            content=f"An error occurred: {str(e)}",
            author="Error",
            type="error"
        ).send()                                       
        


@cl.on_chat_end
def on_chat_end():
    logger.info("Chat ended, cleaning up resources")
    try:
        # Close MongoDB connection
        client = cl.user_session.get("client")
        if client:
            logger.info("Closing MongoDB connection")
            client.close()
            logger.info("MongoDB connection closed")
    except Exception as e:
        logger.error(f"Error during chat cleanup: {str(e)}", exc_info=True)