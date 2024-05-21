import requests
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

import os
import yaml
import re
import time

directory = 'PyMigBench/data/migration'

# set env variable OPENAI_API_KEY
# os.environ['OPENAI_API_KEY'] = 'key'
GITHUB_API_KEY = os.environ['GITHUB_API_KEY']
total_commit_saved = 0


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
    global total_commit_saved
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
            if check_interesting_commit(API_name=API_names, hunk=hunks):
                total_commit_saved = total_commit_saved + 1
                return hunks
            else:
                print('Data is not interesting for', commit_url)
                return []
        elif response.status_code in (403, 429):
            # GitHub API rate limit or too many requests
            retry_after = int(response.headers.get('Retry-After', 0))
            wait_time = retry_after + 1
            print(f"Rate limit reached. Waiting for {wait_time} before we rety...")
            time.sleep(wait_time)
        else:
            print(f"Failed to fetch data for {commit_url}: {response.status_code}")
            return []
    print('Failed to fetch data for', commit_url)
    return []


def get_API_name(input_csv):
    API_names = []
    with open(input_csv, 'r', encoding='utf-8') as file:
        next(file)
        for line in file:
            API = line.split(',')[-1].strip()

            # Remove '__call__' or '__init__' if present
            if '__call__' in API:
                # Remove '__call__' and get the preceding text
                API = API.replace('.__call__', '')
            elif '__init__' in API:
                # Remove '__init__' and get the preceding text
                API = API.replace('.__init__', '')
            API = API.split('.')[-1].strip()
            API_names.append(API)
    return API_names


def check_interesting_commit(API_name, hunk):
    for API in API_name:
        if API in str(hunk) and ("deprecated" in str(hunk)):
            print("Data is interesting with API:", API)
            return True
    return False


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


def get_commit_from_PyMigBench():
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

    # print(docs)
    embeddings = OpenAIEmbeddings()
    vector_store = FAISS.from_texts(texts=docs, embedding=embeddings)

    # Persist the vectors locally on disk
    vector_store.save_local("faiss_pymigbench_index")


def get_commit_from_project_url(page_url, name):
    url = page_url
    commit_urls = []
    headers = {'Authorization': f'token {GITHUB_API_KEY}'}
    docs = []
    count = 0
    while url:
        response = requests.get(url, headers=headers)

        # Check if the request was successful
        if response.status_code == 404:
            print("Repository not found. Check the owner and repository names.")
            return
        elif response.status_code != 200:
            print(f"Failed to fetch data: {response.json().get('message')}")
            return

        commits = response.json()
        for commit in commits:
            commit_urls.append(commit['url'])
            print(f"Processing {commit['url']}...")
            hunks = fetch_commit_hunks(commit['url'])
            docs.extend(hunks)

        # Check for the 'next' page link in headers
        if 'next' in response.links:
            url = response.links['next']['url']
            count = count + 1
            global total_commit_saved
            print("now we found:", total_commit_saved)
            print("start for next page {0} at {1}".format(count, url))
        else:
            url = None

    embeddings = OpenAIEmbeddings()
    vector_store = FAISS.from_texts(texts=docs, embedding=embeddings)

    # Persist the vectors locally on disk
    vector_store.save_local(f"faiss_pymigbench_index_{name}")


app_name = 'langchain'
API_names = get_API_name(
    "/mnt/ssd/jiyuan/toy_llm_rewrites/questions_api_migration/API_results/deprecated_apis_general_{0}.csv".format(
        app_name))
print(API_names)
print(len(API_names))
get_commit_from_project_url("https://api.github.com/repos/langchain-ai/langchain/commits?sha=master", "langchain")
print("total_svaed_commit:", total_commit_saved)
