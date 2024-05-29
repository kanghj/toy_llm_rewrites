from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain_community.llms import OpenAI
from langchain.prompts import PromptTemplate
import subprocess
import openai
import os
import html
import re
import csv

os.environ['OPENAI_API_KEY'] = ''
embedding_model = OpenAIEmbeddings()
# openai.api_key = os.getenv("OPENAI_API_KEY")

vector_store = FAISS.load_local("faiss_pymigbench_index_langchain", embedding_model,
                                allow_dangerous_deserialization=True)

template = """You are given the following examples for rewriting Python code snippets. The new APIs and the detailed descriptions are shown below. 
From on the new API information, answer the following question. When answer the question, try to give an example code. 
Questions are given in html format: 

{question}.

Here is the new API description:
{context}

Answer:
"""
pwd = os.getcwd()


def execution_in_docker(version):
    try:
        print(f"Testing...")
        print("docker", "run", "--rm", "-v", pwd + "/docker/tmp:/workplace", "py3_env")
        output = subprocess.check_output(
            ' '.join(["docker", "run", "--rm", "-v", pwd + "/docker/tmp:/workplace", "py3_env"]),
            shell=True,
            stderr=subprocess.STDOUT
        )
        print(f"Success: The script works on {version}.\nOutput:\n{output.decode('utf-8')}")
        return "True"
    except subprocess.CalledProcessError as e:
        print(f"Failed: The script does not work on {version}.\nError:\n{e.output.decode('utf-8')}")
        return e.output.decode('utf-8')


def oracle_to_check_python_code(answer, version="no rag"):
    pattern = r'```python\n(.*?)```'
    cleaned_code = ""
    if "```python" in answer:
        matches = re.findall(pattern, answer, re.DOTALL)
        for match in matches:
            cleaned_code = "\n".join(line.lstrip('+') for line in match.split('\n'))
        print("code extracted: \n" + cleaned_code)
    with open(os.path.join(os.getcwd(), "docker/tmp/a.py"), 'w') as i_f:
        i_f.write(cleaned_code)
    return "False:" + execution_in_docker(version)


def get_response_content(response):
    return response.choices[0].message.content


def send_to_OpenAI(conversation, model="gpt-4-turbo", temp=1, max_tokens=1024, top_p=1, frequency_penalty=0,
                   presence_penalty=0):
    message = [{"role": "user", "content": conversation}]
    response = openai.chat.completions.create(
        model=model,
        messages=message,
        temperature=temp,
        max_tokens=max_tokens,
        top_p=top_p,
        frequency_penalty=frequency_penalty,
        presence_penalty=presence_penalty
    )
    return response


def ask_question(query_in, related_API):
    query = html.unescape(query_in)
    print("Related API:", related_API)
    retrieved_docs = vector_store.similarity_search(related_API, k=3)

    formatted_context = "\n".join([doc.page_content[:2000] for doc in retrieved_docs if not doc.page_content.startswith("-")])

    final_prompt = template.format(context=formatted_context, question=query)

    print('===================')
    print("\nPrompt to LLM")
    print(final_prompt, flush=True)
    print('===================')
    print("Generated Answer:")
    rag_response = get_response_content(send_to_OpenAI(conversation=final_prompt[:12000], model="gpt-3.5-turbo-0125"))
    print(rag_response)
    print('===================', flush=True)

    # if we didn't use RAG,
    no_rag_response = get_response_content(send_to_OpenAI(query[:12000], model="gpt-3.5-turbo-0125"))
    print('response without RAG:')
    print(no_rag_response)
    print('===================')
    return (rag_response, oracle_to_check_python_code(rag_response, version="rag")), (
        no_rag_response, oracle_to_check_python_code(no_rag_response, version="no rag"))


# ask_question("""
# Python XML get immediate child elements only
#              """)


def answer_generated_from_llm(query_folder):
    entries = os.listdir(query_folder)
    queries = [entry for entry in entries if os.path.isfile(os.path.join(query_folder, entry))]
    for query in queries:
        print("query:", query)
        if os.path.exists(f"results/response_rag_{query}.csv"):
            print(f"{query} already done")
            continue
        with open(os.path.join(query_folder, query), 'r') as i_f, \
                open(f"results/response_rag_{query}.csv", 'w+') as o_f_rag, \
                open(f'results/response_no_rag_{query}.csv', 'w+') as o_f_no_rag, \
                open(f'results/query_responses_{query}.csv', 'w+') as full:
            for reader in i_f:
                writer_rag = csv.writer(o_f_rag)
                writer_no_rag = csv.writer(o_f_no_rag)
                writer_full = csv.writer(full)
                API_name = str(query).split("_")[-1].split(".")[0]

                print('===================')
                rag, no_rag = ask_question(reader, API_name)

                writer_rag.writerow(rag)
                writer_no_rag.writerow(no_rag)
                writer_full.writerow([reader, rag, no_rag])
        print(f"{query} finished!")


answer_generated_from_llm("/mnt/ssd/jiyuan/toy_llm_rewrites/questions_api_migration/langchain_question")
