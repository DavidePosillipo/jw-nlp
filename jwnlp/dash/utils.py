from sqlalchemy import text

def get_years(engine):
    results = engine.execute(text("SELECT DISTINCT year FROM (SELECT data->'year' AS year FROM watchtowers_articles) AS subquery;"))
    years = [y[0] for y in results.fetchall()]

    return years

def get_issues(engine, year: int):
    results = engine.execute(text(f"""
                SELECT DISTINCT issue_id 
                FROM (
                    SELECT data->'issue_id' AS issue_id 
                    FROM watchtowers_articles
                    WHERE data->'year' = '{year}'
                    ) AS subquery;
                """))
    issues = [i[0] for i in results.fetchall()]

    return issues

def get_articles(engine, year: int, issue_id: str):
    results = engine.execute(text(f"""
                SELECT 
                    data->'title' AS title,
                    data->'article_id' AS article_id
                FROM watchtowers_articles
                WHERE 
                    data->'year' = '{year}'
                    AND
                    data->'issue_id' = '\"{issue_id}\"';
                """))
    articles_titles_w_id = [(t[0], t[1]) for t in results.fetchall()]

    return articles_titles_w_id

def get_article_dict(engine, article_id: str):
    results = engine.execute(text(f"""
            SELECT
                data
            FROM
                watchtowers_articles
            WHERE
                data->'article_id' = '\"{article_id}\"'
            ;
            """))
    article_dict = results.fetchall()[0][0]

    return article_dict

