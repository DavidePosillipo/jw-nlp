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
    name VARCHAR UNIQUE,
    is_periodical BOOLEAN,
    is_batch_downloaded BOOLEAN,
    last_update DATE
); 

/* Creating indeces */
CREATE INDEX IF NOT EXISTS idx_articleId ON watchtowers_articles ((data->'article_id'));
CREATE INDEX IF NOT EXISTS idx_year ON watchtowers_articles ((data->'year'));

/* Setting up the publications table */
INSERT INTO publications(name, is_periodical, is_batch_downloaded, last_update) 
    VALUES ('Watchtower', true, false, CURRENT_DATE)
    ON CONFLICT (name) DO NOTHING;
 
