from google.cloud import bigquery

client = bigquery.Client()

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
          AND (
            LOWER(q.title) LIKE '%beginner%'
            OR LOWER(q.title) LIKE '%basic%'
            OR LOWER(q.body) LIKE '%beginner%'
            OR LOWER(q.body) LIKE '%basic%'
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
    WHERE
      LOWER(a.body) LIKE '%lxml%'
    LIMIT 10
"""

query_job = client.query(query)
lxml_python_posts = [dict(row) for row in query_job]

print(len(lxml_python_posts))
# print(lxml_python_posts[0])

output_csv_path = "lxml_python_posts.csv"

import csv
with open(output_csv_path, mode="w", newline="", encoding="utf-8") as csvfile:
    fieldnames = lxml_python_posts[0].keys() if lxml_python_posts else []
    
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    
    writer.writeheader()
    writer.writerows(lxml_python_posts)

print(f"Results have been saved to {output_csv_path}")
