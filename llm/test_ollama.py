from ollama import chat
import time

models = ["llama3.2", "qwen3:8b"]

questions = [
    "What is Retrieval-Augmented Generation (RAG) in AI?",
    "A candidate has 6 years of Python experience and 3 years of Azure experience. "
    "Does this candidate have Azure experience?",
    "List three skills that are commonly relevant for a DevOps engineer."
]

for model in models:
    print("\n" + "=" * 60)
    print(f"MODEL: {model}")
    print("=" * 60)

    for question in questions:
        print(f"\nQuestion: {question}")

        start = time.time()

        response = chat(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": question
                }
            ],
        )

        elapsed = time.time() - start

        print(f"Response: {response.message.content}")
        print(f"Time: {elapsed:.2f} seconds")