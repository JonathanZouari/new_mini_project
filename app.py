from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import traceback

# Import configuration from settings
from config.settings import (
    TWILIO_ACCOUNT_SID,
    TWILIO_AUTH_TOKEN,
    TWILIO_PHONE_NUMBER,
    FLASK_DEBUG
)

# Validate required Twilio credentials
if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER]):
    raise ValueError("Missing required Twilio credentials in .env file")

app = Flask(__name__)

# Import CrewAI after loading env
from crew import process_whatsapp_message

@app.route("/whatsapp/", methods=['POST'])
def receive_whatsapp():
    """Receive incoming WhatsApp message and process with CrewAI"""

    # Get incoming message and sender phone
    incoming_message = request.form.get('Body', '').strip()
    sender_phone = request.form.get('From', '')

    print(f"\n📩 Received message from {sender_phone}: {incoming_message}")

    try:
        # Process with CrewAI + Google Calendar (synchronously)
        bot_response = process_whatsapp_message(incoming_message, sender_phone)

        print(f"✅ Processing completed for {sender_phone}")
        print(f"📝 Bot response: {bot_response}")

        # Send the final response
        response = MessagingResponse()
        response.message(bot_response)

        return str(response)

    except Exception as e:
        print(f"❌ Error processing message: {str(e)}")
        traceback.print_exc()

        # Send error message to user
        response = MessagingResponse()
        response.message("מצטער, אירעה שגיאה. אנא נסה שוב.")
        return str(response)



if __name__ == "__main__":
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=FLASK_DEBUG)

