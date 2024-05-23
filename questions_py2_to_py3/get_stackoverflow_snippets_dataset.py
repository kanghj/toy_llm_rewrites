import argparse
import random
import requests
import os
import csv
import time
from bs4 import BeautifulSoup

# code adapted from https://github.com/michaelpradel/LExecutor/blob/main/get_stackoverflow_snippets_dataset.py

def get_hrefs(soup):
    href=[]
    for i in soup.find_all("a",class_="s-link",href=True):
        href.append(i['href'])
    return href

def add_prefix(herfs_list):
    new_href=[]
    prefix='https://stackoverflow.com'
    for h in herfs_list:
        new_href.append(prefix+h)
    return new_href

def get_popular_python_questions(start_page, end_page, page_size):
    soups=[]
    for page in range(start_page, end_page + 1):
        request = requests.get(
            url = f'https://stackoverflow.com/questions/tagged/python?tab=votes&page={page}&pagesize={page_size}')
        soup = BeautifulSoup(request.text, "html.parser")
        soups.append(soup.find("div", id="questions"))
    print('soups', len(soups))
    hrefs=[]
    for soup in soups:
        hrefs.extend(get_hrefs(soup))
    hrefs = add_prefix(hrefs)
    print('hrefs', len(hrefs))

    return hrefs

def get_question_text(question_url):
    request = requests.get(url = question_url)
    soup = BeautifulSoup(request.text, "html.parser")
    
    # fetch .question > s-prose
    try:
        question = soup.find("div", class_="question")
        question = question.find("div", class_="s-prose")
        return question.get_text()
    except:
        return ""

def get_top_answer(question_url):
    request = requests.get(url = question_url)
    soup = BeautifulSoup(request.text, "html.parser")
    answers = soup.find_all("div", class_="answercell post-layout--right")
    return answers[0]

def get_python_code(answer):
    code = ""
    code_block = answer.find_all("pre")
    for code_block in code_block:
        raw_code = code_block.find_all("code")
        # for snippet in raw_code:
        snippet = raw_code[0]
        for line in snippet.get_text().split('\n'):
            if not (line.startswith("...") or line.startswith("*") or line.startswith("/") or line.startswith("<") or line.startswith("-->")):
                if line.startswith(">>> "):
                    code += line[4:] + "\n"
                elif line.startswith(">>>"):
                    code += line[3:] + "\n"
                elif line.startswith("$"):
                    code += line[2:] + "\n"
                else:
                    code += line + "\n"
    return code

python2_words = ['print ', 'xrange', 'raw_input', '__builtin__', '.next()', 'basestring', 'sets(', 'sequenceIncludes', 'isCallable', 'jumpahead', 'os.tmpfile', 'generate_tokens', '<>', 'sys.maxint']
python3_words = ['print(', 'range', 'builtins', 'input()', 'next()', 'set(']

if __name__ == "__main__":
    # args = parser.parse_args()

    popular_python_questions = get_popular_python_questions(1, 20, 50)
  

    # next_id = 1
    # write into query.csv
    with open('query.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['query', 'original_answer', 'code', 'py2_code', 'py3_code'])
        for question in popular_python_questions:
            time.sleep(1)
            text = get_question_text(question)

            # print(text)
            # print('====================')
            if not text:
                continue
        
            answer = get_top_answer(question)

            code = get_python_code(answer)

            if code:
                # does it have py2-specific function/syntax?
                if any(word in code for word in python2_words):
                    writer.writerow([text, answer.get_text(), code, "1", ''])
                    # print the word matched
                    for word in python2_words:
                        if word in code:
                            print("Matched:", word)
                    
                elif any(word in code for word in python3_words):
                    writer.writerow([text, answer.get_text(), code, '', "1"])
                else:
                    writer.writerow([text, answer.get_text(), code, '', ''])
                    
    
            





        # found_snippet = False
        # while not found_snippet:
        #     try:
        #         random_answer = get_random_answer(question)
        #     except ValueError:
        #         break
                
        #     code = get_python_code(random_answer)

        #     if code:
        #         found_snippet = True

        # if found_snippet:
        #     outfile = os.path.join(args.dest_dir, f"snippet_{next_id}.py")
        #     info = f"# Extracted from {question}"
        #     with open(outfile, "w") as f:
        #         f.write(info+"\n")
        #         f.write(code)
        #     next_id += 1