/* The table containing the watchtowers articles, 
in all the retrieved languages. */
CREATE TABLE IF NOT EXISTS watchtowers_articles (
    wt_articles_key SERIAL PRIMARY KEY,
    data JSONB
);

/* Table containing the description of the
publications available in the database */
CREATE TABLE IF NOT EXISTS publications (
    publication_id SERIAL PRIMARY KEY,
    name VARCHAR,
    is_periodical BOOLEAN,
    last_update DATE
); 

/* Creating indeces */
CREATE INDEX idx_articleId ON watchtowers_articles ((data->'article_id'));
CREATE INDEX idx_year ON watchtowers_articles ((data->'year'));
 
