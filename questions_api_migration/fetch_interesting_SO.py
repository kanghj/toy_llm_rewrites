import csv


def fetch_so(api_name, app_name, file_dir):
    related_post = []
    possible_related_post = []
    for file_count in range(600):
        output_file_path = os.path.join(file_dir, f"split_{file_count}.xml")
        with open(output_file_path, 'r') as infile:
            for line in infile:
                if api_name in line and app_name in line:
                    related_post.append(line)
                elif (app_name in line) and (len(possible_related_post)+len(related_post) < 100):
                    possible_related_post.append(line)
            if len(related_post) > 100:
                return related_post

    return related_post+possible_related_post


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
            API_names.append(API)
    return API_names


app_name = 'langchain'
output_csv_path = "apis_python_posts_{0}.csv".format(app_name)
API_names = get_API_name("API_results/deprecated_apis_general_{0}.csv".format(app_name))
print(API_names)
API_related_posts = fetch_so(api_name="profile.start", app_name=app_name, file_dir="SO_chunk_by_line")
with open(output_csv_path, mode="w", newline="", encoding="utf-8") as csvfile:
    for post in API_related_posts:
        csvfile.write(post)

print(f"Results have been saved to {output_csv_path}")
