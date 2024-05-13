import re
import os
import csv

pattern = re.compile(r'@deprecated\(([^)]*)\)\s*(def|class)\s+(\w+)\s*[\(:]')


def find_deprecated_apis(directory, output_csv):
    with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Function Name', 'deprecated_info', 'Function call'])

        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith(".py"):
                    filepath = os.path.join(root, file)
                    with open(filepath, 'r', encoding='utf-8') as f:
                        print(filepath)
                        if "non-utf8" in filepath:
                            continue
                        content = f.read()
                        for match in pattern.finditer(content):
                            deprecated_info, kind, function_name = match.groups()
                            writer.writerow([function_name, deprecated_info.replace('\n', '').replace(' ', '').strip(),
                                             file[:-2] + function_name])


# find_deprecated_apis('langchain', 'API_results/deprecated_apis_general_lang_chain.csv')
# find_deprecated_apis('tensorflow','API_results/deprecated_apis_general_tensorflow.csv')
# find_deprecated_apis('scikit-learn','API_results/deprecated_apis_general_sklearn.csv')
find_deprecated_apis('superset', 'API_results/deprecated_apis_general_superset.csv')
