import os
from dotenv import load_dotenv
from openai import OpenAI
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

load_dotenv(override=True)

# Initialize the OpenAI/Gemini client
ai_client = OpenAI(
    api_key=os.environ.get("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

# Initialize your Slack App with its bot token
slack_app = App(token=os.environ.get("SLACK_ACCESS_TOKEN"))

@slack_app.event("app_mention")
def handle_mention(event, say):
    # Strip the bot's username tagging out of the text prompt
    raw_text = event.get("text", "")
    user_prompt = " ".join([word for word in raw_text.split() if not word.startswith("<@")])
    thread_ts = event.get("ts") # Keep responses in a clean message thread

    if not user_prompt:
        say("Hello! Tag me and ask a technical question or describe a bug, and I'll jump in.", thread_ts=thread_ts)
        return

    # Build the structural system instructions
    prompt = f"""
    You are a highly efficient developer assistant. Provide a concise, clear, and direct 
    solution, explanation, or code snippet for the following request:
    
    Request: {user_prompt}
    
    Keep the tone professional and helpful. Avoid fluff or generic introductory text. 
    Do not include hashtags or emojis.
    """

    try:
        response = ai_client.chat.completions.create(
            model="models/gemini-2.5-flash",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert full-stack software development assistant specializing in writing clean code, troubleshooting bugs, and explaining technical concepts."
                },
                {"role": "user", "content": prompt}
            ]
        )
        
        dev_answer = response.choices[0].message.content
        
        # Send the solution directly back into the Slack channel thread
        say(text=dev_answer, thread_ts=thread_ts)

    except Exception as e:
        say(text=f"Sorry, an error occurred while processing that: {e}", thread_ts=thread_ts)

if __name__ == "__main__":
    # Start the permanent socket connection connection
    handler = SocketModeHandler(slack_app, os.environ.get("SLACK_APP_TOKEN"))
    handler.start()