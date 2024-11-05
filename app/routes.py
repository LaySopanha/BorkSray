from flask import Blueprint, render_template, request, redirect, url_for, flash
import pandas as pd
import plotly.express as px
import plotly
import json
from .utils import analyze_excel, ask_cohere, generate_data_summary

main = Blueprint('main', __name__)

@main.route("/", methods=["GET", "POST"])
def index():
    response = None
    summary_data = None
    error_message = None
    charts = {}

    if request.method == "POST":
        if "file" in request.files:
            file = request.files["file"]
            # Load and analyze the Excel file
            data_info, error_message = analyze_excel(file)
            if error_message:
                flash(error_message)
                return redirect(url_for('main.index'))  # Redirect if there's an error
            
            if data_info:
                summary_data = generate_data_summary(data_info)
                
                # Load data for visualization
                df = pd.read_excel(file)
                
                # Generate metrics and charts
                charts['bar_product'] = create_bar_chart(df, 'Product')
                charts['bar_region'] = create_bar_chart(df, 'Region')
                if 'Sales' in df.columns and 'Date' in df.columns:
                    charts['line_sales'] = create_line_chart(df, 'Date', 'Sales')

        # Process the query if provided and there is no error
        if "query" in request.form and summary_data and not error_message:
            query = request.form["query"]
            response = ask_cohere(query, data_info)

        # Redirect to the dashboard and pass relevant data
        return render_template("dashboard.html", response=response, summary_data=summary_data, charts=charts)

    # Render the main page if GET request
    return render_template("index.html")

# Helper function to create bar charts
def create_bar_chart(df, column):
    if column in df.columns:
        # Get value counts and reset the index
        df_counts = df[column].value_counts().reset_index()
        # Rename columns for clarity
        df_counts.columns = [column, 'count']
        
        # Create the bar chart
        fig = px.bar(df_counts, x=column, y='count')
        fig.update_layout(title=f"Frequency of {column}", xaxis_title=column, yaxis_title="Count")
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return None

# Helper function to create a line chart for sales over time
def create_line_chart(df, date_col, sales_col):
    if date_col in df.columns and sales_col in df.columns:
        df[date_col] = pd.to_datetime(df[date_col])
        fig = px.line(df, x=date_col, y=sales_col, title="Sales Over Time")
        fig.update_layout(xaxis_title="Date", yaxis_title="Sales")
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return None