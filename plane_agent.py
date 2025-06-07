import requests, json, time

OLLAMA_URL = "http://localhost:11434/api/chat"

def ollama_chat(messages):
    payload = {
        "model": "phi3:mini",
        "messages": messages,
        "stream": False  # Optional, helps get response at once
    }
    print("Connecting to Ollama at", OLLAMA_URL, "using model", payload["model"] + "...")
    headers = {"Content-Type": "application/json"}
    response = requests.post(OLLAMA_URL, headers=headers, data=json.dumps(payload))
    response.raise_for_status()
    return response.json()

def main():
    messages = []
    print(">>> Ask me something (type 'exit' to quit)")
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            break
        messages.append({"role": "user", "content": user_input})
        try:
            response = ollama_chat(messages)
            if "message" in response:
                assistant_reply = response["message"]["content"]
                print("Assistant:", assistant_reply)
                messages.append({"role": "assistant", "content": assistant_reply})
            else:
                print("Unexpected response format:", response)
        except Exception as e:
            print("Error:", e)

if __name__ == "__main__":
    main()