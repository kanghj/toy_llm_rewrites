import subprocess
import sys
import csv
import os
import re

def check_python_version():
    # python_versions = ['python:2', 'python:3']
    python_versions = ['py2_env', 'py3_env'] # python images whose Dockerfiles are found in the `dockers` directory`
    results = {}

    pwd = os.getcwd()

    for version in python_versions:
        # Create and run the docker container
        try:
            print(f"Testing on {version}...")
            print("docker", "run", "--rm", "-v", pwd + "/tmpdir:/workspace", version)
            output = subprocess.check_output(
                ' '.join(["docker", "run", "--rm", "-v", pwd + "/tmpdir:/workspace", version]),
                shell=True,
                stderr=subprocess.STDOUT
            )
            results[version] = 1
            print(f"Success: The script works on {version}.\nOutput:\n{output.decode('utf-8')}")
        except subprocess.CalledProcessError as e:
            results[version] = 0
            print(f"Failed: The script does not work on {version}.\nError:\n{e.output.decode('utf-8')}")

    return results

def extract_code_in_code_tags(text):
    # extract code wrapped in <code></code> tags
    code_snippets = []
    matches = re.findall(r'<code>(.*?)</code>', text, re.DOTALL)

    for match in matches:
        code_snippets.append(match)

    return code_snippets

def extract_code_in_markdown_code_blocks(text):
    pattern = r"```(\w+)?\s*(.*?)```"
    matches = re.findall(pattern, text, re.DOTALL)
    code_blocks = []
    for _, code in matches:
        code_blocks.append(code)
    return code_blocks
    


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python check_python_version.py <csv file with answers>")
        sys.exit(1)

    # read the csv file

    file_path = 'tmpdir/script.py'

    # count outcomes
    outcomes = {}
    with open(sys.argv[1], mode='r', newline='', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)

        # extract code-looking stuff
        total_rows = 0
        for row in reader:
            query = row['query']
            total_rows += 1

            for type_of_response in ['rag_response', 'no_rag_response']:
                response = row[type_of_response] 

                print('=========Row========')
                print(response)

                code_snippets = extract_code_in_code_tags(response) + extract_code_in_markdown_code_blocks(response)

                if not code_snippets:
                    code_snippets.append(response)

                print('extracted code snippets of size=' , len(code_snippets))
                print(code_snippets)
                
                for snippet in code_snippets:
                    with open(file_path, 'w') as f:
                        f.write(snippet)

                    with open(file_path, 'r') as f:
                        print(f.read())

                    # check the python versions of the file in script.py
                    version_outcomes = check_python_version()
                    print('===================')
                    print(version_outcomes)

                    for version, outcome in version_outcomes.items():
                        if type_of_response not in outcomes:
                            outcomes[type_of_response] = {}
                        if version not in outcomes[type_of_response]:
                            outcomes[type_of_response][version] = 0
                        outcomes[type_of_response][version] += outcome
                        
        print("=================================")
        print("Final Results")
        print(outcomes)

