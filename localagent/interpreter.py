import subprocess
import sys
from localagent.utils import get_prompt_from_template, internal_monologue
from localagent.gen import run, stream_run, ollama_generate
from rich.console import Console

console = Console()

CODE_INTERPRETER = """You are Open Interpreter, a world-class programmer that can complete any goal by executing code.
First, write a plan. **Always recap the plan between each code block**.
When you execute code, it will be executed **on the user's machine**. The user has given you **full and complete permission** to execute any code necessary to complete the task.
If you want to send data between programming languages, save the data to a txt or json.
You can access the internet. Run **any code** to achieve the goal, and if at first you don't succeed, try again and again.
You can install new packages.
When a user refers to a filename, they're likely referring to an existing file in the directory you're currently executing code in.
Write messages to the user in Markdown.
In general, try to **make plans** with as few steps as possible. Remember that one code block is considered as a single file and you can't able to access the variable from first code blocks in the second one.
You are capable of **any** task. Don't install libraries using '!' in the python code block instead use seperate bash code block.
As a open interpreter you should mostly respond with codes more than a text. Always tries to print the things up so you can know them via output.
"""

def extract_code(string):
    code_blocks = []
    parts = string.split("```")
    for i in range(1, len(parts), 2):
        lines = parts[i].split("\n")
        lang = lines[0]
        code = "\n".join(lines[1:])
        code_blocks.append((lang, code))
    return code_blocks

class Interpreter:
    def __init__(self, exec, max_try, human_, assistant_, eos_token, stream=False) -> None:
        self.history = []
        self.exec = exec
        self.max_try = max_try
        self.human_ = human_
        self.assistant_ = assistant_
        self.eos_token = eos_token
        self.stream = stream
    
    def execute_code(self, lang, code, timeout=10):
        if lang.lower() == 'python':
            try:
                output = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, timeout=timeout)
            except subprocess.TimeoutExpired:
                print(f"Execution of Python code timed out after {timeout} seconds.")
                return None
        elif lang.lower() == 'bash':
            try:
                output = subprocess.run(code, shell=True, capture_output=True, text=True, timeout=timeout)
            except subprocess.TimeoutExpired:
                print(f"Execution of Bash code timed out after {timeout} seconds.")
                return None
        else:
            print('Only supported python and ')
            return None
        
        return output
    
    def __call__(self, task):
        print('\n')
        internal_monologue("Interpreter is executing the code...\n")
        self.history.append({'role':'user', 'content':task})
        count = 1
        while True and count <= self.max_try:
            prompt = get_prompt_from_template(CODE_INTERPRETER, self.history, self.human_, self.assistant_, self.eos_token)
            if self.exec['name'] == 'webui':
                if self.stream:
                    response = stream_run(self.exec['uri'], prompt)
                else:
                    with console.status("[bold cyan]Executing codes...") as status:
                        response = run(self.exec['uri'], prompt)
            elif self.exec['name'] == 'ollama':
                if self.stream:
                    response = ollama_generate(model_name=self.exec['uri'], template=prompt, stream=True)[0]
                else:
                    with console.status("[bold cyan]Executing codes...") as status:
                        response = ollama_generate(model_name=self.exec['uri'], template=prompt)[0]
            else:
                raise Exception('Only supported webui and ollama.')
            count += 1
            
            self.history.append({'role':'user', 'content':response})
            code_blocks = extract_code(response)
            final_code_output = ''
            outs = []
            if len(code_blocks) > 0:
                for n, i in enumerate(code_blocks):
                    lang, code = i
                    output = self.execute_code(lang, code)
                    if output.returncode == 0:
                        outs.append(0)
                        final_code_output += f"\nThe output of the block number #{n}:\n{output.stdout}"
                    if output.returncode == 1:
                        outs.append(1)
                        final_code_output += f"\nThe block number #{n} got error:\n{output.stderr}.\nPlease check out and come up with better code."
                self.history.append({'role':'user', 'content':final_code_output})
                if 1 not in outs:
                    return final_code_output
                else:
                    print('\n')
            else:
                print('retrying...')
                self.history.pop()
                
        return "Sorry, can't able to make this now."

