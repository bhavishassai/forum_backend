import mysql.connector


# passwords are stored in a separate file or as environment variables
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="lab@Sql6",
    database="forum"
)


cursor = conn.cursor()