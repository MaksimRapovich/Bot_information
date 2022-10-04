import sqlite3
conn = sqlite3.connect('botinformation.db')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE users (id VARCHAR(255), lang VARCHAR(255))''')
