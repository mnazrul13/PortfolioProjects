# Import necessary modules
from db_connection import create_connection
import pandas as pd
from datetime import datetime
from meteostat import Hourly

# Use the connection
try:
    connection = create_connection()
    if connection.is_connected():
        print("Connected to MySQL database")
    
    # Set time period
    start = datetime(2024, 10, 9)
    end = datetime(2024, 11, 9, 23, 59)

    # Get hourly data from Meteostat
    data = Hourly('72254', start, end)
    data = data.fetch()
    
    data.reset_index(inplace=True)
    data.rename(columns={'index': 'time'}, inplace=True)  # Renames the index column to 'time'


    # Replace NaN with None for MySQL compatibility
    data = data.where(pd.notnull(data), None)

    # Calculate Fahrenheit and round to 2 decimal places
    data['temp_F'] = (data['temp'] * (9/5)) + 32
    data['temp_F'] = data['temp_F'].round(2)

    # Create the cursor
    cursor = connection.cursor()

    # Create table if it doesn't exist
    create_table_query = """
    CREATE TABLE IF NOT EXISTS austin_weather_data (
        time TIMESTAMP,
        temp FLOAT,
        dwpt FLOAT,
        rhum FLOAT,
        prcp FLOAT,
        snow FLOAT,
        wdir INT,
        wspd FLOAT,
        wpgt FLOAT,
        pres FLOAT,
        tsun FLOAT,
        coco INT,
        temp_F FLOAT
    )
    """
    cursor.execute(create_table_query)
    connection.commit()

    # Insert DataFrame rows into the table
    insert_query = """
    INSERT INTO austin_weather_data (time, temp, dwpt, rhum, prcp, snow, wdir, wspd, wpgt, pres, tsun, coco, temp_F)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    # Replace NaN values with None for all columns in the dataframe before insertion
    data = data.applymap(lambda x: None if pd.isna(x) else x)

    # Iterate over DataFrame rows and insert each row into the database
    for _, row in data.iterrows():
        cursor.execute(insert_query, tuple(row))
    connection.commit()

    print("Data inserted successfully into 'austin_weather_data' table.")

finally:
    # Ensure the connection is closed after operations are done
    if connection.is_connected():
        connection.close()
        print("Connection closed")
