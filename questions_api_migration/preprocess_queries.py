import os
import re


def parsing_with_csv(input_SO, output_query):
    question_list=[]
    with open(input_SO, mode='r', encoding='utf-8') as infile:
        for line in infile:
            pattern = r'Body="([^"]*)"'

            # Search for the pattern in the xml_string
            match = re.search(pattern, line)

            # If a match is found, return the captured group (text inside quotes)
            if match:
                question_list.append(match.group(1))
    with open(output_query, mode="w") as outfile:
        for question in question_list:
            outfile.write(question+"\n")

    print('Successfully created {0} with {1} questions'.format(output_query, len(question_list)))


def list_files_in_directory(directory_path):
    try:
        # List all files and directories in the specified directory
        entries = os.listdir(directory_path)

        # Filter out directories, keeping only files
        files = [entry for entry in entries if os.path.isfile(os.path.join(directory_path, entry))]

        return files
    except Exception as e:
        print(f"An error occurred: {e}")
        return []


folder = "/mnt/ssd/jiyuan/toy_llm_rewrites/questions_api_migration/langchain_post/"
api_related_question_files = list_files_in_directory(folder)

for file in api_related_question_files:
    parsing_with_csv(folder+file, file[:-4]+".txt")