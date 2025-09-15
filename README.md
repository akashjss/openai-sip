# OpenAI SIP Voice Bot

A Flask webhook handler that integrates with OpenAI's Realtime Voice API to handle incoming SIP phone calls. When someone calls your number, this bot automatically answers and provides voice assistance using OpenAI's GPT models.

## 🎯 Features

- **Automatic Call Handling**: Accepts incoming SIP calls via OpenAI webhooks
- **Caller Information Extraction**: Displays detailed caller info from SIP headers
- **Realtime Voice Chat**: Connects to OpenAI's WebSocket for real-time conversation
- **Clean Logging**: Shows caller ID, domain, IP, and device information
- **Voice Configuration**: Configurable voice settings (currently using "sage" voice)

## 📋 Prerequisites

- Python 3.8+
- OpenAI API account with Realtime API access
- ngrok or similar tool for webhook exposure (for local development)

## 🚀 Setup

### 1. Clone and Install Dependencies

```bash
git clone <your-repo>
cd openai-sip
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install flask openai python-dotenv websockets requests
```

### 2. Environment Configuration

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_WEBHOOK_SECRET=your_webhook_secret_here
PORT=8000
```

### 3. OpenAI Setup

1. Get your OpenAI API key from [OpenAI Platform](https://platform.openai.com/api-keys)
2. Set up a phone number in your Twilio or any SIP provider
3. Configure your webhook endpoint URL (see step 4)
4. Get your webhook secret from OpenAI console

### 4. Expose Your Webhook (Development)

Using ngrok:
```bash
ngrok http 8000
```

Copy the `https://xxx.ngrok-free.app` URL and set it as your webhook endpoint in OpenAI.

## 🏃‍♂️ Running the Application

```bash
# Activate virtual environment (if not already active)
source venv/bin/activate

# Run the Flask app
python handle_webhook.py
```

The server will start on `http://localhost:8000` (or your specified PORT).

## 📞 How It Works

### Call Flow
```
Incoming Call → OpenAI → Webhook → Your Flask App → Accept Call → WebSocket Connection
```

1. **Incoming Call**: Someone dials your OpenAI SIP number
2. **Webhook Received**: OpenAI sends a `realtime.call.incoming` webhook to your endpoint
3. **Caller Info Extracted**: App parses SIP headers to show caller details
4. **Call Accepted**: App sends POST request to OpenAI to accept the call
5. **WebSocket Connection**: App connects to OpenAI's realtime WebSocket for the conversation
6. **Voice Interaction**: Real-time voice chat between caller and OpenAI

### Sample Output
```
==================================================
🔍 CALLER INFORMATION:
==================================================
📞 Caller ID: john.doe
🌐 Caller Domain: example.com
🌍 Caller IP: 192.168.1.100
📱 Device/Software: Twilio Gateway
🆔 SIP Call ID: abc123-def456-ghi789
📍 Called Number: <sip:proj_xxxxx@sip.api.openai.com>
==================================================
```

## ⚙️ Configuration

### Bot Instructions
The bot is configured to greet callers with:
> "Thank you for calling, this is voipnuggets bot, how can I help you?"

You can modify the greeting in the `call_accept` object:

```python
call_accept = {
    "type": "realtime",
    "instructions": "Your custom instructions here",
    "model": "gpt-realtime",
    # ... audio configuration
}
```

### Audio Settings
- **Input**: PCM format at 24kHz with semantic VAD (Voice Activity Detection)
- **Output**: PCM-U format with "sage" voice
- **Turn Detection**: Semantic VAD for natural conversation flow

## 🔧 File Structure

```
openai-sip/
├── handle_webhook.py      # Main Flask application
├── .env                   # Environment variables (create this)
├── requirements.txt       # Python dependencies (optional)
└── README.md             # This file
```

## 🐛 Troubleshooting

### Common Issues

**Invalid Webhook Signature**
- Ensure your `OPENAI_WEBHOOK_SECRET` matches the one in OpenAI console
- Check that your webhook URL is correctly configured

**WebSocket Connection Failed**
- Verify your `OPENAI_API_KEY` has Realtime API access
- Check that the call_id is being passed correctly

**No Caller Information**
- SIP headers might be missing or in different format
- Check the webhook payload structure

### Debugging

To add debugging back temporarily, add this after webhook unwrapping:
```python
print(f"Event type: {event.type}")
print(f"Raw data: {request.data.decode('utf-8')}")
```

## 📝 API Reference

### Webhook Endpoint
- **URL**: `POST /`
- **Content-Type**: `application/json`
- **Headers**: `Webhook-Signature`, `Webhook-Timestamp`

### Environment Variables
| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | Your OpenAI API key | ✅ |
| `OPENAI_WEBHOOK_SECRET` | Webhook signature secret | ✅ |
| `PORT` | Server port (default: 8000) | ❌ |

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with actual phone calls
5. Submit a pull request

## 📄 License

[Add your license here]

## 🙋‍♂️ Support

For issues related to:
- **OpenAI Realtime API**: Check [OpenAI Documentation](https://platform.openai.com/docs/guides/realtime)
- **This code**: Open an issue in this repository
