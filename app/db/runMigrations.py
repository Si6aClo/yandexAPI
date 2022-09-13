import os
import psycopg2

from settings import *

def main():
    connection = psycopg2.connect(
        dbname=DBNAME,
        user=USERNAME,
        password=PASSWORD,
        host=HOST
    )

    connection.autocommit = True
    cursor = connection.cursor()

    files_list = os.listdir(os.path.abspath('migrations'))

    for file_name in files_list:
        f = open(f'migrations/{file_name}', 'r')
        sql_query = f.read()
        cursor.execute(sql_query)
        print(f"Миграция {file_name} успешно завершена!")

if __name__ == '__main__':
    main()
