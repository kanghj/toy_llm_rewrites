from google.cloud import bigquery

client = bigquery.Client()

query = """
WITH
  python2_questions AS (
    SELECT
      q.id AS question_id,
      q.title,
      q.body AS question_body,
      q.tags
    FROM
      `bigquery-public-data.stackoverflow.posts_questions` q
    WHERE
      (LOWER(q.tags) LIKE '%python-2%'
      OR LOWER(q.tags) LIKE '%python-2.x%'
      OR (
        LOWER(q.title) LIKE '%python 2%'
        OR LOWER(q.body) LIKE '%python 2%'
        OR LOWER(q.title) LIKE '%python2%'
        OR LOWER(q.body) LIKE '%python2%'
      ))
      AND (
        LOWER(q.title) NOT LIKE '%python 3%'
        AND LOWER(q.body) NOT LIKE '%python 3%'
        AND LOWER(q.title) NOT LIKE '%python3%'
        AND LOWER(q.body) NOT LIKE '%python3%'
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
  python2_questions q
LEFT JOIN
  `bigquery-public-data.stackoverflow.posts_answers` a
ON
  q.question_id = a.parent_id
    LIMIT 10
"""

query_job = client.query(query)
python_posts = [dict(row) for row in query_job]

print(len(python_posts))
# print(python_posts[0])

output_csv_path = "python_python_posts.csv"

import csv
with open(output_csv_path, mode="w", newline="", encoding="utf-8") as csvfile:
    fieldnames = python_posts[0].keys() if python_posts else []
    
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    
    writer.writeheader()
    writer.writerows(python_posts)

print(f"Results have been saved to {output_csv_path}")
