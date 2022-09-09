import mysql.connector
from os import environ
from dotenv import load_dotenv

load_dotenv()

DB_HOST = environ.get("DB_HOST")
DB_USER =environ.get("DB_USER")
DB_PASSWORD =environ.get("DB_PASSWORD")
DB_NAME = environ.get("DB_NAME")

conn = mysql.connector.connect(
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASSWORD,
    database=DB_NAME,
)


cursor = conn.cursor()