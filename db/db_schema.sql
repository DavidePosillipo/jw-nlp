/* The table containing the watchtowers articles, 
in all the retrieved languages.
The primary key will be article_id + language,
because the article_id is common for every language */
CREATE TABLE IF NOT EXISTS watchtowers_articles (
    wt_articles_key VARCHAR (50) PRIMARY KEY,
    article_id VARCHAR (10),
    year INTEGER,
    edition VARCHAR (10),
    url VARCHAR,
    language VARCHAR (5),
    issue_id VARCHAR (10),
    title VARCHAR,
    paragraphs JSONB
)

-- TODO create index?

/* Table containing the description of the
publications available in the database */
CREATE TABLE IF NOT EXISTS publications (
    publication_id SERIAL PRIMARY KEY,
    name VARCHAR,
    is_periodical BOOLEAN,
    last_update DATE
) 
 
