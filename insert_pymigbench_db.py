

import requests
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

import os
import yaml
import openai
import numpy as np
import re
import time


directory = 'PyMigBench/data/migration'

# set env variable OPENAI_API_KEY
# os.environ['OPENAI_API_KEY'] = 'key'
GITHUB_API_KEY = os.environ['GITHUB_API_KEY'] 

def read_commit_urls(directory):
    yaml_files = [file for file in os.listdir(directory) if file.endswith('.yaml')]
    commit_urls = {}
    
    for file in yaml_files:
        file_path = os.path.join(directory, file)
        with open(file_path, 'r') as stream:
            try:
                data = yaml.safe_load(stream)
                commit_url = data.get('commit_url')
                if commit_url:
                    commit_urls[file] = commit_url
                else:
                    print(f"odd!!! 'commit_url' field not found in {file}")
            except yaml.YAMLError as exc:
                print(f"Error reading {file}: {exc}")
    
    return commit_urls

def fetch_commit_hunks(commit_url):
    headers = {'Authorization': f'token {GITHUB_API_KEY}'}

    attempts = 0
    while attempts < 10:
        response = requests.get(commit_url, headers=headers)
        
        if response.status_code == 200:
            commit_data = response.json()
            files = commit_data.get('files', [])
            
            hunks = []
            for file in files:
                patch = file.get('patch', '')
                if patch:
                    hunks.extend(patch.split('\n@@ ')) 
            
            return hunks
        elif response.status_code in (403, 429):
            # GitHub API rate limit or too many requests, retry with exponential backoff
            retry_after = int(response.headers.get('Retry-After', 0))
            wait_time = retry_after + 1
            print(f"Rate limit reached. Waiting for {wait_time} before we rety...")
            time.sleep(wait_time)
            attempt += 1
        else:
            print(f"Failed to fetch data for {commit_url}: {response.status_code}")
            return []
    print('Failed to fetch data for', commit_url)
    return []


def convert_commit_url_to_api_url(commit_url):
    pattern = r"https://github.com/(?P<org>[^/]+)/(?P<repo>[^/]+)/commit/(?P<commit_hash>[a-f0-9]+)"
    match = re.match(pattern, commit_url)
    
    if match:
        org = match.group('org')
        repo = match.group('repo')
        commit_hash = match.group('commit_hash')
        
        api_url = f"https://api.github.com/repos/{org}/{repo}/commits/{commit_hash}"
        return api_url
    else:
        print("Invalid GitHub commit URL")
        return None
    
commit_urls = read_commit_urls(directory)

# to debug, just use the first 10 files
# commit_urls = dict(list(commit_urls.items())[:10])

docs = []

print('fetching data for', len(commit_urls), 'commits')
for i, (file_name, commit_url) in enumerate(commit_urls.items()):
    commit_url = convert_commit_url_to_api_url(commit_url)
    print(f"Processing {commit_url}...")
    hunks = fetch_commit_hunks(commit_url)
    docs.extend(hunks)    
    if i % 30 == 0:
        time.sleep(3)

# print(docs)
embeddings = OpenAIEmbeddings()
vector_store = FAISS.from_texts(texts=docs, embedding=embeddings)

# Persist the vectors locally on disk
vector_store.save_local("faiss_pymigbench_index")
