import sqlite3

# Connect to the database
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Get the structure of the blogs table
cursor.execute("PRAGMA table_info(blogs);")
columns = cursor.fetchall()

print("Blogs table columns:", columns)

conn.close()