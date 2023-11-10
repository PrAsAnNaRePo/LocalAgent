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