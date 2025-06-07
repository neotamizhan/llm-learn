import requests, json, time

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "phi3:mini"

# ----------------- Tools you expose -----------------
def get_weather(city: str) -> str:
    # Totally offline stub; swap in a real API later.
    fake_report = {
        "Paris": "🌧️  Light rain, 18 °C",
        "Kuwait City": "☀️  Sunny, 38 °C",
        "Tokyo": "⛅  Partly cloudy, 24 °C",
    }
    return fake_report.get(city, "Weather data unavailable.")

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Return a short weather report for a given city.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string"}
                },
                "required": ["city"]
            },
        },
    }
]
# ----------------------------------------------------

def ollama_chat(messages):
    resp = requests.post(OLLAMA_URL, json={
        "model": MODEL,
        "messages": messages,
        "tools": TOOLS,
        "stream": False        # easier parsing for demo
    })
    resp.raise_for_status()
    return resp.json()

def main():
    print(f"Connecting to Ollama at {OLLAMA_URL} using model {MODEL}...\n")
    messages = [
        {"role": "system", "content": "You are a helpful assistant."}
    ]
    print(">>> Ask me something (type 'exit' to quit)")
    while True:
        user = input("You: ")
        if user.lower() == "exit":
            break

        messages.append({"role": "user", "content": user})
        reply = ollama_chat(messages)
        choice = reply["choices"][0]

        if tool := choice.get("tool_calls"):
            # The model wants to call a function
            tc = tool[0]
            fn_name = tc["function"]["name"]
            args = json.loads(tc["function"]["arguments"])

            if fn_name == "get_weather":
                result = get_weather(**args)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc["id"],
                    "name": fn_name,
                    "content": result
                })
                # Ask the model to continue using the tool’s answer
                follow_up = ollama_chat(messages)
                assistant_msg = follow_up["choices"][0]["message"]["content"]
            else:
                assistant_msg = "🤔 I don’t know that tool yet."
        else:
            assistant_msg = choice["message"]["content"]

        messages.append({"role": "assistant", "content": assistant_msg})
        print(f"Assistant: {assistant_msg}\n")

if __name__ == "__main__":
    main()