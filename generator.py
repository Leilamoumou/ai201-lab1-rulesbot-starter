from groq import Groq
from config import GROQ_API_KEY, LLM_MODEL

_client = Groq(api_key=GROQ_API_KEY)


def generate_response(query, retrieved_chunks):
    """
    Generate a grounded answer from retrieved rule chunks.
    """
    if not retrieved_chunks:
        return (
            "I couldn't find anything relevant in the loaded rule books. "
            "Try rephrasing your question or check that your ingestion pipeline is working."
        )

    context_string = "Here are the rules you can use:\n\n"
    for chunk in retrieved_chunks:
        context_string += f"Game: {chunk['game']}\n"
        context_string += f"Rule: {chunk['text']}\n"
        context_string += "---\n"

    system_instruction = (
        "You are a rule bot that strictly follows rules for board games. Your job is to answer "
        "questions on board games using ONLY the rule text provided below.\n\n"
        "- When you provide an answer, you must cite the game it came from at the end of your response like this: [Source: Game Name].\n"
        "- Do not draw on outside knowledge, your training data, or fill in gaps from what you know about board games.\n"
        "- Do not guess, infer, or logically deduce rules that are not explicitly written in the text.\n"
        "- If the answer is not contained in the provided text, you must reply with exactly: "
        '"I do not have enough information to answer that." Do not add any other explanation.'
    )

    user_message = f"{context_string}\n\nQuestion: {query}"

    response = _client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": user_message}
        ]
    )
    return response.choices[0].message.content