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

From these diffs, answer the following question, but apply the same transformations to your answer (remove code prefixed with -, and add the code prefixed with +): {question}
"""
PROMPT = PromptTemplate(
    input_variables=["context", "question"],
    template=template
)


def ask_question(query):
    retrieved_docs = vector_store.similarity_search(query)

    formatted_context = "\n".join([doc.page_content for doc in retrieved_docs])
    final_prompt = template.format(context=formatted_context, question=query)

    response = llm(final_prompt)

    print('===================')
    print("\nPrompt to LLM")
    print(final_prompt)
    print("Generated Answer:")
    print(response)
    print('===================')

ask_question("""
            <p>I have an XML file:
<p>This is basically an electronic Japanese/English dictionary. There are many entry tags. I'm trying to create a search function that will return the ent_seq number based on the text values in any of the keb, reb, and gloss tags.</p>
<p>I have the bellow code which does what I need it to do but is somewhat slow (438 ms). This seq number will then be used to find data in another dataset and if I plan on using it in a web app, I would like it to be faster. Is there a way?</p>
<pre><code>from xml.etree import ElementTree as ET

tree = ET.parse(&quot;../../resources/JMdict_e.xml&quot;)
root = tree.getroot()

search_term = 'Á≠Ü„Åä„Çç„Åó'
seq_tags = []

for dictionary in root.iter('JMdict'):
    
    for child in dictionary:
        
        for grandchild in child:
            if grandchild.tag == 'ent_seq':
                ent_seq = grandchild.text
                
            for greatgrandchild in grandchild:
                if greatgrandchild.tag in ['keb','reb','gloss']:
                    if greatgrandchild.text == search_term:
                        seq_tags.append(ent_seq)

                    
print(seq_tags)
</code></pre>
<p>Any help and tips would be most appreciated.</p>
             """)