import dash
from dash import dcc, html, Input, Output, State
import pandas as pd
import base64
import io
import time
from flask import Flask

server = Flask(__name__)  # Corrected initialization
app = dash.Dash(__name__, server=server)

app.layout = html.Div([
    html.H1("CSV Import and Configuration"),
    
    # Upload CSV file
    dcc.Upload(
        id="upload-data",
        children=html.Button("Upload CSV File"),
        multiple=False
    ),
    
    # Input for temperature sensors count
    html.Div("Enter Number of Temperature Sensors:"),
    dcc.Input(id="sensor-count", type="number", value=5, placeholder="Number of temp sensors"),
    
    # Input for output file path and name
    html.Div("Enter Output File Path and Name (e.g., C:/path_to_folder/Processed_Data.xlsx):"),
    dcc.Input(id="output-filepath", type="text", placeholder="Output file path", style={"width": "100%"}),
    
    html.Button("Process and Save", id="process-button", n_clicks=0),
    html.Div(id="file-info"),
    
    # Progress bar display
    html.Div(id="progress-status", style={"width": "100%", "border": "1px solid #000"}),
    html.Div(id="progress-bar", style={"width": "0%", "height": "30px", "backgroundColor": "#4CAF50"})
])

def parse_contents(contents, sensor_count):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
    
    # Process dataframe based on `sensor_count`
    df = df.shift(axis=1)
    df['TimeStamp'] = df.index
    cols = ['TimeStamp'] + [col for col in df.columns if col != 'TimeStamp']
    df = df[cols]
    df.reset_index(drop=True, inplace=True)
    
    # Process sensor columns
    t_columns = [col for col in df.columns if col.startswith('T')]
    df = pd.concat([df.drop(t_columns, axis=1), df[t_columns[:sensor_count]]], axis=1)
    
    return df

@app.callback(
    [Output("file-info", "children"), Output("progress-bar", "style")],
    [Input("process-button", "n_clicks")],
    [State("upload-data", "contents"), State("sensor-count", "value"), State("output-filepath", "value")]
)
def update_output(n_clicks, contents, sensor_count, output_filepath):
    if contents is not None and n_clicks > 0:
        # Process the file
        df = parse_contents(contents, sensor_count)
        
        # Save processed data to the specified path
        try:
            output_path = output_filepath.strip()  # Ensure no leading/trailing spaces
            df.to_excel(output_path, index=False)
            download_message = f"Data processed and saved to {output_path}"
        except Exception as e:
            download_message = f"Error saving file: {e}"
        
        # Simulate progress for the progress bar
        for i in range(100):
            time.sleep(0.02)  # Simulate processing time
            progress_style = {"width": f"{i+1}%", "height": "30px", "backgroundColor": "#4CAF50"}
        
        return download_message, progress_style

    return "Please upload a CSV file and set parameters.", {"width": "0%", "height": "30px", "backgroundColor": "#4CAF50"}

if __name__ == "__main__":
    app.run_server(debug=True)
