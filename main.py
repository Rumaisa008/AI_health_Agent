
import os
from dotenv import load_dotenv
from agents import Agent, Runner, OpenAIChatCompletionsModel, function_tool, set_tracing_disabled
from openai import AsyncOpenAI
import chainlit as cl
# from whatsapp import send_whatsapp_message # Removed as per your request

load_dotenv()
set_tracing_disabled(True)

API_KEY = os.getenv("GEMINI_API_KEY")

# --- Crucial for Gemini compatibility with OpenAI client ---
# The base_url needs to point to Gemini's OpenAI-compatible endpoint.
# The model name should also reflect this.
external_client = AsyncOpenAI(
    api_key=API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

# Use the openai_client parameter to pass your configured client
model = OpenAIChatCompletionsModel(
    model="gemini-1.5-flash", # Use the actual Gemini model name
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

    # The `input` to Runner.run_sync can be a string or a list of messages.
    # If it's a list, it should match the expected format for the LLM.
    # For simplicity with the `openai-agents` and `OpenAIChatCompletionsModel`,
    # let's try passing the current message content as a string directly,
    # and manage the history for subsequent turns in Chainlit.
    # For a full conversation history, you might need to convert `history`
    # into the specific format expected by `OpenAIChatCompletionsModel`
    # or ensure the `Agent` can handle a list of dicts.
    # For now, let's process the *current* user message for the agent.
    # If you want full chat history for the agent's context, you'd need
    # to pass it as `messages` parameter if `Runner.run_sync` supports it,
    # or let the `Agent` manage its internal history if configured.
    # A common pattern is:
    # result = await ai_health_buddy.run(message.content, history=history) # if agent supports history
    # Or, for `Runner.run_sync` which is simpler:
    result = Runner.run_sync(
        starting_agent=ai_health_buddy,
        input=message.content # Pass only the current message to the agent
    )

    history.append({"role": "assistant", "content": result.final_output})
    cl.user_session.set("history", history)

    await cl.Message(content=result.final_output).send()

