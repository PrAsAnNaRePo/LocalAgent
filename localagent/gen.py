import requests
import asyncio
import json
import sys

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