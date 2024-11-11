from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

# Initialize the OpenAI client
client = OpenAI(
    api_key = os.getenv("OPENAI_API_KEY")
)

# Example API request using Chat Completions
completion = client.chat.completions.create(
    model="gpt-4-turbo-2024-04-09",
    # model="gpt-4-1106-preview",
    messages=[
    {"role": "user", "content":
            r"""

     """
         }

    ]
)

# Print the generated completion
print(completion.choices[0].message.content)






