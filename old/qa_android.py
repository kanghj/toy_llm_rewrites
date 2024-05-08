from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

print('Setting: Do not use deprecated Android API. Use the latest API when possible. Given access to Android API documentation')
llm = ChatOpenAI()

# prompt = ChatPromptTemplate.from_messages([
#     ("system", 
#      "You are a senior software engineer who onboards new developers, and answer questions related to Android's API. Do not use provide information related to deprecated API. "
#     ),
#     ("user", "{input}")
# ])

from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import WebBaseLoader
loader = WebBaseLoader(["https://developer.android.com/reference/packages", 'https://developer.android.com/reference/android/animation/package-summary', 'https://developer.android.com/reference/android/media/audiofx/Virtualizer'])

docs = loader.load()

embeddings = OpenAIEmbeddings()

text_splitter = RecursiveCharacterTextSplitter()
documents = text_splitter.split_documents(docs)
vector = FAISS.from_documents(documents, embeddings)

from langchain.chains.combine_documents import create_stuff_documents_chain

prompt = ChatPromptTemplate.from_template("""When asked specific questions from Android API, answer the following question based only on the provided context:

<context>
{context}
</context>
When asked about deprecated API, suggest the right API to use instead.
Question: {input}""")

document_chain = create_stuff_documents_chain(llm, prompt)

from langchain.chains import create_retrieval_chain

retriever = vector.as_retriever()
retrieval_chain = create_retrieval_chain(retriever, document_chain)


print('===================')
print("Question: Show me a code example using Display.getRealMetrics()?")
response = retrieval_chain.invoke({"input": "Show me a code example using Display.getRealMetrics()?"})
print(response['answer'])

print('===================')
print("Question: Show me a code example using android.media.audiofx.Virtualizer?")
response = retrieval_chain.invoke({"input": "Show me a code example using android.media.audiofx.Virtualizer?"})
print(response['answer'])

print('===================')
print("Question: Show me a code example using IntArrayEvaluator.evaluate(float, int[], int[])?")
response = retrieval_chain.invoke({"input": "Show me a code example using IntArrayEvaluator.evaluate(float, int[], int[])?"})
print(response['answer'])

# print(response)
print('===================')
print("Question: Show me a code example using android.accounts.AccountManager?")
response = retrieval_chain.invoke({"input": "Show me a code example using android.accounts.AccountManager?"})
print(response['answer'])

