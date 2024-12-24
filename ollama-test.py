# how to quickly switch to openai model using api?

import openai
from openai import OpenAI
import time

client = OpenAI(base_url="http://localhost:11434/v1", api_key="dummy") # must use /v1 for the url!!
model_id="qwen2.5:14b" #"llama3:8b-instruct-q8_0"
def get_completion(prompt):
    try:
        response = client.completions.create(model=model_id,  # Ensure this matches the exact model name in Ollama
        prompt=prompt,
        max_tokens=250,  # Adjust as needed
        temperature=0.7)
        return response.choices[0].text.strip()
    except Exception as e:
        return f"Error: {e}"

if __name__ == "__main__":
    user_prompt = "Hello, how are you?"
    start_time = time.time()
    completion = get_completion(user_prompt)
    end_time = time.time()
    time_spent = end_time - start_time
    print(f"Response from {model_id}, Time spent {time_spent:.2f} seconds")
    print(completion)
