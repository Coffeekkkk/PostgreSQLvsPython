import psycopg2
from config import user, db_name, password

try:
    connection = psycopg2.connect(
        database=db_name,
        user=user,
        password=password
    )

except Exception as _ex:
    print('[INFO] Error while working with PostgreSQL', _ex)


def create_tables():
    with connection.cursor() as cursor:
        cursor.execute(
            '''CREATE TABLE IF NOT EXISTS clients(
            id SERIAL PRIMARY KEY,
            name VARCHAR(60) NOT NULL,
            surname VARCHAR(60) NOT NULL,
            email VARCHAR(70) UNIQUE
            );
            CREATE TABLE IF NOT EXISTS phones(
            id SERIAL PRIMARY KEY,
            phone VARCHAR(60) UNIQUE,
            fk_client_id INT REFERENCES clients(id)
            );'''
        )
        connection.commit()


def add_client(name, surname, email, phone=None):
    with connection.cursor() as cursor:
        cursor.execute(
            '''INSERT INTO clients (name, surname, email)
            VALUES (%s, %s, %s) RETURNING id;''', (name, surname, email)
        )
        id = cursor.fetchone()[0]
        cursor.execute(
            '''INSERT INTO phones (phone, fk_client_id)
            VALUES (%s, %s);''', (phone, id)
        )

        connection.commit()
        print('Client added')


def add_phone(client_id, phone):
    with connection.cursor() as cursor:
        cursor.execute(
            '''INSERT INTO phones (phone, fk_client_id)
            VALUES (%s, %s);''', (phone, client_id)
        )
        connection.commit()


def change_client(client_id, name=None, surname=None, email=None, phone=None):
    with connection.cursor() as cursor:
        cursor.execute(
            '''SELECT name, surname, email, phone FROM clients c
            LEFT JOIN phones p ON c.id = p.fk_client_id
            WHERE c.id = %s''', (client_id,)
        )
        info = cursor.fetchone()
        if name is None:
            name = info[0]
        if surname is None:
            surname = info[1]
        if email is None:
            email = info[2]
        if phone is None:
            phone = info[3]
        cursor.execute(
            '''UPDATE clients
            SET name = %s, surname = %s, email = %s
            WHERE id = %s;
            UPDATE phones
            SET phone = %s
            WHERE fk_client_id = %s''', (name, surname, email, client_id, phone, client_id)
        )
        connection.commit()
        return print("Изменения внесены")


def delete_phone(client_id, phone=None):
    with connection.cursor() as cursor:
        cursor.execute(
            '''DELETE FROM phones 
            WHERE fk_client_id = %s OR phone = %s
            ''', (client_id, phone)
        )
        connection.commit()


def delete_client(client_id):
    with connection.cursor() as cursor:
        cursor.execute(
            '''DELETE FROM phones 
            WHERE fk_client_id = %s; 
            DELETE FROM clients 
            WHERE id = %s''', (client_id, client_id)
        )
        connection.commit()


def find_client(name=None, surname=None, email=None, phone=None):
    if name is None:
        name = '%'
    else:
        name = '%' + name + '%'
    if surname is None:
        surname = '%'
    else:
        surname = '%' + surname + '%'
    if email is None:
        email = '%'
    else:
        email = '%' + email + '%'
    if phone is None:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT c.id, name, surname, email, phone FROM clients c
                LEFT JOIN phones p ON c.id = p.fk_client_id
                WHERE c.name iLIKE %s AND c.surname iLIKE %s
                AND c.email iLIKE %s AND p.phone IS %s
                """, (name, surname, email, phone))
            x = [i for i in cursor.fetchall()]
            for i in x:
                print(i)
    else:
        phone = '%' + phone + '%'
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT c.id, name, surname, email, phone FROM clients c
                LEFT JOIN phones p ON c.id = p.fk_client_id
                WHERE c.name iLIKE %s AND c.surname iLIKE %s
                AND c.email iLIKE %s AND p.phone LIKE %s
                """, (name, surname, email, phone))
            x = [i for i in cursor.fetchall()]
            for i in x:
                print(i)


create_tables()
add_client('Denis', 'Kravchenko', 'pochtatdemal.co')
add_phone(4, '222')
change_client(1, name='Fedor', phone='1111111')
delete_phone(2)
delete_client(1)
find_client(name='Denis')

connection.close()
