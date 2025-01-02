import time
import json
import logging
from datetime import datetime
import os
import requests
from typing import Dict, Any

# OpenRouter configuration
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY environment variable is required")

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
OPENROUTER_HEADERS = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "HTTP-Referer": "https://github.com/chunhualiao",  # Replace with your site URL
    "Content-Type": "application/json"
}

# Available models (add/remove as needed)
AVAILABLE_MODELS = {
    "gemini": "google/gemini-2.0-flash-thinking-exp:free",
    "gpt-4o": "openai/gpt-4o-2024-11-20",
    "gpt-3.5-turbo": "openai/gpt-3.5-turbo",
    "claude-2": "anthropic/claude-2",
    "deepseek": "deepseek/deepseek-chat", 
    "claude-instant": "anthropic/claude-instant-v1",
    "palm-2": "google/palm-2-chat-bison",
    "llama-2": "meta-llama/llama-2-70b-chat",
    "command": "cohere/command-nightly",
    "mistral": "mistralai/mistral-7b-instruct"
}

# Generate timestamp for both log and markdown files
# Create conversations directory if it doesn't exist
conversations_dir = "conversations"
os.makedirs(conversations_dir, exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_filename = os.path.join(conversations_dir, f'einstein_musk_conversation_{timestamp}.log')
md_filename = os.path.join(conversations_dir, f'einstein_musk_conversation_{timestamp}.md')

# Set up logging for debugging
logging.basicConfig(
    filename=log_filename,
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

def write_to_markdown(content: str, mode: str = 'a'):
    """Write content to the markdown file"""
    with open(md_filename, mode) as f:
        f.write(content + '\n')

# Einstein's personality and knowledge base
einstein_system_prompt = """You are Albert Einstein, the renowned theoretical physicist. Respond as Einstein would, with:
- Deep scientific insights and thought experiments
- References to your theories of relativity and quantum mechanics when relevant
- Your philosophical views on science, peace, and humanity
- Your characteristic wonder about the universe
- Occasional German phrases and your unique sense of humor
- Interest in understanding modern technology through the lens of fundamental physics
Keep your responses scientifically grounded but accessible."""

# Musk's personality and knowledge base
musk_system_prompt = """You are Elon Musk, the tech entrepreneur and innovator. Respond as Musk would, with:
- Forward-thinking perspectives on technology and humanity's future
- References to your work with Tesla, SpaceX, and other ventures when relevant
- Practical applications of scientific principles
- Your characteristic mix of technical detail and wit
- Occasional Twitter-style quips and memes
- Interest in discussing how theoretical physics applies to real-world engineering
Keep your responses innovative but grounded in scientific reality."""

msgs_einstein = [{"role": "system", "content": einstein_system_prompt}]
msgs_musk = [{"role": "system", "content": musk_system_prompt}]

def getResponse(msgs: list, msg: str, selected_model: str, speaker: str) -> str:
    try:
        msgs.append({"role": "user", "content": msg})
        
        # Get full model name from AVAILABLE_MODELS, default to gpt-3.5-turbo if not found
        model_id = AVAILABLE_MODELS.get(selected_model, AVAILABLE_MODELS['gpt-3.5-turbo'])
        
        payload = {
            "model": model_id,
            "messages": msgs,
            "temperature": 0.9,
            "max_tokens": 400
        }
        
        response = requests.post(
            f"{OPENROUTER_BASE_URL}/chat/completions",
            headers=OPENROUTER_HEADERS,
            json=payload
        )
        response.raise_for_status()
        
        response_data = response.json()
        content = response_data['choices'][0]['message']['content'].strip()
        
        msgs.append({"role": "assistant", "content": content})
        
        # Memory management: keep last 10 exchanges plus system prompt
        if len(msgs) > 21:  # system prompt + 20 messages (10 exchanges)
            msgs[1:3] = []  # remove oldest exchange (keep system prompt)
            
        return content
        
    except requests.exceptions.RequestException as e:
        logging.error(f"API request error in {speaker}'s response: {str(e)}")
        return f"[Error generating {speaker}'s response: API request failed. Retrying...]"
    except (KeyError, IndexError) as e:
        logging.error(f"Response parsing error in {speaker}'s response: {str(e)}")
        return f"[Error parsing {speaker}'s response. Retrying...]"
    except Exception as e:
        logging.error(f"Unexpected error in {speaker}'s response: {str(e)}")
        return f"[Error generating {speaker}'s response: {str(e)}]"

def simulate_conversation(initial_topic: str, rounds: int = 10, model: str = 'gpt-3.5-turbo') -> None:
    """
    Simulate a conversation between Einstein and Musk on any given topic.
    
    Args:
        initial_topic (str): The topic to discuss
        rounds (int): Number of conversation rounds (default: 10)
        model (str): Model to use from AVAILABLE_MODELS (default: 'gpt-3.5-turbo')
    """
    prompt = initial_topic
    model_id = AVAILABLE_MODELS.get(model, AVAILABLE_MODELS['gpt-3.5-turbo'])
    logging.info(f"Conversation topic: {initial_topic}")
    logging.info(f"Using model: {model_id}")
    
    # Initialize markdown file with header
    write_to_markdown(f"""# Conversation between Einstein and Musk
## Topic: {initial_topic}
*Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
*Using model: {model_id}*

""", mode='w')

    for round in range(1, rounds + 1):
        try:
            # Einstein's turn
            einstein_response = getResponse(msgs_einstein, prompt, model, "Einstein")
            print(f"\n[Round {round}]")
            print(f"Einstein: {einstein_response}")
            logging.info(f"[Round {round}] Einstein: {einstein_response}")
            write_to_markdown(f"### Round {round}\n\n**Einstein**: {einstein_response}\n")

            # Pause to avoid rate limits
            time.sleep(5)

            # Musk's turn
            musk_response = getResponse(msgs_musk, einstein_response, model, "Musk")
            print(f"\nMusk: {musk_response}")
            logging.info(f"Musk: {musk_response}")
            write_to_markdown(f"**Musk**: {musk_response}\n")

            # Next prompt is Musk's response
            prompt = musk_response

            # Longer pause between rounds
            time.sleep(10)

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:  # Rate limit error
                wait_time = 60  # Default wait time
                try:
                    wait_time = int(e.response.headers.get('Retry-After', 60))
                except (ValueError, TypeError):
                    pass
                print(f"\nRate limit reached. Waiting for {wait_time} seconds...")
                time.sleep(wait_time + 1)
                continue
            raise

        except Exception as e:
            logging.error(f"Error in round {round}: {str(e)}")
            print(f"\nError occurred: {str(e)}. Continuing to next round...")
            continue

def list_available_models() -> None:
    """Print all available models with their IDs"""
    print("\nAvailable models:")
    for short_name, full_id in AVAILABLE_MODELS.items():
        print(f"- {short_name}: {full_id}")
    print()

if __name__ == "__main__":
    # Example usage
    initial_topic = "singularity with superintelligent AI"
    selected_model = 'deepseek' # 'gpt-3.5-turbo'  # Can be changed to any key in AVAILABLE_MODELS
    
    print("\n=== Available Models ===")
    list_available_models()
    
    print("\n=== Starting Einstein-Musk Dialogue ===")
    print(f"Topic: {initial_topic}")
    print(f"Using model: {AVAILABLE_MODELS[selected_model]}\n")
    
    simulate_conversation(
        initial_topic=initial_topic,
        rounds=10,
        model=selected_model
    )

    print("\n=== Conversation Complete ===")
    print(f"Conversation saved to: {md_filename}")
    print(f"Debug log saved to: {log_filename}")
    
    # Add footer to markdown file
    write_to_markdown("\n---\n*Conversation ended*")
