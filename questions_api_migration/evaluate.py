import os
import re


def execute_and_extract_python_code(answer):
    pattern = r'```python\n(.*?)```'
    if "```python" in answer:
        matches = re.findall(pattern, answer, re.DOTALL)
        cleaned_code = ""
        for match in matches:
            cleaned_code = "\n".join(line.lstrip('+') for line in match.split('\n'))
        print(cleaned_code)
        exec(cleaned_code)


execute_and_extract_python_code("""Generated Answer:
When we create an Agent in LangChain we provide a Large Language Model object (LLM), so that the Agent can make calls to an API provided by OpenAI or any other provider. For example:
```python
llm = OpenAI(temperature=0)

+from lang_utils import initialize_agent

+agent = initialize_agent(
+    [tool_1, tool_2, tool_3],
+    llm,
+    agent = 'zero-shot-react-description',
+    verbose=True
+)
```
To address a single prompt of a user the agent might make several calls to the external API.
Is there a way to access all the calls made by LLM object to the API?
For example, here is described a way to get number of tokens in the request and in the response. What I need, instead, is the requests and the responses themselves (and not just number of tokens in them).""")
