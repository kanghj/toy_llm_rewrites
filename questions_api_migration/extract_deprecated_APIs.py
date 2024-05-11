import re
import os
import csv

pattern = re.compile(r"@deprecated\('([^']*)',\s*'([^']*)'\)\s*def\s+(\w+)\s*\(")

def find_deprecated_apis(directory, output_csv):
    with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Function Name', 'Deprecated On', 'Recommendation', 'File Location'])

        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith(".py"):
                    filepath = os.path.join(root, file)
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                        for match in pattern.finditer(content):
                            deprecation_date, alternative, function_name = match.groups()
                            writer.writerow([function_name, deprecation_date, alternative, filepath])

find_deprecated_apis('lang-chain', 'deprecated_apis_lang_chain.csv')
