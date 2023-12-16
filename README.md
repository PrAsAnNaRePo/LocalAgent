# Local-Agent: A open implementation of GPT agents
![Twitter Follow](https://img.shields.io/twitter/follow/prasanna448?style=social)

localagent empowers you to craft Large Language Model (LLM) Agents tailored to your needs, utilizing your own functions and tools alongside **local open LLMs**. Unleash your creative ideas to effortlessly develop diverse agents with localagent. It seamlessly integrates with any openly available LLM and accommodates a wide range of tools, providing flexibility and ease of use.

### Demo:
https://github.com/PrAsAnNaRePo/LocalAgent/assets/98259409/229b47df-226f-453c-81a6-5d7b69fbee06

## Table of Contents

- [Local Agent: A tool for creating agents with local llms.](#local-agent)
  - [Table of Contents](#table-of-contents)
  - [🚀 Features](#🚀-features)
  - [📋 Requirements](#📋-requirements)
  - [💾 Installation](#💾-installation)
  - [🔧 Usage](#🔧-usage)
  - [Setup webui api](#setup-webui-api)
  - [Running agents](#running-agents)
  - [Native Code Interpreter](#native-code-interpreter)
  - [Auto Knowledge Retrival](#auto-knowledge-retrival)
  - [Using different llms](#using-different-llms)
  - [🔍 Custom tools](#custom-tools)
  - [🐦 Connect with Us on Twitter](#🐦-connect-with-us-on-twitter)

## 🚀 Features

- Create Agents with any tools and api calls.
- Comes with native code interpreter support.
- Also it allow to easlily work with document as Retrival-knowledge.
- Supports streaming and non-streaming generation.

## 📋 Requirements
- [Python 3.7 or later](https://www.tutorialspoint.com/how-to-install-python-in-windows)

Optional:
- HuggingFace API key

## 💾 Installation

To install Local-Agent, follow these steps:

well, just,
```
pip install localagent
```
## 🔧 Usage

### Using Agents with textgeneration webui.
1. Create any kinda agent using `CreateAgent` class from `localagent.initialize_agents`

## Setup webui api
Use open LLMs in localagent using [textgeneration](https://github.com/oobabooga/text-generation-webui) webui api.

1. Clone textgen webui.
```
git clone https://github.com/oobabooga/text-generation-webui.git
```
2. heads up to main folder and run the following command to start the webui locally to download open models from huggingface.
```
python3 server.py
```

3. Select capable model and download it. (This package `localagent` is primarily uses [openchat-3.5](https://huggingface.co/openchat/openchat_3.5) model)

## Running agents

- Start the llm with textgeneration webui as *API*. change directory to textgeneration webui and type the following command
```
python3 server.py --api --api-blocking-port 5050 --model openchat_3.5.Q4_K_M.gguf --n-gpu-layers 20 --n_batch 512
```
  #### NOTE:
  The args such as `--n-gpu-layers` and `--n_batch` require GPU support.

- Create simple agent by typing the following commands.
```python
from localagent.initialize_agents import CreateAgent

agent = CreateAgent(
    webui_url='ws://127.0.0.1:5005/api/v1/stream', # copy and paste the url you got in the above step.
    verbose=True
)
```
- To run the agent with streaming capablity pass the streaming uri (ends with stream in the url) or To run with non-streaming just pass the url starts with http (for example: `http://127.0.0.1:5050/api`)

### Using Agents with ollama.
1. Install [ollama](https://ollama.ai/)
2. download any models from cli using ollama. You can download any model you want.
```
ollama run dolphin2.2-mistral
```
3. That's all you need to setup for agents with ollama. Lets create a agent with it.
```python
from localagent.initialize_agents import CreateAgent

agent = CreateAgent(
    ollama_model_name='dolphin2.2-mistral'
)
```

## Native Code Interpreter

You can able to create a new tool as a code-interpreter, but now its need in a lot places, so local-agent comes with it!
here is the example:
```python
from localagent.initialize_agents import CreateAgent

agent = CreateAgent(
    webui_url='ws://127.0.0.1:5005/api/v1/stream',
    use_codeinterpreter=True, # That's it
    verbose=True
)
agent.go_flow('Checkout my ip address in the system.')
```

## Auto Knowledge Retrival

- Lot of agents need a knowledge of thier own company or whatever, So use can able to set multiple files as a knowledge for llm. The Agent decides when it needs the information in it.
```python
from localagent.initialize_agents import CreateAgent
from localagent.knowledge_base import KnowledgeBase

knowledge = KnowledgeBase('/home/nnpy/Downloads/Retrival_files')

agent = CreateAgent(
    webui_url='ws://127.0.0.1:5005/api/v1/stream',
    system_prompt="I have given a study material for you to answer questions from that.",
    knowledge_base=knowledge,
    verbose=True
)

agent.go_flow('What is the 2nd Experiment?')
```
- You need Huggingface api key to work with knowledge retrival. follow the steps belo to set HF api token.

### Setting up environment variables

```
export HUGGINGFACEHUB_API_TOKEN=hf_xxxxxxxx
```

## Using different llms
### working with webui:
- To use different llms, make sure you have downloaded the model in textgen webui.
- Use the command for the model you want to use: 
`python3 server.py --api --api-blocking-port 5050 --model <Model name here> --n-gpu-layers 20 --n_batch 512`
- While creating the agent class, make sure that use have pass a correct human, assistant, and eos tokens. For example.
```python
from localagent.initialize_agents import CreateAgent

agent = CreateAgent(
    webui_url='ws://127.0.0.1:5005/api/v1/stream',
    system_prompt="I have given a study material for you to answer questions from that.",
    use_codeinterpreter=True,
    human_ = '<|im_start|>user\n',
    assistant_ = '<|im_start|>assistant\n',
    eos_token = '<|im_end|>',
    verbose=True
)
```
### working with ollama:
- This example shows how to use [OpenHermes 2.5](https://huggingface.co/teknium/OpenHermes-2.5-Mistral-7B) with ollama!
- Make sure to pull the model before executing the code.
```python
from localagent.initialize_agents import CreateAgent

agent = CreateAgent(
    ollama_model_name='openhermes2.5-mistral',
    use_codeinterpreter=True,
    verbose=True,
    stream=True,
    system_="<|im_start|>system\n",
    human_='<|im_start|>user\n',
    assistant_='<|im_start|>assistant\n')

```
- Feel free to adjust the `system_`, `human_`, `assistant_` parameters depends upon the model.

## Custom tools
You can able to build agents with your own tools.
```python
from localagent.initialize_agents import CreateAgent

def search(query): # arg name should be same as the parameter name in json.
  # do the stuff.
  return 'result' # return the result of the tools as a string.

tools = [
    {
        'name_for_human': 'google search',
        'name_for_model': 'google_search',
        'description_for_model':
        'google Search is a general search engine that can be used to access the Internet, query encyclopedia knowledge, understand current affairs news, etc. Use this API only you are not familliar with the topic or any current trends',
        'parameters': [{
            'name': 'query',
            'description': 'Search for a keyword or phrase',
            'required': True,
            'schema': {
                'type': 'string'
            },
        }],
        "function": search
    }
]

agent = CreateAgent(
    webui_url='ws://127.0.0.1:5005/api/v1/stream',
    tools=tools,
    verbose=True
)

agent.go_flow('when did openai was founded?')
```

Let's create full-fledged AI assistant.
```python
import os
from metaphor_python import Metaphor
from localagent import CreateAgent

metaphor = Metaphor(os.environ.get("METAPHOR_API_KEY"))

def search(search_query: str) -> dict:
    response = metaphor.search(
                search_query,
                num_results=1,
                use_autoprompt=True
            )
    return f"{response.autoprompt_string}\n{str(response.get_contents())}"

def update_memory(data:str):
    with open("memory.txt", "a") as f:
        f.write(data+'\n')
    return f"Updated memory with {data}."

tools = [
    {
        'name_for_human':
        'google search',
        'name_for_model':
        'google_search',
        'description_for_model':
        'google Search is a general search engine that can be used to access the Internet, query encyclopedia knowledge, understand current affairs news, etc. Use this API only you are not familliar with the topic or any current trends',
        'parameters': [{
            'name': 'search_query',
            'description': 'Search for a keyword or phrase',
            'required': True,
            'schema': {
                'type': 'string'
            },
        }],
        "function": search
    },
    {
        'name_for_human':
        'Memory',
        'name_for_model':
        'update_memory',
        'description_for_model':
        'update_memory is a tool that helps to store important info in local permanent memory.',
        'parameters': [{
            'name': 'data',
            'description': 'Enter data to store such as user name, remainders etc.',
            'required': True,
            'schema': {
                'type': 'string'
            },
        }],
        "function": update_memory
    },
]

agent = CreateAgent(
    system_prompt="You are a personal assistant who has wide knowledge in world topics.",
    webui_url='ws://127.0.0.1:5005/api/v1/stream',
    tools=tools,
    use_codeinterpreter=True,
)

agent.go_flow('Check out my IP address.')
```
## 🐦 Connect with Us on Twitter 

Stay up-to-date with the latest news, updates, and insights about Local Agent by following our Twitter accounts. Engage with the developer and the AI's own account for interesting discussions, project updates, and more.

We look forward to connecting with you and hearing your thoughts, ideas, and experiences with Local Agent. Join us on Twitter and let's explore the future of AI together!
