import sqlite3

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

cursor.execute("DROP TABLE IF EXISTS blogs;")

conn.commit()
conn.close()

print("Blogs table dropped successfully.")
