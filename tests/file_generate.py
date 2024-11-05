import pandas as pd



# Define the sample data
data = {
    'Product': ['Widget A', 'Widget B', 'Widget A', 'Widget C', 'Widget B', 'Widget C', 'Widget A'],
    'Sales': [500, 300, 450, 700, 350, 650, 400],
    'Date': ['2024-01-01', '2024-01-02', '2024-01-03', '2024-01-04', '2024-01-05', '2024-01-06', '2024-01-07'],
    'Region': ['North', 'South', 'East', 'West', 'North', 'South', 'West']
}

# Create a DataFrame from the data
df = pd.DataFrame(data)

# Convert 'Date' column to datetime type
df['Date'] = pd.to_datetime(df['Date'])

# Save the DataFrame to an Excel file
df.to_excel('sales_data.xlsx', index=False)

print("Test Excel file 'sales_data.xlsx' created successfully.")
