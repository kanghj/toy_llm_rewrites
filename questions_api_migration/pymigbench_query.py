from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain_community.llms import OpenAI
from langchain.prompts import PromptTemplate

import os

# os.environ['OPENAI_API_KEY'] = 'key'

embedding_model = OpenAIEmbeddings()

vector_store = FAISS.load_local("faiss_pymigbench_index", embedding_model,allow_dangerous_deserialization=True)

llm = OpenAI(model_name="gpt-3.5-turbo-instruct") 

template = """
You are given the following example transformations (provided in diff format) for rewriting Python code snippets. Added code is prefixed by +, and removed code prefixed by -.:
{context}

From these diffs, answer the following question, but apply the same transformations to your answer (remove code prefixed with -, and add the code prefixed with +, but do not format your answer as a diff): {question}
"""


PROMPT = PromptTemplate(
    input_variables=["context", "question"],
    template=template
)


def ask_question(query):
    retrieved_docs = vector_store.similarity_search(query,k=3)

    formatted_context = "\n".join([doc.page_content[:2000] for doc in retrieved_docs])
    final_prompt = template.format(context=formatted_context, question=query)

    

    print('===================')
    print("\nPrompt to LLM")
    print(final_prompt)
    print("Generated Answer:")
    response = llm(final_prompt)
    print(response)
    print('===================')

    # if we didn't use RAG,
    response = llm(query)
    print('response without RAG:')
    print(response)
    print('===================')

ask_question("""
Python XML get immediate child elements only
             
        
             """)