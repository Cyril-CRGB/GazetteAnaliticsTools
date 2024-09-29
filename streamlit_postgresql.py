import pandas as pd
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv
import env
import psycopg2 

load_dotenv() # Load environment variables from env.py file

DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL is None:
    raise ValueError('DATABASE_URL environnement variable is not set')
try:
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    print('Connected to the database successfully.')
except Exception as e:
    print(f"Error connecting to the database: {e}")