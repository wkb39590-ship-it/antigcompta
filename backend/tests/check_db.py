import sqlite3
import os

db_path = 'test.db'
if not os.path.exists(db_path):
    print(f"File {db_path} not found")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()
codes = ['2355', '2835', '6193', '6181']
placeholders = ', '.join(['?'] * len(codes))
cursor.execute(f'SELECT code, label FROM comptes_pcm WHERE code IN ({placeholders})', codes)
rows = cursor.fetchall()
print("--- Search Results ---")
for r in rows:
    print(f"{r[0]} | {r[1]}")

cursor.execute('SELECT COUNT(*) FROM comptes_pcm')
count = cursor.fetchone()[0]
print(f"Total accounts in table: {count}")
conn.close()
