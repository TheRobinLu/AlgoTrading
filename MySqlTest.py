import mysql.connector as conn

db = conn.connect(
    host='localhost',
    user='root',
    password='TToomm7&',
    database='stock'
)


def DBquery():
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

def SelectProc():
    mycursor = db.cursor()
    sql = "SELECT FROM p_bollinger()"


DBquery()