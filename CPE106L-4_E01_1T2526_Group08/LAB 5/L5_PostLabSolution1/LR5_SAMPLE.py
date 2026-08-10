import sqlite3

conn = sqlite3.connect('chinook.db')
cursor = conn.cursor()

cursor.execute("SELECT Title FROM albums WHERE ArtistId = 1") 

albums = cursor.fetchall()
for album in albums:
    print(album)

conn.close()
