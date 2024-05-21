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

Answer: 
"""


def ask_question(query):
    retrieved_docs = vector_store.similarity_search(query,k=3)

    formatted_context = "\n".join([doc.page_content[:2000] for doc in retrieved_docs])
    final_prompt = template.format(context=formatted_context, question=query)

    

    print('===================')
    print("\nPrompt to LLM")
    print(final_prompt[:300] + '...' if len(final_prompt) > 300 else final_prompt, flush=True)
    print("Generated Answer:")
    rag_response = llm(final_prompt)
    print(rag_response)
    print('===================', flush=True)

    # if we didn't use RAG,
    no_rag_response = llm(query)
    # print('response without RAG:')
    # print(no_rag_response)
    # print('===================')
    return (rag_response, no_rag_response)

# ask_question("""
# Python XML get immediate child elements only
#              """)

import csv


with open('query.csv', 'r') as i_f,\
        open('response_rag.csv', 'w+') as o_f_rag,\
        open('response_no_rag.csv', 'w+') as o_f_no_rag,\
        open('query_responses.csv', 'w+') as full:
    
    reader = csv.reader(i_f)
    writer_rag = csv.writer(o_f_rag)
    writer_no_rag = csv.writer(o_f_no_rag)
    writer_full = csv.writer(full)

    next(reader)
    print('===================')
    for i, row in enumerate(reader):
        rag, no_rag = ask_question(row[0])

        writer_rag.writerow(rag)
        writer_no_rag.writerow(no_rag)
        writer_full.writerow([row[0], rag, no_rag])
