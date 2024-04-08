import psycopg2

def create_db(conn):
    
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS clients (
        id SERIAL PRIMARY KEY,
        first_name VARCHAR(50) NOT NULL,
        last_name VARCHAR(50) NOT NULL,
        email VARCHAR(100) UNIQUE,
        phones TEXT[]
    );
    """)
    conn.commit()

def add_client(conn, first_name, last_name, email, phones=None):
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO clients (first_name, last_name, email, phones)
    VALUES (%s, %s, %s, %s);
    """, (first_name, last_name, email, phones))
    conn.commit()

def add_phone(conn, client_id, phone):

    cursor = conn.cursor()
    cursor.execute("""
    UPDATE clients
    SET phones = array_append(phones, %s)
    WHERE id = %s;
    """, (phone, client_id))
    conn.commit()

def change_client(conn, client_id, first_name=None, last_name=None, email=None, phones=None):

    cursor = conn.cursor()
    update_query = "UPDATE clients SET "
    update_values = []
    
    if first_name:
        update_query += "first_name = %s, "
        update_values.append(first_name)
    if last_name:
        update_query += "last_name = %s, "
        update_values.append(last_name)
    if email:
        update_query += "email = %s, "
        update_values.append(email)
    if phones:
        update_query += "phones = %s, "
        update_values.append(phones)
    
    update_query = update_query[:-2]
    update_query += " WHERE id = %s;"
    update_values.append(client_id)
    
    cursor.execute(update_query, tuple(update_values))
    conn.commit()

def delete_phone(conn, client_id, phone):

    cursor = conn.cursor()
    cursor.execute("""
    UPDATE clients
    SET phones = array_remove(phones, %s)
    WHERE id = %s;
    """, (phone, client_id))
    conn.commit()

def delete_client(conn, client_id):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM clients WHERE id = %s;", (client_id,))
    conn.commit()

def find_client(conn, first_name=None, last_name=None, email=None, phone=None):

    cursor = conn.cursor()
    cursor.execute("""
    SELECT * FROM clients
    WHERE first_name = COALESCE(%s, first_name)
    AND last_name = COALESCE(%s, last_name)
    AND email = COALESCE(%s, email)
    AND %s = ANY(phones);
    """, (first_name, last_name, email, phone))
    result = cursor.fetchall()
    return result


with psycopg2.connect(database="clients_db", user="postgres", password="7Ff3imRYmE") as conn:
    create_db(conn)
    
    add_client(conn, "John", "Doe", "johndoe@example.com", ["123456789", "987654321"])
    add_phone(conn, 1, "999999999")
    change_client(conn, 1, last_name="Smith")
    delete_phone(conn, 1, "123456789")
    
conn.close()
