from flask import Flask, request, Response, jsonify, make_response
from openai import OpenAI, InvalidWebhookSignatureError
import asyncio
import json
import os
import requests
import time
import threading
import websockets
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
client = OpenAI(
    webhook_secret=os.environ["OPENAI_WEBHOOK_SECRET"]
)

AUTH_HEADER = {
    "Authorization": "Bearer " + os.getenv("OPENAI_API_KEY")
}

call_accept = {
    "type": "realtime",
    "instructions": "Say to the user in english 'Thank you for calling,this is voipnuggets bot, how can I help you?'. Don't say anything else.",
    "model": "gpt-realtime",
      "audio": {
        "input": {
          "format": {
            "type": "audio/pcm",
            "rate": 24000,
          },
          "turn_detection": {
            "type": "semantic_vad"
          }
        },
        "output": {
          "format": {
            "type": "audio/pcmu",
          },
          "voice": "sage",
        }
      },
}

response_create = {
    "type": "response.create",
    "response": {
        "instructions": (
            "Say to the user 'Thank you for calling,this is voipnuggets bot, how can I help you?'. Don't say anything else."
        )
    },
}

def extract_caller_info(sip_headers):
    """Extract caller information from SIP headers"""
    caller_info = {}

    for header in sip_headers:
        # Handle both dict and object formats
        if hasattr(header, 'name') and hasattr(header, 'value'):
            # Pydantic object format
            name = header.name.lower() if header.name else ""
            value = header.value if header.value else ""
        else:
            # Dictionary format (fallback)
            name = header.get("name", "").lower()
            value = header.get("value", "")

        if name == "from":
            # Extract caller ID from From header: <sip:test@voipnuggets.com>;tag=...
            if "<sip:" in value and "@" in value:
                caller_part = value.split("<sip:")[1].split(">")[0]
                if "@" in caller_part:
                    caller_info["caller_id"] = caller_part.split("@")[0]
                    caller_info["caller_domain"] = caller_part.split("@")[1]
                caller_info["from_header"] = value

        elif name == "contact":
            # Extract caller IP from Contact header
            if "@" in value:
                contact_part = value.split("@")[1].split(":")[0] if ":" in value.split("@")[1] else value.split("@")[1].split(";")[0]
                caller_info["caller_ip"] = contact_part
            caller_info["contact_header"] = value

        elif name == "call-id":
            caller_info["sip_call_id"] = value

        elif name == "user-agent":
            caller_info["user_agent"] = value

        elif name == "to":
            caller_info["destination"] = value

    return caller_info


def print_caller_info(caller_info):
    """Print formatted caller information"""
    print("=" * 50)
    print("🔍 CALLER INFORMATION:")
    print("=" * 50)

    if caller_info.get("caller_id"):
        print(f"📞 Caller ID: {caller_info['caller_id']}")

    if caller_info.get("caller_domain"):
        print(f"🌐 Caller Domain: {caller_info['caller_domain']}")

    if caller_info.get("caller_ip"):
        print(f"🌍 Caller IP: {caller_info['caller_ip']}")

    if caller_info.get("user_agent"):
        print(f"📱 Device/Software: {caller_info['user_agent']}")

    if caller_info.get("sip_call_id"):
        print(f"🆔 SIP Call ID: {caller_info['sip_call_id']}")

    if caller_info.get("destination"):
        print(f"📍 Called Number: {caller_info['destination']}")

    print("=" * 50)


async def websocket_task(call_id):
    try:
        async with websockets.connect(
            "wss://api.openai.com/v1/realtime?call_id=" + call_id,
            additional_headers=AUTH_HEADER,
        ) as websocket:

            while True:
                response = await websocket.recv()
                print(f"Received from WebSocket: {response}")
    except Exception as e:
        print(f"WebSocket error: {e}")


@app.route("/", methods=["POST"])
def webhook():
    try:
        event = client.webhooks.unwrap(request.data, request.headers)

        if event.type == "realtime.call.incoming":
            # Extract and print caller information if SIP headers are available
            if hasattr(event.data, 'sip_headers') and event.data.sip_headers:
                caller_info = extract_caller_info(event.data.sip_headers)
                print_caller_info(caller_info)
            requests.post(
                "https://api.openai.com/v1/realtime/calls/"
                + event.data.call_id
                + "/accept",
                headers={**AUTH_HEADER, "Content-Type": "application/json"},
                json=call_accept,
            )
            threading.Thread(
                target=lambda: asyncio.run(
                    websocket_task(event.data.call_id)
                ),
                daemon=True,
            ).start()
            return Response(status=200)
    except InvalidWebhookSignatureError as e:
        print("Invalid signature", e)
        return Response("Invalid signature", status=400)


if __name__ == "__main__":
    app.run(port=int(os.getenv("PORT", 8000)))