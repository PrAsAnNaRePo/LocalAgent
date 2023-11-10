from localagent.initialize_agents import CreateAgent
from metaphor_python import Metaphor
import os

metaphor = Metaphor(os.environ.get("METAPHOR_API_KEY"))

## buld a actual function to search the web.
def search(search_query: str) -> dict:
    response = metaphor.search(
                search_query,
                num_results=1,
                use_autoprompt=True
            )
    return f"{response.autoprompt_string}\n{str(response.get_contents())}"

tools = [
    {
        'name_for_human': 'google search',
        'name_for_model': 'google_search',
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
    }
]

agent = CreateAgent(
    webui_url='ws://127.0.0.1:5005/api/v1/stream',
    tools=tools,
    verbose=True
)

agent.go_flow('when openai was founded?')