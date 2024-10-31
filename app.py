# Filename: app.py
import dash
from dash import html
#import dash_html_components as html


# Define the app
app = dash.Dash(__name__)
server = app.server  # expose the server variable for gunicorn

# Define layout
app.layout = html.Div([
    html.H1("Minimal Proxy App"),
    html.P("If you can see this, the deployment is successful!")
])

if __name__ == "__main__":
    app.run_server(debug=True)
