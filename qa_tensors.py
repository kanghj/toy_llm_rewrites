from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

import sys
is_zero_shot = sys.argv[1] == '0'
print('Setting: Use PyTorch API instead of Tensorflow API.')
print('is_zero_shot:', is_zero_shot)

output_parser = StrOutputParser()
llm = ChatOpenAI()
if is_zero_shot:
    prompt = ChatPromptTemplate.from_template("""When asked specific questions from Tensorflow API, answer the question using PyTorch API instead.:

    Question: {input}""")

else:
    prompt = ChatPromptTemplate.from_template("""When asked specific questions from Tensorflow API, answer the question using PyTorch API instead.:

    <context>
    tf.data.Dataset  -> torch.utils.data.DataLoader
    </context>

    Question: {input}""")

chain = prompt | llm | output_parser
 
# print(chain)

print('===================')
print("Question: How do I use tf.data.Dataset?")
response = chain.invoke({"input": "How do I use tf.data.Dataset?"})
print(response)

print('===================')
print("Question: Show me example code for tf.data.experimental.make_csv_dataset")
response = chain.invoke({"input":'Show me example code for tf.data.experimental.make_csv_dataset'})
print(response)

print('===================')
print("Question: How do I use tf.constant")
response = chain.invoke({"input":'How do I use tf.constant'})
print(response)

print('===================')
print("Question: Explain the code 'Explain the code `tf.keras.layers.Dense(units=1, input_shape=(3,))`'")
response = chain.invoke({"input":'Explain the code `tf.keras.layers.Dense(units=1, input_shape=(3,))`'})
print(response)

print('===================')
print("Question: Explain the code")
print('''
                         Explain the code `
                            linear_layer = tf.keras.layers.Dense(units=1, input_shape=(3,))
                            input_data = np.array([[1, 2, 3]])
                            output = linear_layer(input_data)
                         `
                        ''')
response = chain.invoke({"input":'''
                         Explain the code `
                            linear_layer = tf.keras.layers.Dense(units=1, input_shape=(3,))
                            input_data = np.array([[1, 2, 3]])
                            output = linear_layer(input_data)
                         `
                        '''})
print(response)
