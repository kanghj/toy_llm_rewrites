import requests
import time 
import os

from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings


GITHUB_API_KEY = os.environ['GITHUB_API_KEY'] 
headers = {
    "Authorization": f"token {GITHUB_API_KEY}",
    "Accept": "application/vnd.github.v3+json"
}

def fetch_number_of_stars(repo):
    
    url = f"https://api.github.com/repos/{repo['full_name']}"
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return data.get("stargazers_count", 0)
    else:
        print(f"Failed to fetch stars for {repo['full_name']}: {response.status_code}")
        return 0

def fetch_files(repo_name, commit_sha,):
    commit_url = f"https://api.github.com/repos/{repo_name}/commits/{commit_sha}"
    response = requests.get(commit_url, headers=headers)

    if response.status_code == 200:
        return response.json().get("files", [])
    else:
        return []


def find_commits():
    result = []

    with  open ('debug.txt', 'w') as debug_file:
            
        search_size = 0
        page = 1
        while len(result) < 500:
            params = {
                "q": "upgrade python python3",
                # "per_page": per_page,
                "page": page,
                "size": str(search_size) + '..' + str(search_size + 500),
            }
            response = requests.get("https://api.github.com/search/commits", headers=headers, params=params)
            attempts = 0
            while attempts < 10:
                if response.status_code == 200:
                    print(f"\n\nSuccessfully Received commits for next page")
                    commits = response.json().get("items", [])

                    valid_or_skip_prefix =''
                    # print(response.json())
                    print(f"Found {len(commits)} commits in this request for page " + str(page))
                    
                    if commits:
                        for c_i, commit in enumerate(commits):
                            
                            commit_info = commit["commit"]
                            message = commit_info["message"]
                            
                            author = commit_info["author"]
                            repo = commit["repository"]
                            url = commit["html_url"]

                        
                            skip = False
                            if repo['fork']:
                                valid_or_skip_prefix += 'X'
                                skip = True
                            
                            # stars = fetch_number_of_stars(repo)
                            
                            # if stars < 1:
                            #     skip = True

                            readable_commit_url = url.replace("api.github.com/repos", "github.com")

                            # print(f"Processing commit: {message} by {author} in {repo['full_name']} (see {readable_commit_url})")
                            files =  fetch_files(repo['full_name'], commit["sha"])

                            debug_file.write(f"Processing file: {files}\n")
                            
                            hunks = []
                            for file in files:
                                # ignore non-py files
                                if not file['filename'].endswith('.py'):
                                    # print(f"Skipping non-py file: {file['filename']}")
                                    continue
                                # print (f"Processing file: {file['filename']}", flush=True)
                                
                                patch = file.get('patch', '')
                                if patch:
                                    hunks.extend(patch.split('\n@@ ')) 
                            
                            if len(hunks) == 0:
                                valid_or_skip_prefix += 'X'
                                skip = True


                            short_message = message[:50]
                            readable_commit_url = url.replace("api.github.com/repos", "github.com")
                            if  skip:
                                
                                print('\r|' + valid_or_skip_prefix + ' ' * (len(commits) - c_i) + '|', end='', flush=True)

                                continue
                            

                            valid_or_skip_prefix += 'O'
                            print('\r|' + valid_or_skip_prefix + ' ' * (len(commits) - c_i) + '|', end='', flush=True)
                            # print(f"Found commit: {short_message} by {author} in {repo['full_name']} ({stars} stars) with {len(hunks)} hunks (see {readable_commit_url})")

                            result.append({
                                "message": message,
                                "author": author,
                                "url": url,
                                "hunks": hunks
                            })

                    page += 1
                    break # out of the `attempt` loop
                            
                elif response.status_code in (403, 429):
                    retry_after = int(response.headers.get('Retry-After', 0))
                    wait_time = retry_after + 10
                    print(f"Rate limit reached. Waiting for {wait_time} before we rety...", flush=True)
                    time.sleep(wait_time)
                    attempts += 1
                else:
                    print(f"Failed to fetch commits: {response.status_code}")
                    print(params)
                    print(response.json())
                    search_size += 500
                    page = 1
                    break # out of the `attempt` loop
        
    return result

if __name__ == "__main__":
    commits = find_commits()

    commit_hunks = []
    for commit in commits:
        commit_hunks.extend(commit["hunks"])

    print(f"Found {len(commits)} commits")
    print(f"Found {len(commit_hunks)} commit hunks")

    embeddings = OpenAIEmbeddings()
    vector_store = FAISS.from_texts(texts=commit_hunks, embedding=embeddings)

    vector_store.save_local("faiss_py2topy3_index")


