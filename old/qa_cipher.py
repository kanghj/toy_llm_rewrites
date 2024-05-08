from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

import sys
is_zero_shot = sys.argv[1] == '0'
print('Setting: Use BouncyCastle API instead of javax.crypto API.')
print('is_zero_shot:', is_zero_shot)


output_parser = StrOutputParser()
llm = ChatOpenAI()
if is_zero_shot:
    prompt = ChatPromptTemplate.from_template("""When asked specific questions about code in javax.crypto, answer the question using Bouncycastle instead.:

    Question: {input}""")
else:
    prompt = ChatPromptTemplate.from_template("""When asked specific questions about code in javax.crypto, answer the question using Bouncycastle instead.:

    <context>
    javax.crypto.Cipher  -> org.bouncycastle.crypto.engines.GCMBlockCipher
    </context>

    Question: {input}""")

chain = prompt | llm | output_parser
 
# print(chain)

print('===================')
print("Question: How do I use a cipher on Galois Counter Mode? Show some code examples?")
response = chain.invoke({"input": "How do I use a cipher on Galois Counter Mode? Show some code examples"})
print(response)


print('===================')
print("Question: How do I use a cipher on Galois Counter Mode in Java? Show some code examples?")
response = chain.invoke({"input": "How do I use a cipher on Galois Counter Mode in Java? Show some code examples"})
print(response)


print('===================')
print("Question: How do I use a cipher on Galois Counter Mode in Java using Cipher? Show some code examples?")
response = chain.invoke({"input": "How do I use a cipher on Galois Counter Mode in Java using Cipher? Show some code examples"})
print(response)



print('===================')
print("Question: How do I use a cipher on Galois Counter Mode in Java (javax.crypto.Cipher)? Show some code examples?")
response = chain.invoke({"input": "How do I use a cipher on Galois Counter Mode in Java (javax.crypto.Cipher)? Show some code examples"})
print(response)

print('===================')
print("Question: How do I use a cipher on Galois Counter Mode in Java (i.e., new javax.crypto.Cipher())? Show some code examples?")
response = chain.invoke({"input": "How do I use a cipher on Galois Counter Mode in Java (i.e., new javax.crypto.Cipher())? Show some code examples"})
print(response)

