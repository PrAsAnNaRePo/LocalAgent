import os
import sys
from colorama import Fore, Style, init
from rich.markdown import Markdown
from rich import print as Print

init(autoreset=True)

def get_prompt_from_template(system, history, human_, assistant_, eos_token):
        for i in history:
            if i['role'] == 'user':
                system += f'{human_}{i["content"]}{eos_token}'
            if i['role'] == 'assistant':
                system += f'{assistant_}{i["content"]}{eos_token}'

        if history[-1]['role'] == 'user':
            system += f'{assistant_}'

        return system

def important_message(msg):
    print(f"{Fore.MAGENTA}{Style.BRIGHT}{msg}{Style.RESET_ALL}")

def warning_message(msg):
    print(f"{Fore.RED}{Style.BRIGHT}{msg}{Style.RESET_ALL}")

def internal_monologue(msg):
    # ANSI escape code for italic is '\x1B[3m'
    print(f"\x1B[3m{Fore.LIGHTBLACK_EX}💭 {msg}{Style.RESET_ALL}")

def assistant_message(msg):
    Print(Markdown(f"{Fore.YELLOW}{Style.BRIGHT}🤖 {Fore.YELLOW}{msg}{Style.RESET_ALL}"))

def user_message(msg):
    print(f"{Fore.YELLOW}{Style.BRIGHT}🧑 {Fore.MAGENTA}{msg}{Style.RESET_ALL}")

def clear_line():
    if os.name == "nt":  # for windows
        console.print("\033[A\033[K", end="")
    else:  # for linux
        sys.stdout.write("\033[2K\033[G")
        sys.stdout.flush()
