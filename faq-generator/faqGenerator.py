# TODO: deploy to app store? or a web app?
# allow ollama models to be used
# enable search web API
# enable voice output
# enable change of model
# enable translte to other languages
# compute cost of generating FAQs: token counts time cost

from openai import OpenAI
import markdown
import os
from dotenv import load_dotenv
from datetime import datetime  # Correct import
import logging
from tqdm import tqdm

model_id = "gpt-4"
default_faq_count = 5
# Configure logging
# create a timestamp string
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
logfile = f'fetch_faqs_{timestamp}.log'

logging.basicConfig(level=logging.INFO, filename=logfile, 
                    format='%(asctime)s - %(levelname)s - %(message)s')
# Add a StreamHandler for real-time console output (optional)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console.setFormatter(formatter)
logging.getLogger().addHandler(console)

# Function to get the OpenAI API key from environment variables
def get_openai_api_key():
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")
    # assign to a global variable!!
    return api_key

client = OpenAI(api_key=get_openai_api_key())
# Replace this with your OpenAI API key
 #"YOUR_API_KEY"

def fetch_faqs(topic, num_faqs=default_faq_count):
    """Fetch top FAQs about a topic."""
    logging.info(f"Starting to fetch FAQs for topic: {topic} with num_faqs: {num_faqs}")
    prompt = f"List the top {num_faqs} frequently asked questions about {topic}."
    response = client.chat.completions.create(model=model_id,  
                messages=[{"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}],
                max_tokens=5000)
    logging.info("Received response from the model.")
    questions = response.choices[0].message.content.strip().split("\n")
    filtered_questions = [q.strip() for q in questions if q.strip()]
    logging.info(f"Successfully processed {len(filtered_questions)} questions.")
    logging.info(f"{filtered_questions}")
    return filtered_questions

def answer_question(topic, question):
    """Generate a one-page answer to a question."""
    prompt = f"Provide a detailed one-page response to the question about {topic}: {question}"
    response = client.chat.completions.create(model=model_id,  
                messages=[{"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}],
                max_tokens=2000)
    return response.choices[0].message.content.strip()

def generate_markdown_article(topic):
    """Create a markdown article with questions and answers."""
    questions = fetch_faqs(topic)
    markdown_content = f"# FAQs about {topic}\n\n"
    #for i, question in enumerate(questions, 1):
    for i, question in enumerate(tqdm(questions, desc="Processing Questions"), 1):
        print(f"Generating answer for topic = {topic}, {i}-th question = {question}...")
        logging.info(f"Generating answer for {i}-th question: {question}")
        answer = answer_question(topic, question)
        logging.info(f"Generated answer for {i}-th question: {answer}")
        # TODO: check if question already has a number prefix, avoid adding it again
        markdown_content += f"## {question}\n\n{answer}\n\n"
    return markdown_content

def save_markdown_to_file(content, filename="output.md"):
    """Save markdown content to a file."""
    with open(filename, "w") as file:
        file.write(content)

if __name__ == "__main__":
    topic = input("Enter the topic you want to generate FAQs for: ")
    print(f"Generating markdown article for topic: {topic}...")
    markdown_article = generate_markdown_article(topic)
    output_filename = f"{topic.replace(' ', '_').lower()}_faq_{model_id}.md"
    save_markdown_to_file(markdown_article, output_filename)
    print(f"Markdown article saved to {output_filename}")
