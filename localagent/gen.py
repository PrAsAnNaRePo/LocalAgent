import requests
import asyncio
import json
import sys
import os

try:
    import websockets
except ImportError:
    print("Websockets package not found. Make sure it's installed.")


def run(uri, prompt, force_model=False):
    if force_model:
        prompt += "\nThought:"
    request = {
        'prompt': prompt,
        'max_new_tokens': 500,
        'auto_max_new_tokens': False,
        'max_tokens_second': 0,
        'do_sample': True,
        'temperature': 0.01,
        'repetition_penalty': 1.24,
        'temperature': 0.1,
        'skip_special_tokens': True,
        'stopping_strings': ['<|end_of_turn|>', '<|im_end|>', 'Observation']
    }

    response = requests.post(uri, json=request)
    if response.status_code == 200:
        result = response.json()['results'][0]['text']
        return '\nThought:'+result if force_model else result
    

async def stream(uri, context, force_model=False):
    if force_model:
        context += "\nThought:"
    # Note: the selected defaults change from time to time.
    request = {
        'prompt': context,
        'max_new_tokens': 500,
        'auto_max_new_tokens': False,
        'max_tokens_second': 0,
        'do_sample': True,
        'temperature': 0.01,
        'skip_special_tokens': True,
        'stopping_strings': ['<|end_of_turn|>', '<|im_end|>', 'Observation']
    }

    async with websockets.connect(uri, ping_interval=None) as websocket:
        await websocket.send(json.dumps(request))

        while True:
            incoming_data = await websocket.recv()
            incoming_data = json.loads(incoming_data)

            match incoming_data['event']:
                case 'text_stream':
                    yield incoming_data['text']
                case 'stream_end':
                    return

async def print_response_stream(uri, prompt, force_model):
    tot_res = ''
    async for response in stream(uri, prompt, force_model):
        print(response, end='')
        sys.stdout.flush()
        tot_res += response
    return '\nThought:' + tot_res if force_model else tot_res

def stream_run(uri, prompt, force_model=False):
    return asyncio.run(print_response_stream(uri, prompt, force_model))

BASE_URL = os.environ.get('OLLAMA_HOST', 'http://localhost:11434')

def ollama_generate(model_name, prompt=None, system=None, template=None, stream=False, format="", context=None, options=None, callback=None, force_model=False):
    try:
        if template is not None and force_model:
            template += '\nThought:'
        url = f"{BASE_URL}/api/generate"
        payload = {
            "model": model_name, 
            "prompt": prompt, 
            "system": system, 
            "template": template, 
            "context": context, 
            "options": options,
            "format": format,
        }
        
        # Remove keys with None values
        payload = {k: v for k, v in payload.items() if v is not None}
        
        with requests.post(url, json=payload, stream=True) as response:
            response.raise_for_status()
            
            # Creating a variable to hold the context history of the final chunk
            final_context = None
            
            # Variable to hold concatenated response strings if no callback is provided
            full_response = ""

            # Iterating over the response line by line and displaying the details
            for line in response.iter_lines():
                if line:
                    # Parsing each line (JSON chunk) and extracting the details
                    chunk = json.loads(line)
                    
                    # If a callback function is provided, call it with the chunk
                    if callback:
                        callback(chunk)
                    else:
                        # If this is not the last chunk, add the "response" field value to full_response and print it
                        if not chunk.get("done"):
                            response_piece = chunk.get("response", "")
                            full_response += response_piece
                            if 'Observation' in full_response:
                                break
                            if stream:
                                print(response_piece, end="", flush=True)
                    
                    # Check if it's the last chunk (done is true)
                    if chunk.get("done"):
                        final_context = chunk.get("context")
            full_response = full_response.replace('Observation', '')
            # Return the full response and the final context
            return '\nThought:'+full_response if force_model else full_response, final_context
        
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None, None