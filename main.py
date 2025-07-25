import os
from dotenv import load_dotenv
from agents import Agent, Runner, OpenAIChatCompletionsModel, function_tool, set_tracing_disabled
from openai import AsyncOpenAI
import chainlit as cl
from whatsapp import send_whatsapp_message 

load_dotenv()
set_tracing_disabled(True)

API_KEY = os.getenv("GEMINI_API_KEY")

external_client = AsyncOpenAI(
    api_key=API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

model = OpenAIChatCompletionsModel(
    model="gemini-1.5-flash", 
    openai_client=external_client,
)

# Tools for AI Health Buddy

@function_tool
def give_medical_advice(symptom: str) -> str:
    """Provides basic medical advice based on symptom"""
    if "fever" in symptom.lower():
        return "🩺 For fever: Stay hydrated, rest, and consider paracetamol."
    elif "headache" in symptom.lower():
        return "💊 For headache: Try rest, drink water, and avoid screen time."
    else:
        return "⚠️ Please consult a doctor for specific advice."

@function_tool
def provide_mental_support(feeling: str) -> str:
    """Responds supportively to mental health keywords"""
    if "sad" in feeling.lower():
        return "💙 I'm here for you. Try journaling or reaching out to a loved one."
    elif "anxious" in feeling.lower():
        return "🧘‍♂️ Take a deep breath. Grounding exercises can help."
    else:
        return "🫶 You are not alone. Would you like a motivational quote?"

@function_tool
def plan_meal(goal: str) -> str:
    """Suggests meal based on goal"""
    if "weight gain" in goal.lower():
        return "🍽️ Meal Plan: Chicken curry, brown rice, boiled eggs, banana shake."
    elif "weight loss" in goal.lower():
        return "🥗 Meal Plan: Grilled fish, steamed veggies, green tea, apple."
    else:
        return "🥘 Balanced Diet: Daal, roti, yogurt, seasonal fruits."

# Agent Setup

ai_health_buddy = Agent(
    name="AI Health Buddy",
    instructions="""
    You are a friendly AI Health Buddy that provides:
    - Basic medical suggestions
    - Mental wellness tips
    - Meal plans based on goals
    - Keep your answers short and friendly. Use the tools available to help users.
    """,
    model=model,
    tools=[
        give_medical_advice,
        provide_mental_support,
        plan_meal,
    ]
)

# --- Chainlit Events ---

@cl.on_chat_start
async def start():
    cl.user_session.set("history", [])
    await cl.Message("👋 Salam! I'm your AI Health Buddy.\nTell me what you need: medical help, mental support, or meal planning!").send()

@cl.on_message
async def handle_message(message: cl.Message):
    await cl.Message("🤖 Thinking...").send()
    history = cl.user_session.get("history") or []
    history.append({"role": "user", "content": message.content})

 
    result = Runner.run_sync(
        starting_agent=ai_health_buddy,
        input=message.content 
    )

    history.append({"role": "assistant", "content": result.final_output})
    cl.user_session.set("history", history)

    await cl.Message(content=result.final_output).send()

