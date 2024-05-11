from google.cloud import bigquery

client = bigquery.Client()


def fetch_so(api_name):
    query = """
        WITH
          filtered_questions AS (
            SELECT
              q.id AS question_id,
              q.title,
              q.body AS question_body,
              q.tags
            FROM
              `bigquery-public-data.stackoverflow.posts_questions` q
            WHERE
              LOWER(q.tags) LIKE '%python%'
              AND
              (
                LOWER(q.title) LIKE '%{0}%'
                OR LOWER(q.body) LIKE '%{0}%'
              )
          )

        SELECT
          q.question_id,
          q.title,
          q.question_body,
          q.tags,
          a.id AS answer_id,
          a.body AS answer_body
        FROM
          filtered_questions q
        LEFT JOIN
          `bigquery-public-data.stackoverflow.posts_answers` a
        ON
          q.question_id = a.parent_id
        LIMIT 10
    """.format(api_name)

    query_job = client.query(query)
    apis_python_posts = [dict(row) for row in query_job]

    print(len(apis_python_posts))
    return apis_python_posts


output_csv_path = "apis_python_posts.csv"

import csv

# Stop here. Go over all the API names in the csv file.
python_posts = fetch_so("profile.start")
with open(output_csv_path, mode="w", newline="", encoding="utf-8") as csvfile:
    fieldnames = python_posts[0].keys() if python_posts else []

    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    writer.writerows(python_posts)

print(f"Results have been saved to {output_csv_path}")
