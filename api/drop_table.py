import sqlite3

# Connect to the database
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Drop the blogs table
cursor.execute("DROP TABLE IF EXISTS blogs;")

# Commit changes and close the connection
conn.commit()
conn.close()

print("Blogs table dropped successfully.")
