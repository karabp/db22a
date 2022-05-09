from django.conf import settings

import os.path
import pymysql.cursors

def mariadb_create_connection():
    return pymysql.connect(host='localhost',
                           user=settings.MARIADB['USER'],
                           password=settings.MARIADB['PASSWORD'],
                           db=settings.MARIADB['NAME'],
                           charset='utf8',
                           cursorclass=pymysql.cursors.DictCursor)

def mariadb_execute_script(file, nosplit=False):
    # Construct the script path
    script_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database_scripts', file)

    # Connect to the database
    connection = mariadb_create_connection()
    connection.begin()
    executed_statements = 0

    try:
        with open(script_path) as file:
            with connection.cursor() as cursor:
                sql = file.read()

                # Split the script into statements, as the pymysql
                # driver cannot handle multiple statements.
                #
                # WARNING: This form of parsing is very rudimentary,
                #          it is only intended to work with the
                #          shipped DDL scripts.
                if not nosplit:
                    statements = sql.split(';');
                else:
                    statements = [sql];
                for statement in statements:
                    if statement == '' or str.isspace(statement):
                       continue
                    cursor.execute(statement)
                    executed_statements += 1
            connection.commit()
    finally:
        connection.close()
    return executed_statements

def mariadb_insert_many(query, args):
    connection = mariadb_create_connection()

    try:
        with connection.cursor() as cursor:
            cursor.executemany(query, args)
        connection.commit()
    finally:
        connection.close()

def mariadb_select_one(query, args):
    connection = mariadb_create_connection()
    try:
        with connection.cursor() as cursor:
            print(cursor.mogrify(query, args))
            cursor.execute(query, args)
            result = cursor.fetchone()
    finally:
        connection.close()
    return result

def mariadb_select_all(query, args):
    connection = mariadb_create_connection()
    try:
        with connection.cursor() as cursor:
            print(cursor.mogrify(query, args))
            cursor.execute(query, args)
            result = cursor.fetchall()
    finally:
        connection.close()
    return result
