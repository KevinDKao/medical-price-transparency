import pandas as pd
from dash import Dash, html, dcc, Input, Output, State
import dash_leaflet as dl
import dash_bootstrap_components as dbc
from dash_iconify import DashIconify
from pathlib import Path

# App initialization
app = Dash(__name__, 
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap"
    ],
    suppress_callback_exceptions=True,
    title='EOM Provider Map'
)

# Constants
DEFAULT_ZOOM = 4
DEFAULT_CENTER = [39.8283, -98.5795]
THEME = {
    'bg': '#FFFFFF',
    'primary': '#2563EB',
    'secondary': '#64748B',
    'success': '#059669',
    'text': '#1E293B',
    'light': '#F1F5F9'
}

class Dashboard:
    def __init__(self):
        self.df = self.load_data()
        self.stats = self.calculate_stats()
        
    @staticmethod
    def load_data():
        df = pd.read_csv('cancer/data/clean_eom_data.csv')
        df['info'] = df.apply(lambda row: {
            'name': row['Organization Name'],
            'address': row['Street Address'],
            'city': row['City'],
            'state': row['State']
        }, axis=1)
        return df
    
    def calculate_stats(self):
        return {
            'total_providers': len(self.df),
            'total_states': self.df['State'].nunique(),
            'top_states': self.df['State'].value_counts().head(5).to_dict()
        }
    
    def create_markers(self):
        return dl.LayerGroup([
            dl.Marker(
                position=[row['Latitude'], row['Longitude']],
                children=[
                    dl.Tooltip(
                        self.create_tooltip_content(row['info']),
                        permanent=False,
                        direction="top"
                    )
                ],
                id={'type': 'marker', 'index': i}
            ) for i, row in self.df.iterrows()
        ])

    @staticmethod
    def create_tooltip_content(info):
        return html.Div([
            html.H6(info['name'], className="mb-2 font-weight-bold"),
            html.P([
                DashIconify(icon="carbon:location", className="me-2"),
                f"{info['address']}, {info['city']}, {info['state']}"
            ], className="mb-0 d-flex align-items-center")
        ], className="tooltip-content")

    def create_stats_cards(self):
        return dbc.Row([
            dbc.Col(
                dbc.Card([
                    dbc.CardBody([
                        html.H3(self.stats['total_providers'], className="mb-0 text-primary"),
                        html.P("Total Providers", className="text-muted mb-0")
                    ])
                ], className="shadow-sm")
            , width=6),
            dbc.Col(
                dbc.Card([
                    dbc.CardBody([
                        html.H3(self.stats['total_states'], className="mb-0 text-success"),
                        html.P("States Covered", className="text-muted mb-0")
                    ])
                ], className="shadow-sm")
            , width=6)
        ], className="mb-4")

    def create_layout(self):
        return html.Div([
            dbc.Container([
                dbc.Row([
                    dbc.Col([
                        html.H1("Enhancing Oncology Model Providers", 
                               className="text-center my-4 fw-bold"),
                        self.create_stats_cards(),
                        dbc.Card([
                            dbc.CardBody([
                                dl.Map([
                                    dl.TileLayer(
                                        url="https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}.png",
                                        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
                                    ),
                                    self.create_markers(),
                                    dl.FullScreenControl(position="topright"),
                                    dl.ScaleControl(position="bottomleft"),
                                ],
                                style={'height': '70vh', 'borderRadius': '8px'},
                                center=DEFAULT_CENTER,
                                zoom=DEFAULT_ZOOM,
                                )
                            ])
                        ], className="shadow-sm mb-4"),
                        dbc.Row([
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardHeader([
                                        html.H6("Top States", className="mb-0"),
                                    ], className="bg-light"),
                                    dbc.CardBody([
                                        html.Div([
                                            html.Div([
                                                html.Span(state, className="text-muted"),
                                                html.Span(count, className="ms-auto fw-bold")
                                            ], className="d-flex justify-content-between mb-2")
                                            for state, count in self.stats['top_states'].items()
                                        ])
                                    ])
                                ], className="shadow-sm")
                            ])
                        ])
                    ], width=12)
                ])
            ], fluid=True, className="dash-container px-4 py-3")
        ])

# Initialize dashboard and set layout
dashboard = Dashboard()
app.layout = dashboard.create_layout()

# Custom CSS
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>EOM Providers Dashboard</title>
        {%favicon%}
        {%css%}
        <link rel="stylesheet" href="/assets/styles.css">
        <style>
            body { 
                font-family: 'Inter', sans-serif;
                color: #1E293B;
            }
            .tooltip-content {
                background: white;
                border-radius: 8px;
                padding: 12px;
                box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
                min-width: 200px;
            }
            .card {
                border: none;
                border-radius: 12px;
            }
            .leaflet-container {
                font-family: 'Inter', sans-serif;
                border-radius: 8px;
            }
            .leaflet-tooltip {
                background: white;
                border: none;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                padding: 8px 12px;
                border-radius: 6px;
                font-size: 14px;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

if __name__ == '__main__':
    app.run_server(debug=True, port=8050)