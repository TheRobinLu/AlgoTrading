import mysql.connector as conn

db = conn.connect(
    host='localhost',
    user='root',
    password='1234',
    database='stock'
)

mycursor = db.cursor()
mycursor.execute("SHOW DATABASES")
print("DATABASES")
for x in mycursor:
    print(x)

print("TABLES")
mycursor.execute("SHOW TABLES")
for x in mycursor:
    print(x)

# mycursor.execute("CREATE TABLE test (name VARCHAR(255), address VARCHAR(255))")

mycursor.execute("INSERT test (name , address ) VALUES ('Peter Pan', 'Silver Treasure Island') ")

db.commit()
