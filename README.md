# Flask Application for Visualizing Taxi Dataset

This is a simple Flask application that fetches data from a Databricks Statement execution API and creates a few visualizations using Plotly.

![Screenshot 2023-05-01 at 11 11 14 pm](https://user-images.githubusercontent.com/2042132/235457049-b3227a60-6243-4880-bf4d-ec47684bcbe8.png)


## Prerequisites
Before running the application, you need to:

Have a Databricks workspace and a Databricks token with read access to your data.
Install the necessary packages using pip:
````bash
pip install flask plotly requests pandas numpy plotly.io
````
## Running the application

Replace the placeholders in the index() function with the relevant values for your Databricks workspace, token, catalog, schema, and warehouse ID.

Run the Flask app using flask run.

Visit http://localhost:5000 to see the visualizations.

## Code structure
The index() function in app.py is the main entry point for the application. It makes a POST request to the Databricks SQL endpoint to fetch the data, processes the data using pandas, and creates the visualizations using Plotly.

The templates/ directory contains the HTML templates for the app. In this case, there is only one template (index.html), which embeds the Plotly visualizations using the plotly.js library.

