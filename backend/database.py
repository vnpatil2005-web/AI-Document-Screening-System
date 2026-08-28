import mysql.connector


def get_connection():

    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="ai_document_screening"
    )

    return connection