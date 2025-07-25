
# import os
# import requests
# from agents import function_tool

# @function_tool
# def send_whatsapp_message(number: str, message: str) -> str:
#     """
#     Uses UltraMsg API to send WhatsApp message.
#     """
#     instance_id = os.getenv("INSTANCE_ID")
#     token = os.getenv("API_TOKEN")

#     if not message or len(message.strip()) < 3:
#         return "❌ Message is too short to send."

#     if not number.startswith("92"):
#         return "❌ Please provide WhatsApp number in international format (e.g., 923142345678)."

#     url = f"/{instance_id}/messages/chat"
#     payload = {
#         "token": token,
#         "to": number,
#         "body": message
#     }

#     try:
#         response = requests.post(url, data=payload)
#         if response.status_code == 200:
#             return f"📤 Message sent to {number}"
#         else:
#             return f"❌ Failed: {response.text}"
#     except Exception as e:
#         return f"❌ Exception: {str(e)}"