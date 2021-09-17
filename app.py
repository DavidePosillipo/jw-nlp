# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.express as px
import pandas as pd

import psycopg2
from jwnlp.utils.config import Config
from jwnlp.dash.utils import (
	get_years, get_issues, get_articles, get_article_dict
)
from jwnlp.nlp.summarization.summarize_article import summarize_article

app = dash.Dash(__name__)

##### CONFIGS #####

database = Config.database_name
user = Config.user_name

conn = psycopg2.connect(f"dbname={database} user={user}")

years = get_years(conn)

##### LAYOUT #####

app.layout = html.Div([
    dcc.Dropdown(
        id='years-dropdown',
        options=[{'label': year, 'value': year} for year in years],
        value=2006
    ),

    html.Hr(),

    dcc.Dropdown(id='issues-dropdown'),

    html.Hr(),

    dcc.Dropdown(id='articles-dropdown'),
    
    html.Hr(),

    html.Div(id='article-id-hidden', style={'display': 'none'}),

    html.Hr(),

    html.Button(id='submit-button-state', n_clicks=0, children='Submit'),

    html.Hr(),

    html.Div(id='article-summary')

])

##### CALLBACK ####

### Issues dropdown ###
@app.callback(
    dash.dependencies.Output('issues-dropdown', 'options'),
    [dash.dependencies.Input('years-dropdown', 'value')])
def set_issues_options(selected_year):
    issues = get_issues(conn, int(selected_year))
    return [{'label': i, 'value': i} for i in issues]

@app.callback(
    dash.dependencies.Output('issues-dropdown', 'value'),
    [dash.dependencies.Input('issues-dropdown', 'options')])
def set_issues_value(available_options):
    return available_options[0]['value']

### Articles dropdown ###
@app.callback(
    dash.dependencies.Output('articles-dropdown', 'options'),
    [dash.dependencies.Input('years-dropdown', 'value'),
     dash.dependencies.Input('issues-dropdown', 'value')]
)
def set_issues_options(selected_year, selected_issue):
    issues = get_issues(conn, int(selected_year))
    articles = get_articles(conn, int(selected_year), selected_issue)
    # title[0] is the title, title[1] is the ID
    return [{'label': title[0], 'value': " | ".join([title[0], title[1]])} for title in articles]

@app.callback(
    dash.dependencies.Output('articles-dropdown', 'value'),
    [dash.dependencies.Input('articles-dropdown', 'options')])
def set_issues_value(available_options):
    return available_options[0]['value']

# Setting article id
@app.callback(
    dash.dependencies.Output('article-id-hidden', 'children'),
    [dash.dependencies.Input('articles-dropdown', 'value')])
def set_articles_id_value(value):
    """
    Returns the ID of the article and set it as the value
    for the dropdown menu
    """
    return value.split("|")[1].strip()

### Article summary ###
@app.callback(
    dash.dependencies.Output('article-summary', 'children'),
    dash.dependencies.Output('submit-button-state', 'n_clicks'),
    [dash.dependencies.Input('article-id-hidden', 'children'),
     dash.dependencies.Input('submit-button-state', 'n_clicks')]
)
def summarize_selected_article(article_id, n_clicks):
    """
    Triggers the summarize_article function and reset the click counts
    to avoid that the task starts again when the user selects a new
    article but doesn't click on Submit.
    """
    if n_clicks>0:
        article_dict = get_article_dict(conn, article_id)
        summary = summarize_article(article_dict)
        return summary, 0
    else:
        return "Please select an article and click the Submit button", 0
 
if __name__ == '__main__':
    app.run_server(debug=True)
