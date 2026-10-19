
import ollama

MODEL = "llama3.2:3b"

messages = [
    {
        "role": "system",
        "content": (
            "You are my personal AI assistant. "
            "Explain things in simple language. "
            "Help me learn Python, AI, and machine learning. "
            "Be friendly and give examples when useful."
        )
    }
]

print("\n===== MY PERSONAL AI ASSISTANT =====")
print("Ask me anything!")
print("Type /clear to clear the conversation.")
print("Type /exit to quit.\n")

while True:
    question = input("You: ").strip()

    if question.lower() == "/exit":
        print("Assistant: Goodbye!")
        break

    if question.lower() == "/clear":
        messages = messages[:1]
        print("Assistant: Conversation cleared.\n")
        continue

    if not question:
        continue

    messages.append({
        "role": "user",
        "content": question
    })

    try:
        response = ollama.chat(
            model=MODEL,
            messages=messages
        )

        answer = response.message.content

        messages.append({
            "role": "assistant",
            "content": answer
        })

        print(f"\nAssistant: {answer}\n")

    except Exception as error:
        messages.pop()
        print(f"Error: {error}")
        print("Check that Ollama is running and the model is installed.")
