import mysql.connector

config = {
    'user':'todos',
    'password':'todos',
    'host' : 'localhost',
    'database' : 'todos',
    'raise_on_warnings':True
}

try:
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()

    query = "SELECT * FROM users;"
    cursor.execute(query)

    rows = cursor.fetchall()
    for row in rows:
        print(row)

except mysql.connector.Error as err:
    print("Error: ", err)

finally:
    cursor.close()
    connection.close()