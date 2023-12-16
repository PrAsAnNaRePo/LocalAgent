import json
from localagent.knowledge_base import KnowledgeBase
from localagent.utils import get_prompt_from_template, assistant_message, internal_monologue, important_message, clear_line, warning_message
from localagent.interpreter import Interpreter
from localagent.gen import stream_run, run, ollama_generate
from rich.console import Console

console = Console()

import warnings
warnings.filterwarnings("ignore")


class CreateAgent:
    def __init__(
            self,
            webui_url: str=None,
            ollama_model_name:str = None,
            system_prompt: str = None,
            system_:str = '',
            human_:str = 'GPT4 User',
            assistant_:str = "GPT4 Assistant",
            eos_token:str = '<|end_of_turn|>',
            tools: list[dict] = None,
            use_codeinterpreter: bool = False,
            interpreter_max_try:int = 3,
            knowledge_base: KnowledgeBase = None,
            stream:bool = False,
            verbose:bool = False,
    ) -> None:
        assert webui_url is not None or ollama_model_name is not None, 'Either webui_url or ollama_model_name should be given.'
        self.webui_url = webui_url
        self.olla_model_name = ollama_model_name
        self.stream = stream
        if webui_url is not None:       
            if webui_url.startswith('http'):
                self.stream = False
                self.webui_url = webui_url+'/v1/generate'
                if verbose:
                    important_message('agent initialized with non stream, If you want to start agent with streaming pass the streaming uri instead.')
            elif webui_url.startswith('ws'):
                self.stream = True
                self.webui_url = webui_url
                if verbose:
                    important_message('agent initialized with stream, If you want to start agent with non streaming pass the regular api uri instead.')
        
        self.system_prompt = system_prompt
        self.tools = tools
        self.system_ = system_
        self.human_ = human_
        self.assistant_ = assistant_
        self.eos_token = eos_token
        self.use_codeinterpreter = use_codeinterpreter
        self.knowledge_base = knowledge_base
        self.verbose = verbose

        self.history = []
        if verbose:
            important_message(f'Agent initialized with stream={self.stream}')
        if not system_prompt:
            if verbose:
                important_message('No system prompt given, creating default system prompt.')
            self.system_prompt = f'{self.system_}\nYou are an AI assistant\n'
        
        if not self.tools:
            self.tools = []

        if knowledge_base is not None:
            if verbose:
                important_message('Knowledge base is given, creating knowledge_retrival tool.')
            self.system_prompt += 'You have given a Knowledge document where you able to access contents in that using knowledge_retrival tool.\n'
            self.tools.append(
                {
                    'name_for_human':
                    'Knowledge retrival',
                    'name_for_model':
                    'knowledge_retrival',
                    'description_for_model':
                    'knowledge_retrival is a tool used to retrive any information from the Knowledge document.',
                    'parameters': [{
                        'name': 'query',
                        'description': 'A query to search the specific information from document uploaded.',
                        'required': True,
                        'schema': {
                            'type': 'string'
                        },
                    }],
                }
            )

        if use_codeinterpreter:
            if verbose:
                important_message('Code interpreter is enabled, creating code_interpreter tool.')
            self.interpreter = Interpreter(
                exec={"name": 'ollama' if self.olla_model_name is not None else 'webui', "uri": self.olla_model_name if self.olla_model_name is not None else self.webui_url},
                max_try=interpreter_max_try,
                human_=human_,
                assistant_=assistant_,
                eos_token=eos_token,
                stream=self.stream,
            )
            self.tools.append(
                {
                    'name_for_human':
                    'code interpreter',
                    'name_for_model':
                    'code_interpreter',
                    'description_for_model':
                    'Code Interpreter enables the assistant to write and run code. code_interpreter is sensitive, it need all the information about the task to perform it such as path to file, correct file name, any other information required to perform the task.',
                    'parameters': [{
                        'name': 'task',
                        'description': 'Describe the task clearly and briefly to the code interpreter to run the code and returns the output with you.',
                        'required': True,
                        'schema': {
                            'type': 'string'
                        },
                    }],
                }
            )

        if len(self.tools) != 0:
            self.system_prompt = self.create_prompt_with_tools()

    
    def create_prompt_with_tools(self):
        tool_desc = """{name_for_model}: Call this tool to interact with the {name_for_human} API. What is the {name_for_human} API useful for? {description_for_model} Parameters: {parameters} Format the arguments as a JSON object."""
        tool_descs = []
        tool_names = []
        for info in self.tools:
            tool_descs.append(
                tool_desc.format(
                    name_for_model=info['name_for_model'],
                    name_for_human=info['name_for_human'],
                    description_for_model=info['description_for_model'],
                    parameters=json.dumps(
                        info['parameters'], ensure_ascii=False),
                )
            )
            tool_names.append(info['name_for_model'])

        tool_descs = '\n\n'.join(tool_descs)
        tool_names = ','.join(tool_names)
        if self.use_codeinterpreter:
            react_prompt = f"""{self.system_}
YOUR PERSONA:
{self.system_prompt}

You have access to these following tools:
{tool_descs}

Use the following format:

Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can be repeated zero or more times)
Thought: I now know the final answer
Message: the final answer to the original input question

{self.human_}: hey, you UP!{self.eos_token}{self.assistant_}:
Thought: User asking about my availability, I should respond by telling i'm available for assistance. So no need to use any tool for this.
Message: Hey there! I'm just here. How can I help you today?{self.eos_token}
{self.human_}: Create a folder called Project-1 and create a file called temp.py in it.{self.eos_token}{self.assistant_}:
Thought: The user wants to create a folder and a file in it, so I need to ask code_interpreter to create folder and file.
Action: code_interpreter
Action Input: {{"task": "Create a folder called Project-1 in the current folder and create a file called temp.py in Project-1 folder."}}{self.eos_token}
{self.human_}: This is code interpreter (not user). Created a folder called Project-1 and created a file called temp.py inside Project-1.
Thought: Now the files are created. I should tell the user about it. No need to use any tools again.
Message: Created a folder and file in it. I'm here to help you if you need any assistance.{self.eos_token}
"""
        else:
            react_prompt = f"""{self.system_}
YOUR PERSONA:
{self.system_prompt}

{tool_descs}

Use the following format:

Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action (in json format)
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can be repeated zero or more times)
Thought: I now know the final answer
Message: the final answer to the original input question

{self.human_}: hey, you UP!{self.eos_token}{self.assistant_}:
Thought: User asking about my availability, I should respond by telling i'm available for assistance. So no need to use any tool for this.
Message: Hey there! I'm just here. How can I help you today?{self.eos_token}"""
            
        return react_prompt
    
    def go_flow(self, prompt):
        self.history.append({'role':'user', 'content':prompt})
        done = False
        while not done:
            prompt = get_prompt_from_template(self.system_prompt, self.history, self.human_, self.assistant_, self.eos_token)
            
            if len(self.tools) != 0:
                if self.stream:
                    raw_response = stream_run(self.webui_url, prompt, force_model=True) if self.webui_url else ollama_generate(self.olla_model_name, template=prompt, force_model=True, stream=True)[0].replace(self.eos_token, "").replace(self.eos_token[:-1], "")
                else:
                    with console.status("[bold cyan]Thinking...") as status:
                        raw_response = run(self.webui_url, prompt, force_model=True) if self.webui_url else ollama_generate(self.olla_model_name, template=prompt)[0].replace(self.eos_token, "").replace(self.eos_token[:-1], "")
            else:
                if self.stream:
                    raw_response = stream_run(self.webui_url, prompt) if self.webui_url else ollama_generate(self.olla_model_name, template=prompt, stream=True)[0].replace(self.eos_token, "").replace(self.eos_token[:-1], "")
                else:
                    with console.status("[bold cyan]Thinking...") as status:
                        raw_response = str(run(self.webui_url, prompt)) if self.webui_url else ollama_generate(model_name=self.olla_model_name, template=prompt)[0].replace(self.eos_token, "").replace(self.eos_token[:-1], "")

            self.history.append({"role": "assistant", "content": raw_response})

            if len(self.tools) != 0:
                response = raw_response.strip().split('\n')

                thought, message, action, action_inp = None, None, None, None
                for i in response:
                    if i.startswith('Thought:'):
                        thought = i.replace('Thought: ', '')
                    if i.startswith('Message:'):
                        message = i.replace('Message: ', '')
                    if i.startswith('Action:'):
                        action = i.replace('Action: ', '')
                if action:
                    start_index = raw_response.find('{')
                    end_index = raw_response.rfind('}')
                    json_part = raw_response[start_index:end_index + 1]
                    action_inp = json.loads(json_part)

                internal_monologue(thought)

                if message:
                    assistant_message(message)
                    print('\n')
                    done = True
                else:
                    for tool in self.tools:
                        if action == tool['name_for_model']:
                            func_args = action_inp
                            if action == 'code_interpreter':
                                func_out = f"This is code_interpreter tool (not user). Here is the result for your task:\n{self.interpreter(**func_args)}\nTake this to user."
                                print('\n')
                            elif action == 'knowledge_retrival':
                                func_out = f"This is knowledge_retrival tool (not user). Here is the result for your query:\n{self.knowledge_base.create_similarity_search_docs(**func_args)}\nTake this to user."
                            else:
                                func = tool['function']

                                func_out = f"This is {tool['name_for_model']} tool (not user). Here is the result of your api call:\n{func(**func_args)}\nTake this to user."
                            
                            self.history.append({'role': 'user', 'content': func_out})

            else:
                assistant_message(raw_response)
                print('\n')
                done = True

    
    def clear_history(self):
        self.history = []
    
    def load_history(self, hist):
        self.history = hist