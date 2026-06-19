import os
import requests
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(override=True)
client = OpenAI(
    api_key=os.environ.get("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

def send_slack_notification(message: str) -> None:
    print("Sending Slack notification...")
    response = requests.post(
        "https://slack.com/api/chat.postMessage",
        json={"channel": os.environ.get("CHANNEL_ID"), "text": message},
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {os.environ.get('SLACK_ACCESS_TOKEN')}",
        },
    )
    response.raise_for_status()
    data = response.json()
    if data.get("ok"):
        print("Slack notification sent successfully.")
    else:
        raise Exception(f"Failed to send Slack notification: {data.get('error')}")

def dev_assistant():
    # Prompt the developer for their question or technical task
    topic = input("AI bot assistant for devs: ")
    
    prompt = f"""
    You are a highly efficient developer assistant. Provide a concise, clear, and direct 
    solution, explanation, or code snippet for the following request:
    
    Request: {topic}
    
    Keep the tone professional and helpful. Avoid fluff or generic introductory text so 
    it reads cleanly when sent to the team Slack channel. Do not include hashtags or emojis.
    """
    
    try:
        response = client.chat.completions.create(
            model="models/gemini-2.5-flash",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert full-stack software development assistant specializing in writing clean code, troubleshooting bugs, and explaining technical concepts."
                },
                {"role": "user", "content": prompt}
            ]
        )
        
        # Extract the assistant's technical response
        dev_answer = response.choices[0].message.content
        print(dev_answer)
        print("\n----------------------------------------")
        
        # Forward the developer response straight to your channel
        send_slack_notification(dev_answer)
        
    except Exception as e:
        print(f"An error occurred while generating the response: {e}")
        print("Please ensure your API key is correct, the model name is valid for your setup, and that SLACK_ACCESS_TOKEN is set.")

# Call the correct function name to run it locally
dev_assistant()
