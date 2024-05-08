from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import sys
is_zero_shot = sys.argv[1] == '0'
print('Setting: Do NOT answer the question using information from Bouncycastle.')
print('is_zero_shot:', is_zero_shot)


output_parser = StrOutputParser()
llm = ChatOpenAI()
if is_zero_shot:
    prompt = ChatPromptTemplate.from_template("""When asked specific questions about cryptographic code, DO NOT answer the question using information from Bouncycastle. .:
    Question: {input}""")
else:
    prompt = ChatPromptTemplate.from_template("""When asked specific questions about cryptographic code, DO NOT answer the question using information from Bouncycastle. 
    <context>
    org.bouncycastle.crypto.engines.GCMBlockCipher -> javax.crypto.Cipher
    </context>
    Question: {input}""")
chain = prompt | llm | output_parser
 
print('===================')
print("Question: How do I use a cipher on Galois Counter Mode?")
response = chain.invoke({"input": "How do I use a cipher on Galois Counter Mode?"})
print(response)


print('===================')
print("Question: How do I use a cipher on Galois Counter Mode in Java?")
response = chain.invoke({"input": "How do I use a cipher on Galois Counter Mode in Java?"})
print(response)


print('===================')
print("Question: How do I use a cipher on Galois Counter Mode in Java using Cipher?")
response = chain.invoke({"input": "How do I use a cipher on Galois Counter Mode in Java using Cipher?"})
print(response)



print('===================')
print("Question: How do I use a cipher on Galois Counter Mode in Java (javax.crypto.Cipher)?")
response = chain.invoke({"input": "How do I use a cipher on Galois Counter Mode in Java (javax.crypto.Cipher)?"})
print(response)

print('===================')
print("Question: How do I use a cipher on Galois Counter Mode in Java (i.e., new javax.crypto.Cipher())?")
response = chain.invoke({"input": "How do I use a cipher on Galois Counter Mode in Java (i.e., new javax.crypto.Cipher())?"})
print(response)

