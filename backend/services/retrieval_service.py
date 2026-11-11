from langchain_classic.chains.conversation.base import ConversationChain
from langchain_classic.memory import ConversationBufferWindowMemory, ConversationSummaryMemory
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama


llm = ChatOllama(
    model="llama3.2:3b",
    temperature=.9 # from 0-1. higher temp = more creativity
)






def get_memory_chain():

    memory = ConversationSummaryMemory(llm=llm)

    memory_prompt = ChatPromptTemplate.from_messages([
        ("system", "You give detailed information about boardgame."
                ),
        ("user", "Conversation History: {history}"
                 "Current Input: {input}")
    ])

    # Make and return a chain in the old fashioned way (NOT using LCEL)
    return ConversationChain(
        llm = llm,
        memory = memory,
        prompt = memory_prompt
    )