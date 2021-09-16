/* The table containing the watchtowers articles, 
in all the retrieved languages. */
CREATE TABLE IF NOT EXISTS watchtowers_articles (
    wt_articles_key SERIAL PRIMARY KEY,
    data JSONB
);

/* Table containing the description of the
publications available in the database */
CREATE TABLE IF NOT EXISTS publications (
    name VARCHAR NOT NULL,
    language VARCHAR NOT NULL,
    is_periodical BOOLEAN,
    is_batch_downloaded BOOLEAN,
    is_batch_uploaded_on_db BOOLEAN,
    creation_date DATE,
    last_update DATE,
    PRIMARY KEY (name, language)
); 

/* Creating indeces */
CREATE INDEX IF NOT EXISTS idx_articleId ON watchtowers_articles ((data->'article_id'));
CREATE INDEX IF NOT EXISTS idx_year ON watchtowers_articles ((data->'year'));
