import os
import json
import uvicorn
import google.generativeai as genai
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import Response
from twilio.rest import Client
from dotenv import load_dotenv
from pydantic import BaseModel

# Load environment variables from .env file
load_dotenv()

# --- Configuration ---
PORT = int(os.getenv("PORT", "8080"))
DOMAIN = os.getenv("NGROK_URL") 
if not DOMAIN:
    raise ValueError("NGROK_URL environment variable not set.")
WS_URL = f"wss://{DOMAIN}/ws"

# Twilio Configuration
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")  # Your Twilio phone number

if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER]):
    raise ValueError("Missing required Twilio environment variables: TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER")

# Initialize Twilio client
twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Updated greeting to reflect the new model
WELCOME_GREETING = "Hi! I am a voice assistant powered by Twilio and Google Gemini. Ask me anything!"

# System prompt for Gemini
SYSTEM_PROMPT = """You are a helpful and friendly voice assistant. This conversation is happening over a phone call, so your responses will be spoken aloud. 
Please adhere to the following rules:
1. Provide clear, concise, and direct answers.
2. Spell out all numbers (e.g., say 'one thousand two hundred' instead of 1200).
3. Do not use any special characters like asterisks, bullet points, or emojis.
4. Keep the conversation natural and engaging."""

# --- Gemini API Initialization ---
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY environment variable not set.")

genai.configure(api_key=GOOGLE_API_KEY)

# Configure the Gemini model
model = genai.GenerativeModel(
    model_name='gemini-2.5-flash',
    system_instruction=SYSTEM_PROMPT
)

# Store active chat sessions
sessions = {}

# Create FastAPI app
app = FastAPI()

# Pydantic model for outbound call request
class OutboundCallRequest(BaseModel):
    to_number: str  # Phone number to call (e.g., "+1234567890")
    custom_greeting: str = None  # Optional custom greeting

async def gemini_response(chat_session, user_prompt):
    """Get a response from the Gemini API and stream it."""
    response = await chat_session.send_message_async(user_prompt)
    return response.text

@app.post("/make-call")
async def make_outbound_call(request: OutboundCallRequest):
    """Endpoint to initiate an outbound call"""
    try:
        # Create the TwiML URL for this call
        twiml_url = f"https://{DOMAIN}/twiml"
        
        # If custom greeting is provided, you could store it temporarily
        # For simplicity, we'll use the default greeting
        
        # Make the outbound call
        call = twilio_client.calls.create(
            to=request.to_number,
            from_=TWILIO_PHONE_NUMBER,
            url=twiml_url,
            method='POST'
        )
        
        return {
            "success": True,
            "call_sid": call.sid,
            "status": call.status,
            "to": request.to_number,
            "from": TWILIO_PHONE_NUMBER,
            "message": f"Call initiated to {request.to_number}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to make call: {str(e)}")

@app.post("/twiml")
async def twiml_endpoint():
    """Endpoint that returns TwiML for Twilio to connect to the WebSocket"""
    xml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
    <Response>
    <Connect>
    <ConversationRelay url="{WS_URL}" welcomeGreeting="{WELCOME_GREETING}" ttsProvider="ElevenLabs" voice="FGY2WhTYpPnrIDTdsKH5" />
    </Connect>
    </Response>"""
    
    return Response(content=xml_response, media_type="text/xml")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time communication"""
    await websocket.accept()
    call_sid = None
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message["type"] == "setup":
                call_sid = message["callSid"]
                print(f"Setup for outbound call: {call_sid}")
                # Start a new chat session for this call
                sessions[call_sid] = model.start_chat(history=[])
                
            elif message["type"] == "prompt":
                if not call_sid or call_sid not in sessions:
                    print(f"Error: Received prompt for unknown call_sid {call_sid}")
                    continue

                user_prompt = message["voicePrompt"]
                print(f"Processing prompt from outbound call: {user_prompt}")
                
                chat_session = sessions[call_sid]
                response_text = await gemini_response(chat_session, user_prompt)
                
                # Send the complete response back to Twilio
                await websocket.send_text(
                    json.dumps({
                        "type": "text",
                        "token": response_text,
                        "last": True
                    })
                )
                print(f"Sent response to outbound call: {response_text}")
                
            elif message["type"] == "interrupt":
                print(f"Handling interruption for outbound call {call_sid}")
                
            else:
                print(f"Unknown message type received: {message['type']}")
                
    except WebSocketDisconnect:
        print(f"WebSocket connection closed for outbound call {call_sid}")
        if call_sid in sessions:
            sessions.pop(call_sid)
            print(f"Cleared session for outbound call {call_sid}")

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Twilio Outbound Voice Assistant API",
        "endpoints": {
            "make_call": "POST /make-call - Initiate an outbound call",
            "twiml": "POST /twiml - TwiML webhook endpoint",
            "websocket": "WS /ws - WebSocket for voice communication"
        }
    }

if __name__ == "__main__":
    print(f"Starting Twilio Outbound Voice Assistant server on port {PORT}")
    print(f"WebSocket URL for Twilio: {WS_URL}")
    print(f"TwiML URL: https://{DOMAIN}/twiml")
    print(f"Make calls via: POST https://{DOMAIN}/make-call")
    uvicorn.run(app, host="0.0.0.0", port=PORT)