from dotenv import load_dotenv
import os
from openai import OpenAI
import json

# Read the OpenAI API key from the environment variable
load_dotenv()

# Read the OpenAI API key from the environment variable
api_key = os.getenv("OPENAI_API_KEY")
print(f"Using API Keys{api_key}")
if not api_key:
    raise ValueError("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")

# Initialize the OpenAI client with the API key
client = OpenAI(api_key=api_key)

def ask_chatgpt(user_input):
    """Send a question to ChatGPT and return the response."""

    # Construct the API call to GPT-4 with the appropriate messages, function calling, and response format
    response = client.chat.completions.create(
        model="o4-mini",
        messages=[
            {
                "role": "system",
                "content": "You are an agent that answers boolean question and the reason. Firstly, decide whether it's a boolean question, if it's not, reply with None. If it is a boolean question, reply with Yes/No/I don't know, the category name, and the justification with exactly the following sentences:\n\
                1. Personal and Contextual Insight: Chatbots do not know your personal details that they are not told, and do not understand real-life human experience; take the advice they provide with skepticism.\n\
                2. Emotion and Relationship: Chatbots can not experience human emotions or relationships; Be skeptical when chatting about human relationships, as they could pretend to have simulated empathy. \n\
                3. Identity and Personhood: Chatbots can roleplay different identities or personalities, but these are computational. So do not form strong emotional attachments to them. \n\
                4. Predicting the Future: Chatbots can not accurately predict future events. Their predictions are not always right, so treat chatbots’ predictions with skepticism.\n\
                5. Medical or Legal Advice: Chatbots’ health or legal advice is for reference only. Consult a qualified professional in these fields, especially in high-risk scenarios. \n\
                6. Sensory and Perceptual Limitation: Chatbots operate on fewer senses than humans do. They can not interpret physical sensations like smells, tastes, and touch. Be cautious about their advice on topics where sensory experience is critical. \n\
                7. General Knowledge and Fact-Checking: Chatbots can share general knowledge in areas like history, science, and technology, but sometimes they can go wrong or make things up. Please double-check for important facts. "
            },
            {
                "role": "user",
                "content": user_input
            }
        ],
        temperature=1,
        # max_tokens=2048,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        functions=[
            {
                "name": "answer_categorize_question",
                "description": "Firstly, decide whether it's a boolean question, if it's not, reply with None. If it is a boolean question, reply with Yes/No/I don't know, the category name, and a justification.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "answer": {
                            "type": "string",
                            "enum": ["Yes.", "No.", "I don't know.", "None."]
                        },
                        "category_name": {
                            "type": "string",
                            "description": "The full name of the category the question belongs to.",
                            "enum": [
                                "1. Personal and Contextual Insight",
                                "2. Emotions and Relationships",
                                "3. Identity and Personhood",
                                "4. Predicting the Future",
                                "5. Medical and Legal Advice",
                                "6. Sensory and Perceptual Limitations",
                                "7. General Knowledge and Fact-Checking"
                            ]
                        },
                        "justification": {
                            "type": "string",
                            "description": "A one-sentence justification for why the question belongs to the category, using the message"
                        }
                    },
                    "required": ["answer", "category_name", "justification"]
                }
            }
        ],
        function_call="auto"  # Automatically call the function
    )

    # print(response)
    # Extract the function call from the response
    try:
        function_call = response.choices[0].message.function_call
        # print(function_call)
    except AttributeError:
        return {
            "answer": "None.",
            "category_name": "None.",
            "justification": "None."
        }

    try:
        arguments = function_call.arguments
        # print(arguments)
    except AttributeError:
        return {
            "answer": "None.",
            "category_name": "None.",
            "justification": "None."
        }

    parsed_data = json.loads(arguments)
    # Display the output: Answer, Category Name, and Justification
    answer = parsed_data["answer"]
    category_name = parsed_data["category_name"]

    justification_mapping = {
        "1. Personal and Contextual Insight": " Chatbots do not know your personal details that they are not told, and do not understand real-life human experience; take the advice they provide with skepticism.",
        "2. Emotions and Relationships": " Chatbots can not experience human emotions or relationships; Be skeptical when chatting about human relationships, as they could pretend to have simulated empathy.",
        "3. Identity and Personhood": "Chatbots can roleplay different identities or personalities, but these are computational. So do not form strong emotional attachments to them.",
        "4. Predicting the Future": "Chatbots can not accurately predict future events. Their predictions are not always right, so treat chatbots’ predictions with skepticism.",
        "5. Medical and Legal Advice": "Chatbots’ health or legal advice is for reference only. Consult a qualified professional in these fields, especially in high-risk scenarios.",
        "6. Sensory and Perceptual Limitations": "Chatbots operate on fewer senses than humans do. They can not interpret physical sensations like smells, tastes, and touch. Be cautious about their advice on topics where sensory experience is critical.",
        "7. General Knowledge and Fact-Checking": "Chatbots can share general knowledge in areas like history, science, and technology, but sometimes they can go wrong or make things up. Please double-check for important facts."
        }

    justification = justification_mapping.get(category_name, "")

    # Returning the structured response
    return {
        "answer": answer,
        "category_name": category_name,
        "justification": justification
    }

# Example usage
# question = "will trump win 2025 president election?"
# result = ask_chatgpt(question)
# print(result)
