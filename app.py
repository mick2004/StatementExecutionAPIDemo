import plotly
from flask import Flask, render_template
import plotly.graph_objs as go
import json
import requests
import pandas as pd
import numpy as np
import plotly.io as pio


app = Flask(__name__)


@app.route("/")
def index():
    # Define the API endpoint and headers
    url = 'https://<<Databricks Workspace>>/api/2.0/sql/statements'
    headers = {'Authorization': 'Bearer <<Databricks Token>>'}

    # Define the data you want to post
    data = {
        "on_wait_timeout": "CANCEL",
        "statement": "select trip_distance,total_amount as Total_Amt,pickup_ts as Trip_Pickup_DateTime,payment_type as Payment_Type,rate_code as Rate_Code from <<catalog>>.<<schema>>.nyctaxi where Rate_Code is not null  and total_amount is  not null limit 100000;",
        "wait_timeout": "30s",
        "warehouse_id": "<<warehouseid>>"
    }

    # Set the default theme for all charts
    pio.templates.default = "plotly_dark"

    # Define the colors to use for each chart
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']

    # Make the POST request with the specified headers and data
    response = requests.post(url, headers=headers, json=data)

    # Parse the JSON response into a dictionary
    data = response.json()


    # Define the schema
    schema = {
        "fields": [
            {'name': 'trip_distance', 'type': 'float'},
            {'name': 'Total_Amt', 'type': 'float'},
            {'name': 'Trip_Pickup_DateTime', 'type': 'datetime64[ns]'},
            {'name': 'Payment_Type', 'type': 'object'},
            {'name': 'Rate_Code', 'type': 'int'}
        ],
        "metadata": {"key": "value"}
    }

    df = pd.DataFrame(data["result"]["data_array"], columns=[field["name"] for field in schema["fields"]])
    df['Trip_Pickup_DateTime'] = pd.to_datetime(df['Trip_Pickup_DateTime']).dt.tz_localize(None)
    # Convert the 'Rate_Code' column to a float, but first replace any None values with NaN
    df['Rate_Code'] = df['Rate_Code'].replace({None: np.nan}).astype(float)
    df = df.astype({field["name"]: field["type"] for field in schema["fields"]})


    # Filter the DataFrame to only include trips with a fare amount greater than 0
    df = df[df['Total_Amt'] > 0]

    # Group the trips by pickup hour and calculate the average fare amount for each hour
    df_grouped_hour = df.groupby(pd.to_datetime(df['Trip_Pickup_DateTime']).dt.hour)['Total_Amt'].mean()

    # Group the trips by payment type and calculate the average fare amount for each payment type
    df_grouped_payment = df.groupby(['Payment_Type'])['Total_Amt'].mean()

    # Group the trips by rate code and calculate the average fare amount for each rate code
    df_grouped_ratecode = df.groupby(['Rate_Code'])['Total_Amt'].mean()

    # Convert the grouped data to lists for use in Plotly charts
    x_data_hour = list(df_grouped_hour.index)
    y_data_hour = list(df_grouped_hour.values)
    x_data_payment = list(df_grouped_payment.index)
    y_data_payment = list(df_grouped_payment.values)
    x_data_ratecode = list(df_grouped_ratecode.index)
    y_data_ratecode = list(df_grouped_ratecode.values)



    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=x_data_hour, y=y_data_hour, mode='lines', line=dict(color=colors[0], width=3)))

    # Set the chart title and axis labels
    fig1.update_layout(title='Average Fare Amount by Pickup Hour',
                       xaxis_title='Pickup Hour',
                       yaxis_title='Average Fare Amount',
                       font=dict(size=14))

    # Create a Plotly bar chart with the grouped data for payment type
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(x=x_data_payment, y=y_data_payment))



    fig2 = go.Figure()
    fig2.add_trace(go.Bar(x=x_data_payment, y=y_data_payment, marker=dict(color=colors[1])))

    # Set the chart title and axis labels
    fig2.update_layout(title='Average Fare Amount by Payment Type',
                       xaxis_title='Payment Type',
                       yaxis_title='Average Fare Amount',
                       font=dict(size=14))

    # Create a Plotly pie chart with the grouped data for rate code

    fig3 = go.Figure()
    fig3.add_trace(go.Pie(labels=x_data_ratecode, values=y_data_ratecode, marker=dict(colors=colors[2:])))

    # Set the chart title and axis labels
    fig3.update_layout(title='Average Fare Amount by Rate Code',
                       font=dict(size=14))

    # Create a Plotly scatter plot with the grouped data for trip distance and fare amount

    fig4 = go.Figure()
    fig4.add_trace(
        go.Scatter(x=df['trip_distance'], y=df['Total_Amt'], mode='markers', marker=dict(color=colors[3], size=5)))

    # Set the chart title and axis labels
    fig4.update_layout(title='Trip Distance vs Fare Amount',
                       xaxis_title='Trip Distance (miles)',
                       yaxis_title='Fare Amount',
                       font=dict(size=14))



    # Create a Plotly bar chart with the grouped data for rate code and payment type
    df_grouped_ratecode_payment = df.groupby(['Rate_Code', 'Payment_Type'])['Total_Amt'].mean()
    fig5 = go.Figure()
    for payment_type in df_grouped_ratecode_payment.index.get_level_values(1).unique():
        df_filtered = df_grouped_ratecode_payment.xs(payment_type, level=1)
        fig5.add_trace(go.Bar(x=df_filtered.index, y=df_filtered.values, name=payment_type))

    # Set the chart title and axis labels
    fig5.update_layout(title='Average Fare by Rate Code and Payment Type',
                       xaxis_title='Rate Code',
                       yaxis_title='Average Fare Amount',
                       font=dict(size=14),
                       barmode='group',
                       legend=dict(font=dict(size=12)))


    # Convert the Plotly charts to JSON for use in the webpage
    chart1JSON = json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder)
    chart2JSON = json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)
    chart3JSON = json.dumps(fig3, cls=plotly.utils.PlotlyJSONEncoder)
    chart4JSON = json.dumps(fig4, cls=plotly.utils.PlotlyJSONEncoder)
    chart5JSON = json.dumps(fig5, cls=plotly.utils.PlotlyJSONEncoder)

    # Render the webpage with the Plotly charts
    return render_template('index.html', chart1JSON=chart1JSON, chart2JSON=chart2JSON, chart3JSON=chart3JSON, chart4JSON=chart4JSON, chart5JSON=chart5JSON)

if __name__ == '__main__':
    app.run()
