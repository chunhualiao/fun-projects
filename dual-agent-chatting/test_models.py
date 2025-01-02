import os
import requests
import time
from datetime import datetime

# OpenRouter configuration
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY environment variable is required")

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
OPENROUTER_HEADERS = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "HTTP-Referer": "https://github.com/chunhualiao",
    "Content-Type": "application/json"
}

# Available models to test (testing most reliable models first)
MODELS_TO_TEST = {
    "gpt-3.5-turbo": "openai/gpt-3.5-turbo",
    "claude-2": "anthropic/claude-2",
    "deepseek": "deepseek/deepseek-chat",
    "gemini": "google/gemini-2.0-flash-thinking-exp:free"
}

def test_model(model_name: str, model_id: str) -> dict:
    """Test a single model with a simple prompt"""
    print(f"\nTesting {model_name} ({model_id})...")
    
    try:
        payload = {
            "model": model_id,
            "messages": [
                {"role": "user", "content": "Say 'Hello, World!' and briefly introduce yourself."}
            ],
            "temperature": 0.7,
            "max_tokens": 150
        }
        
        start_time = time.time()
        response = requests.post(
            f"{OPENROUTER_BASE_URL}/chat/completions",
            headers=OPENROUTER_HEADERS,
            json=payload,
            timeout=30  # 30 second timeout
        )
        response_time = time.time() - start_time
        
        response.raise_for_status()
        response_data = response.json()
        
        # Log the raw response for debugging
        print(f"Raw response: {response_data}")
        
        # Handle different response formats
        if 'choices' in response_data:
            content = response_data['choices'][0]['message']['content'].strip()
            return {
                "status": "success",
                "response_time": f"{response_time:.2f}s",
                "response": content
            }
        elif 'error' in response_data:
            return {
                "status": "error",
                "error": response_data['error'].get('message', 'Unknown error')
            }
        else:
            return {
                "status": "error",
                "error": f"Unexpected response format: {response_data}"
            }
            
    except requests.exceptions.Timeout:
        return {
            "status": "timeout",
            "error": "Request timed out after 30 seconds"
        }
    except requests.exceptions.RequestException as e:
        return {
            "status": "error",
            "error": f"Request error: {str(e)}"
        }
    except KeyError as e:
        return {
            "status": "error",
            "error": f"Response parsing error: {str(e)}"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": f"Unexpected error: {str(e)}"
        }

def main():
    # Create results directory if it doesn't exist
    results_dir = "model_tests"
    os.makedirs(results_dir, exist_ok=True)
    
    # Generate timestamp for the results file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = os.path.join(results_dir, f'model_test_results_{timestamp}.md')
    
    # Write header to results file
    with open(results_file, 'w') as f:
        f.write(f"# OpenRouter Models Test Results\n")
        f.write(f"*Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n")
    
    # Test each model
    for model_name, model_id in MODELS_TO_TEST.items():
        result = test_model(model_name, model_id)
        
        # Write results to file
        with open(results_file, 'a') as f:
            f.write(f"## {model_name}\n")
            f.write(f"**Model ID**: `{model_id}`\n")
            f.write(f"**Status**: {result['status']}\n")
            
            if result['status'] == 'success':
                f.write(f"**Response Time**: {result['response_time']}\n")
                f.write(f"**Response**:\n{result['response']}\n")
            else:
                f.write(f"**Error**: {result['error']}\n")
            
            f.write("\n---\n\n")
        
        # Print status to console
        print(f"Status: {result['status']}")
        if result['status'] == 'success':
            print(f"Response Time: {result['response_time']}")
            print(f"Response: {result['response'][:100]}...")  # Print first 100 chars
        else:
            print(f"Error: {result['error']}")
        
        # Wait between requests to avoid rate limits
        time.sleep(5)
    
    print(f"\nTest results saved to: {results_file}")

if __name__ == "__main__":
    main()
