import sqlite3

con = sqlite3.connect('menu.db')
cur = con.cursor()
cur.execute('''CREATE TABLE MENU
               (name text, protein real, fats real, carbs real, kcal real)''')
con.commit()
con.close()