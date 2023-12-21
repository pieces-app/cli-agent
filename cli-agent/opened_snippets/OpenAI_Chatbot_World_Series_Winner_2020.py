
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()
client = OpenAI()
response = client.chat.completions.create(
  model="gpt-4-1106-preview",
  messages=[
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Who won the world series in 2020?"}
  ]
)
content = response.choices[0].message.content
print(content)
