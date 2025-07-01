# **📞 Twilio \+ Gemini Outbound Voice Assistant**

This project is a voice assistant you can call on the phone, powered by Twilio (for calls) and Google Gemini (for AI). When someone calls in, their voice is processed in real time, Gemini generates a smart response, and Twilio reads it back. Think: ChatGPT, but on the phone.

---

## **🏁 Features**

* **Make Outbound Calls:** Start calls to any phone number.  
* **Conversational AI:** All answers powered by Google Gemini.  
* **Real-Time Voice:** User talks, Gemini thinks, Twilio speaks.  
* **WebSocket Magic:** Instant communication for seamless convos.  
* **Configurable Greetings:** Use your own intro or stick with the default.

---

## **⚡️ Quickstart**

### **1\. Clone this repo**

git clone ai-calling-agent  
cd ai-calling-agent

### **2\. Install dependencies**

pip install \-r requirements.txt

### **3\. Set up your `.env`**

Create a `.env` file in the project root with:

PORT=8080  
NGROK\_URL=https://\<your-ngrok-subdomain\>.ngrok-free.app  
TWILIO\_ACCOUNT\_SID=ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXX  
TWILIO\_AUTH\_TOKEN=your\_twilio\_auth\_token  
TWILIO\_PHONE\_NUMBER=+1234567890  
GOOGLE\_API\_KEY=your\_gemini\_api\_key

### **4\. Run Ngrok to Expose Your Local Server**

(You need ngrok installed)

ngrok http 8080

Copy the generated HTTPS forwarding URL and put it in `NGROK_URL` in your `.env`.

### **5\. Start the app**

python app.py

You should see:

Starting Twilio Outbound Voice Assistant server on port 8080  
WebSocket URL for Twilio: wss://\<your-ngrok-url\>/ws  
TwiML URL: https://\<your-ngrok-url\>/twiml  
Make calls via: POST https://\<your-ngrok-url\>/make-call  
---

## **🚀 How It Works**

**High level:**

1. **POST /make-call** to trigger an outbound call.  
2. Twilio dials out, asks your server for TwiML at `/twiml`.  
3. TwiML tells Twilio to connect the call to your `/ws` WebSocket.  
4. User talks. Audio is transcribed. Transcription sent as prompt to Gemini.  
5. Gemini responds. Twilio reads response aloud.  
6. Repeat until user hangs up or the call ends.

---

## **🛠️ API Endpoints**

### **`POST /make-call`**

Start an outbound call.

**Body:**

{  
  "to\_number": "+1234567890",  
  "custom\_greeting": "Hi, this is your personal AI assistant\!" // (optional)  
}

**Response:**

{  
  "success": true,  
  "call\_sid": "CAxxx...",  
  "status": "queued",  
  "to": "+1234567890",  
  "from": "+10987654321",  
  "message": "Call initiated to \+1234567890"  
}  
---

### **`POST /twiml`**

*Twilio-only*: Twilio requests this after you call `/make-call`. You don’t need to call this yourself.

---

### **`WS /ws`**

WebSocket endpoint for real-time voice communication.  
You shouldn’t have to interact with this directly—Twilio does it all.

---

### **`GET /`**

Basic info about the API and available endpoints.

---

## **🧑‍💻 Code Structure**

* `app.py` — The whole backend  
* `.env` — Your secrets and config (never commit this\!)  
* `requirements.txt` — Python deps

---

## **🪄 Customization**

* **Greeting:**  
  Pass a custom message in the `custom_greeting` param when calling `/make-call`.  
* **Voice:**  
  Edit the voice in the `<ConversationRelay>` tag inside `/twiml`.  
* **Model:**  
  Switch Gemini models (e.g. `"gemini-2.5-flash"`) by changing `model_name` in the script.

---

## **🏓 Example Usage (with curl)**

curl \-X POST https://\<your-ngrok-url\>/make-call \\  
\-H "Content-Type: application/json" \\  
\-d '{"to\_number": "+11234567890", "custom\_greeting": "Yo, what can I help you with today?"}'  
---

## **🤖 Tech Stack**

* Python 3.9+  
* FastAPI  
* Twilio REST API  
* Google Generative AI (Gemini)  
* Ngrok (for tunneling)

---

## **🦄 Contributing**

Pull requests and issues welcome\! Just keep it chill.

