def get_years(connection):
    cur = connection.cursor()
    cur.execute(f"SELECT DISTINCT year FROM (SELECT data->'year' AS year FROM watchtowers_articles) AS subquery;")
    years = [y[0] for y in cur.fetchall()]

    return years

def get_issues(connection, year: int):
    cur = connection.cursor()
    cur.execute(f"""
                SELECT DISTINCT issue_id 
                FROM (
                    SELECT data->'issue_id' AS issue_id 
                    FROM watchtowers_articles
                    WHERE data->'year' = '{year}'
                    ) AS subquery;
                """)
    issues = [i[0] for i in cur.fetchall()]

    return issues

def get_articles(connection, year: int, issue_id: str):
    cur = connection.cursor()
    cur.execute(f"""
                SELECT 
                    data->'title' AS title,
                    data->'article_id' AS article_id
                FROM watchtowers_articles
                WHERE 
                    data->'year' = '{year}'
                    AND
                    data->'issue_id' = '\"{issue_id}\"';
                """)
    articles_titles_w_id = [(t[0], t[1]) for t in cur.fetchall()]

    return articles_titles_w_id

def get_article_dict(connection, article_id: str):
    cur = connection.cursor()
    cur.execute(f"""
            SELECT
                data
            FROM
                watchtowers_articles
            WHERE
                data->'article_id' = '\"{article_id}\"'
            ;
            """)
    article_dict = cur.fetchall()[0][0]

    return article_dict

