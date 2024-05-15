from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain_community.llms import OpenAI
from langchain.prompts import PromptTemplate

import os

embedding_model = OpenAIEmbeddings()

vector_store = FAISS.load_local("../faiss_pymigbench_index", embedding_model, allow_dangerous_deserialization=True)

llm = OpenAI(model_name="gpt-3.5-turbo-instruct")

template = """
You are given the following example transformations (provided in diff format) for rewriting Python code snippets. Added code is prefixed by +, and removed code prefixed by -.:
{context}

From these diffs, answer the following question, but apply the same transformations to your answer (remove code prefixed with -, and add the code prefixed with +, but do not format your answer as a diff): {question}
"""


def ask_question(query):
    print("Question:", query)
    retrieved_docs = vector_store.similarity_search(query, k=3)

    formatted_context = "\n".join([doc.page_content[:2000] for doc in retrieved_docs])
    final_prompt = template.format(context=formatted_context, question=query)

    print('===================')
    print("\nPrompt to LLM")
    print(final_prompt[:300] + '...' if len(final_prompt) > 300 else final_prompt, flush=True)
    print("Generated Answer:")
    rag_response = llm.invoke(final_prompt)
    print(rag_response)
    print('===================', flush=True)

    # if we didn't use RAG,
    no_rag_response = llm.invoke(query)
    # print('response without RAG:')
    # print(no_rag_response)
    # print('===================')
    return (rag_response, no_rag_response)


# ask_question("""
# Python XML get immediate child elements only
#              """)

import csv


def answer_generated_from_llm(query_folder):
    entries = os.listdir(query_folder)
    queries = [entry for entry in entries if os.path.isfile(os.path.join(query_folder, entry))]
    for query in queries:
        print("query:", query)
        with open(os.path.join(query_folder, query), 'r') as i_f, \
                open('response_rag.csv', 'w+') as o_f_rag, \
                open('response_no_rag.csv', 'w+') as o_f_no_rag, \
                open('query_responses.csv', 'w+') as full:
            for reader in i_f:
                writer_rag = csv.writer(o_f_rag)
                writer_no_rag = csv.writer(o_f_no_rag)
                writer_full = csv.writer(full)

                print('===================')
                rag, no_rag = ask_question(reader)

                writer_rag.writerow(rag)
                writer_no_rag.writerow(no_rag)
                writer_full.writerow([reader, rag, no_rag])


answer_generated_from_llm("/mnt/ssd/jiyuan/toy_llm_rewrites/questions_api_migration/langchain_question")
