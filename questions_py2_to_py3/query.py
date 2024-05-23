from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate

from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

import os
import sys

embedding_model = OpenAIEmbeddings()

db = sys.argv[1]

model = sys.argv[2]

vector_store = FAISS.load_local(db, embedding_model, allow_dangerous_deserialization=True)

if model == 'gpt-3.5-turbo-instruct':
    from langchain_community.llms import OpenAI
    llm = OpenAI(model_name="gpt-3.5-turbo-instruct") 
elif model == 'gpt-4-turbo':
    from langchain_community.chat_models import ChatOpenAI
    llm = ChatOpenAI(model_name="gpt-4-turbo")

template = """
You are to answer questions in the style of a user on StackOverflow answering questions. You MUST provide a code snippet in your answer.
Ensure that all imports are included in the code.
You are given the following example transformations (provided in diff format) for rewriting code snippets in your response. Added code is prefixed by +, and removed code prefixed by -.:
{context}

Answer the following question, but transform your answer based on the above diffs/transformations (remove code prefixed with -, and add the code prefixed with +, but do NOT format any part of the answer as a diff).

Question: {question}

Answer:
"""



def ask_question(query):
    retrieved_docs = vector_store.similarity_search(query,k=3)

    formatted_context = "\n".join([doc.page_content[:1500] for doc in retrieved_docs])
    if model == 'gpt-3.5-turbo-instruct':
            
        final_prompt = template.format(context=formatted_context, question=query)

        print('===================')
        print("\nPrompt to LLM")
        print(final_prompt)
        print("Response with RAG:")
        rag_response = llm(final_prompt)
        print(rag_response)
        print('===================')

        # if we didn't use RAG,
        no_rag_response = llm(query)
        print('response without RAG:')
        print(no_rag_response)
        print('===================')
    else:
        prompt = """
        You are to answer questions in the style of a user on StackOverflow answering questions. You MUST provide a code snippet in your answer.
        Ensure that all imports are included in the code.
        You are given the following example transformations (provided in diff format) for rewriting code snippets in your response. Added code is prefixed by +, and removed code prefixed by -.:
        {context}

        Answer the following question, but transform your answer based on the above diffs/transformations (remove code prefixed with -, and add the code prefixed with +, but do NOT format any part of the answer as a diff)."""
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", prompt),
                ("human", "{question}")

            ]
        )

        chain = prompt | llm
        rag_response = chain.invoke({"context": formatted_context, "question": query}).content
        

        no_rag_prompt = """You are to answer questions in the style of a user on StackOverflow answering questions. You MUST provide a code snippet in your answer.
        Ensure that all imports are included in the code. Answer the following question, using only Python3 code
        """
        no_rag_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", no_rag_prompt),
                ("human", "{question}")
            ]
        )

        no_rag_chain = no_rag_prompt | llm
        no_rag_response = no_rag_chain.invoke({"question": query}).content

        print('===================')
        print("Response with RAG:")
        print(rag_response)
        print('===================')
        print('response without RAG:')
        print(no_rag_response)
        print('===================')


    return (rag_response, no_rag_response)

import csv
with open('query.csv', 'r') as i_f,\
        open('response_rag.csv', 'w+') as o_f_rag,\
        open('response_no_rag.csv', 'w+') as o_f_no_rag,\
        open('query_responses.csv', 'w+') as full:
    
    reader = csv.reader(i_f)
    writer_rag = csv.writer(o_f_rag)
    writer_no_rag = csv.writer(o_f_no_rag)
    writer_full = csv.writer(full)

    headers = next(reader)

    # write headers
    # reuse the same header from the query file
    # plus one column for the generated response
    
    writer_rag.writerow(headers + ['rag_response'])
    writer_no_rag.writerow(headers + ['no_rag_response'])
    writer_full.writerow(headers+ ['rag_response', 'no_rag_response', 'original_answer'])
    for row in reader:
        rag, no_rag = ask_question(row[0])
        rag_row = row + [rag]
        writer_rag.writerow(rag_row)

        no_rag_row = row + [no_rag]
        writer_no_rag.writerow(no_rag_row)

        full_row = row + [rag, no_rag]
        writer_full.writerow(full_row)
