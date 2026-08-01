"""
test_client.py — quick terminal chat loop against your running server.

Run the server first:
    uvicorn main:app --port 8000

Then in another terminal:
    python test_client.py
"""

import requests

BASE_URL = "http://127.0.0.1:8000"

history = []

print("MindMend test chat — type 'quit' to exit.\n")

while True:
    user_input = input("You: ").strip()
    if user_input.lower() in ("quit", "exit"):
        break

    history.append({"role": "user", "content": user_input})

    resp = requests.post(
        f"{BASE_URL}/chat/completions",
        json={"model": "mindmend-v1", "messages": history, "stream": False},
    )
    resp.raise_for_status()
    data = resp.json()
    reply = data["choices"][0]["message"]["content"]
    history.append({"role": "assistant", "content": reply})

    print(f"Scyla: {reply}\n")
