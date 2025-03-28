from flask import Flask, request, jsonify
import logging
import traceback
import time
import os
from crewai import LLM
from crews import create_crew_from_config
from dotenv import load_dotenv
from pymongo import MongoClient
from helpers import get_conversation_history, store_conversation

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route("/api/message", methods=["POST"])
def process_message():
    try:
        # Log that we received a request
        start_time = time.time()
        logger.info("Received request")
        
        # Get request data
        req_data = request.get_json()
        if not req_data or "content" not in req_data:
            logger.error("Missing required field 'content'")
            return jsonify({"error": "Missing required field 'content'"}), 400
            
        content = req_data["content"]
        user_id = req_data.get("user_id", "default_user")

        logger.info(f"Processing message: {content}")
        
        # Get crew name from request or use default
        crew_id = req_data.get("crew_id")
        
        # Create the LLM
        logger.info("Creating Crew")

        # # Get conversation history for context
        conversation_context = get_conversation_history(user_id)
        print("#######################", conversation_context)
        message_content =' '.join(conversation_context) + ' ' + content


        client = MongoClient(os.getenv("MONGODB_URI"))
        db = client["crewai_db"]
        
        # Create crew from database configuration
        crew = create_crew_from_config(crew_id, db=db, user_id=user_id,message_content=message_content) 
        
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
        
        # Execute the crew with the message content - add timeout
        logger.info("Executing crew")
        result = crew.kickoff(inputs={"user_input": message_content, "payload": str(payload["entry"])})


        # Store this conversation turn
        if crew.memory:
            store_conversation(
                user_id=user_id,
                user_message=message_content,
                assistant_response=result.raw,
                metadata={"crew_id": crew_id}
            )
        
        # Return the response
        logger.info("Returning response")
        logger.info(f"Crew execution completed in {time.time() - start_time:.2f} seconds")
        return jsonify({"content": result.raw})
    
    except Exception as e:
        error_msg = f"Error: {str(e)}\n{traceback.format_exc()}"
        logger.error(error_msg)
        return jsonify({"error": str(e)}), 500

@app.route("/health", methods=["GET"])
def health_check():
    """Simple endpoint to verify the server is responding"""
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8001, debug=True)