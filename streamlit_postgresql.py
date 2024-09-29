import pandas as pd
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

load_dotenv() # Load environment variables from .env file

# Heroku DATABASE_URL from environment variables
DATABASE_URL = os.environ.get('DATABASE_URL')

# Load the csv file into a DataFrame
csv_file_path = 'inputs/datasets/raw/Crime_Data_from_2020_to_Present.csv' 
df = pd.read_csv(csv_file_path)

# Create a database engine
engine = create_engine(DATABASE_URL)

# Write the DataFrame to PostgreSQL
df.to_sql('crime_data_from_2020_to_present', engine, if_exists='replace', index=False)