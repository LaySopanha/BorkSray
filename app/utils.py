import cohere
import pandas as pd
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Cohere client
co = cohere.Client(os.getenv("COHERE_API_KEY"))

def analyze_excel(file_stream):
    try:
        # Load the Excel file
        df = pd.read_excel(file_stream)

        # Check if the file is empty
        if df.empty:
            return None, "The uploaded file is empty. Please upload a valid Excel file with data."

        # Analyze each column to detect its type and compute relevant statistics
        data_info = []
        for col in df.columns:
            col_data = df[col]
            if pd.api.types.is_numeric_dtype(col_data):
                col_type = "numerical"
                summary = {
                    "mean": col_data.mean(),
                    "min": col_data.min(),
                    "max": col_data.max(),
                    "std_dev": col_data.std()
                }
            elif pd.api.types.is_datetime64_any_dtype(col_data):
                col_type = "datetime"
                summary = {
                    "earliest": col_data.min(),
                    "latest": col_data.max()
                }
            else:
                col_type = "categorical"
                summary = {
                    "top": col_data.mode()[0] if not col_data.mode().empty else None,
                    "unique_count": col_data.nunique()
                }

            # Store column info in a dictionary
            data_info.append({
                "name": col,
                "type": col_type,
                "summary": summary
            })

        return data_info, None  # Return the analysis and no error message

    except Exception as e:
        return None, f"Error processing the Excel file: {str(e)}"

def generate_data_summary(data_info):
    # Check if data_info is empty or invalid
    if not data_info:
        return None  # Return None to indicate no data

    summary_data = []
    for col_info in data_info:
        col_name = col_info["name"]
        col_type = col_info["type"]
        summary = col_info["summary"]

        if col_type == "numerical":
            summary_data.append({
                "name": col_name,
                "type": col_type,
                "mean": round(summary['mean'], 2),
                "min": summary['min'],
                "max": summary['max'],
                "std_dev": round(summary['std_dev'], 2)
            })
        elif col_type == "datetime":
            summary_data.append({
                "name": col_name,
                "type": col_type,
                "earliest": summary['earliest'],
                "latest": summary['latest']
            })
        else:
            summary_data.append({
                "name": col_name,
                "type": col_type,
                "top": summary['top'],
                "unique_count": summary['unique_count']
            })

    return summary_data  # Return structured summary data


def ask_cohere(query, data_info, max_tokens=60):
    # Generate a data summary dynamically based on data_info
    summary = generate_data_summary(data_info)

    # Flexible prompt to guide concise responses for various question types
    prompt = (
        "You are analyzing a dataset from an uploaded Excel file. The dataset has the following columns:\n\n"
        f"{summary}\n\n"
        f"Question: {query}\n\n"
        "Please provide a concise and direct answer based on the question asked. "
        "Only use relevant information from the data summary to answer accurately. "
        "Avoid adding interpretive analysis or commentary unless explicitly requested.\n\n"
        "Example questions you might receive include:\n"
        "- 'What is the average sales amount and sales range?'\n"
        "- 'Identify the most common product and region.'\n"
        "- 'Summarize key trends in sales figures.'\n"
        "- 'Provide the earliest and latest dates in the dataset.'"
    )

    # Call the Cohere API
    response = co.generate(
        model='command',  # Ensure this is a valid model
        prompt=prompt,
        max_tokens=max_tokens  # Adjust as needed for conciseness
    )
    return response.generations[0].text.strip()
