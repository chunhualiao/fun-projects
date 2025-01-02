import openai
import time
import json
import logging
from datetime import datetime

# Set up logging with timestamp
logging.basicConfig(
    filename=f'einstein_musk_conversation_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

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
        
        response = openai.ChatCompletion.create(
            model=selected_model,
            messages=msgs,
            temperature=0.9,
            max_tokens=400
        )['choices'][0]['message']['content'].strip()

        msgs.append({"role": "assistant", "content": response})
        
        # Memory management: keep last 10 exchanges plus system prompt
        if len(msgs) > 21:  # system prompt + 20 messages (10 exchanges)
            msgs[1:3] = []  # remove oldest exchange
            
        return response
        
    except Exception as e:
        logging.error(f"Error in {speaker}'s response: {str(e)}")
        return f"[Error generating {speaker}'s response. Retrying...]"

def simulate_conversation(initial_topic: str, rounds: int = 10, model: str = 'gpt-4'):
    """
    Simulate a conversation between Einstein and Musk on any given topic.
    """
    prompt = initial_topic
    logging.info(f"Conversation topic: {initial_topic}")
    
    for round in range(1, rounds + 1):
        try:
            # Einstein's turn
            einstein_response = getResponse(msgs_einstein, prompt, model, "Einstein")
            print(f"\n[Round {round}]")
            print(f"Einstein: {einstein_response}")
            logging.info(f"[Round {round}] Einstein: {einstein_response}")
            
            # Pause to avoid rate limits
            time.sleep(5)
            
            # Musk's turn
            musk_response = getResponse(msgs_musk, einstein_response, model, "Musk")
            print(f"\nMusk: {musk_response}")
            logging.info(f"Musk: {musk_response}")
            
            # Next prompt is Musk's response
            prompt = musk_response
            
            # Longer pause between rounds
            time.sleep(10)
            
        except openai.error.RateLimitError as e:
            wait_time = e.retry_after if hasattr(e, 'retry_after') else 60
            print(f"\nRate limit reached. Waiting for {wait_time} seconds...")
            time.sleep(wait_time + 1)
            continue
        
        except Exception as e:
            logging.error(f"Error in round {round}: {str(e)}")
            print(f"\nError occurred: {str(e)}. Continuing to next round...")
            continue

if __name__ == "__main__":
    # Example usage
    initial_topic = "singularity with superintelligent AI"
    What are your thoughts on the relationship between consciousness and quantum mechanics, 
    and how might this understanding affect the development of artificial intelligence?
    """
    
    print("\n=== Starting Einstein-Musk Dialogue ===")
    print(f"Topic: {initial_topic}\n")
    
    simulate_conversation(
        initial_topic=initial_topic,
        rounds=10,  # Number of exchanges
        model='gpt-4o'  # Or any other available model
    )
    
    print("\n=== Conversation Complete ===")
    print("Full conversation log has been saved.")
