import sqlite3

con = sqlite3.connect('ProtFatCarbKCal.db')
cur = con.cursor()
cur.execute('''CREATE TABLE PFCKC
               (date text, time text, name text, protein real, fats real, carbs real, kcal real)'''
            )
con.commit()
con.close()