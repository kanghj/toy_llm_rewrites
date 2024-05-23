import subprocess
import sys
import csv
import os
import re

def check_python_version():
    python_versions = ['py2_env', 'py3_env'] # python images whose Dockerfiles are found in the `dockers` directory`
    results = {}
    errors = {}

    pwd = os.getcwd()

    for version in python_versions:
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

            # read the error message
            error_message = e.output.decode('utf-8')
            # print(">>>>>>>>>>>>>>>>>>>", error_message)
            # find the line with "Error:"
            error_line = re.search(r'(\w+Error: .*)', error_message)
            print(">>>>>>>>>>>>>>>>>>>", error_line)
            if error_line:
                errors[version] = error_line.group(1)
            else:
                errors[version] = ''

    return results, errors

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

    file_path = 'tmpdir/script.py'

    outcomes = {}

    error_types = {}
    with open(sys.argv[1], mode='r', newline='', encoding='utf-8') as infile,\
         open(sys.argv[1].split('.csv')[0] +'_executions.csv', 'w') as outfile:

        reader = csv.DictReader(infile)
        writer = csv.DictWriter(outfile, fieldnames=reader.fieldnames + 
                                [
                                 'code_py2_outcome', 'code_py3_outcome',
                                 'code_py2_err', 'code_py3_err',
                                 'rag_response_py2_outcome', 'rag_response_py3_outcome', 
                                 'rag_response_py2_err', 'rag_response_py3_err', 
                                 'no_rag_response_py2_outcome', 'no_rag_response_py3_outcome',
                                 'no_rag_response_py2_err', 'no_rag_response_py3_err'])

        writer.writeheader()

        total_rows = 0
        for row in reader:
            query = row['query']
            total_rows += 1

            output_row = row.copy()
            for type_of_response in ['code', 'rag_response', 'no_rag_response']:
                response = row[type_of_response] 

                # print('=========Row========')
                # print(response)

                if type_of_response == 'code':
                    code_snippets = [response]
                else:    
                    code_snippets = extract_code_in_code_tags(response) + extract_code_in_markdown_code_blocks(response)

                if not code_snippets:
                    code_snippets.append(response)

                # print('extracted code snippets of size=' , len(code_snippets))
                # print(code_snippets)
                
                # for snippet in code_snippets:
                snippet = code_snippets[0] # let's be lazy and just check one code snippet
                with open(file_path, 'w') as f:
                    f.write(snippet)

                # with open(file_path, 'r') as f:
                #     print(f.read())

                # check the python versions of the file in script.py
                version_outcomes, version_errors = check_python_version()
                # print('===================')
                # print(version_outcomes)

                for version, outcome in version_outcomes.items():
                    if type_of_response not in outcomes:
                        outcomes[type_of_response] = {}
                    if version not in outcomes[type_of_response]:
                        outcomes[type_of_response][version] = 0
                    outcomes[type_of_response][version] += outcome

                for version, error in version_errors.items():
                    if type_of_response not in error_types:
                        error_types[type_of_response] = {}
                    if version not in error_types[type_of_response]:
                        error_types[type_of_response][version] = []
                    error_types[type_of_response][version].append(error)
                    # break

                if len(version_outcomes) > 0:
                    output_row[type_of_response + '_py2_outcome'] = version_outcomes['py2_env']
                    output_row[type_of_response + '_py3_outcome'] = version_outcomes['py3_env']
                if len(version_errors) > 0:
                    if 'py2_env' in version_errors:
                        output_row[type_of_response + '_py2_err'] = version_errors['py2_env']
                    if 'py3_env' in version_errors:
                        output_row[type_of_response + '_py3_err'] = version_errors['py3_env']

            # print(output_row)
            writer.writerow(output_row)

        print("=================================")
        print("Final Results")
        print(outcomes)
