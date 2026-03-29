import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, dash_table
import plotly.express as px
import pandas as pd
from ..database import get_trades

def create_dashboard():
    app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CERULEAN])

    trades = get_trades()
    trade_list = [
        {
            "Ticker":t.ticker,
            "Issuer":t.issuer_name,
            "Type":t.transaction_type,
            "Date":t.transaction_date,
            "Amount":t.amount_range
        } for t in trades
    ]
    df = pd.DataFrame(trade_list)

    if not df.empty:
        ticker_counts = df['Ticker'].value_counts().reset_index()
        ticker_counts.columns=['Ticker', 'Count']
        fig = px.bar(ticker_counts, x='Ticker', y='Count', title='Trades by Ticker')
    else:
        fig = px.line(title="No data available")

    app.layout = dbc.Container([
        dbc.Row([
            dbc.Col(html.H1("Nancy Pelosi Trade Tracker", className="text-center my-4"),width=12)
        ]),
        dbc.Row([
            dbc.Col(dbc.Card([
                dbc.CardBody([
                    html.H4("Total Trades", className="card-title"),
                    html.H2(f"{len(df)}", className="card-text text-primary"),
                ])
            ], class_name="mb-4"),width=4),
        ]),
        dbc.Row([
            dbc.Col(dcc.Graph(figure=fig), width=12, className="mb-4")
        ]),

        dbc.Row([
            dbc.Col([
                html.H2("Recent Activity"),
                dash_table.DataTable(
                    data=df.to_dict('records') if not df.empty else [],
                    columns=[{"name": i, "id": i} for i in df.columns],
                    page_size=12,
                    style_table={'overflowX':'auto'},
                    style_header={
                        'backgroundColor':'rgb(210,210,210)',
                        'fontWeight':'bold'
                    },
                    style_cell={'textAlign': 'left'}
                )
            ], width=12)
        ])
    ])
    return app