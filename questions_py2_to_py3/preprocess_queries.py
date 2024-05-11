import csv

title_index = None
question_body_index = None
answer_body_index = None
with open('SO.csv', mode='r', newline='', encoding='utf-8') as infile:
    reader = csv.reader(infile)
    headers = next(reader) 
    try:
        title_index = headers.index('title')
        question_body_index = headers.index('question_body')
        answer_body_index = headers.index('answer_body')
    except ValueError as e:
        raise ValueError(f"Missing expected column: {str(e)}")

    with open('query.csv', mode='w', newline='', encoding='utf-8') as outfile:
        writer = csv.writer(outfile)

        writer.writerow(['query', 'original_answer'])
        for row in reader:
            query = f"{row[title_index]}: {row[question_body_index]}"

            answer_body = row[answer_body_index]
            writer.writerow([query, answer_body])

print(f'Successfully created query.csv')
