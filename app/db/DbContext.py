import psycopg2
from app.db.settings import DBNAME, PASSWORD, USERNAME, HOST


class DbContext:
    # Singleton pattern
    def __new__(cls):
        if not hasattr(cls, '__instance'):
            cls.__instance = super(DbContext, cls).__new__(cls)
        return cls.__instance

    def __init__(self):
        connection = psycopg2.connect(
            dbname=DBNAME,
            user=USERNAME,
            password=PASSWORD,
            host=HOST
        )

        connection.autocommit = True

        self.__cursor = connection.cursor()

    def contains_item_in_files(self, id: str) -> bool:
        self.__cursor.execute("""
            select * from file
            where id = %s
        """, (id,))

        data = self.__cursor.fetchone()

        return True if data is not None else False

    def contains_item_in_folders(self, id: str) -> bool:
        self.__cursor.execute("""
            select * from folder
            where id = %s
        """, (id,))

        data = self.__cursor.fetchone()

        return True if data is not None else False

    def insert_data(self, id, url, parent_id, size, date, type):
        if type == "FOLDER":
            self.__cursor.execute("""
                insert into folder (id, url, date, parentId, size)
                values (%s, %s, %s, %s, %s)
            """, (id, None, date, parent_id, 0,))
        else:
            self.__cursor.execute("""
                insert into file (id, url, date, parentId, size)
                values (%s, %s, %s, %s, %s)
            """, (id, url, date, parent_id, size,))

    def update_data(self, id, url, parent_id, size, date, type):
        if type == "FOLDER":
            self.__cursor.execute("""
                update folder
                set date = %s, parent_id = %s
                where id = %s
            """, (date, parent_id, id,))
        else:
            self.__cursor.execute("""
                update file
                set url = %s, date = %s, parent_id = %s, size = %s
                where id = %s
            """, (url, date, parent_id, size, id,))

    def delete_item(self, id: str) -> bool:
        item_in_files = self.contains_item_in_files(id)
        item_in_folders = self.contains_item_in_folders(id)
        if not (item_in_files or item_in_folders):
            return False
        else:
            if item_in_files:
                self.__cursor.execute("""
                    delete from file
                    where id = %s
                """, (id,))
            else:
                self.__cursor.execute("""
                    delete from folder
                    where id = %s
                """, (id,))
            return True

    def get_item_by_id(self, id, type):
        if type == "file":
            self.__cursor.execute("""
                select * from file
                where id = %s
            """, (id,))

            data = self.__cursor.fetchone()
        else:
            self.__cursor.execute("""
                select * from folder
                where id = %s
            """, (id,))

            data = self.__cursor.fetchone()

        return data

    def get_children_by_id(self, id):
        self.__cursor.execute("""
            select * from file
            where parentId = %s
        """, (id,))
        all_files = self.__cursor.fetchall()

        self.__cursor.execute("""
            select * from folder
            where parentId = %s
        """, (id,))
        all_folders = self.__cursor.fetchall()

        children_arr = []
        if all_folders is not None:
            for item in all_folders:
                children_arr.append({
                    "data": item,
                    "type": "folder"
                })
        if all_files is not None:
            for item in all_files:
                children_arr.append({
                    "data": item,
                    "type": "file"
                })

        return children_arr

    def get_files_by_date(self, date):
        self.__cursor.execute("""
            select * from file
            where date >= %s::timestamp - '1 day'::INTERVAL and date <= %s::timestamp
        """, (date, date,))

        data = self.__cursor.fetchall()
        return data

    def get_history_by_id(self, id, dateStart, dateEnd):
        in_files = self.contains_item_in_files(id)
        in_folders = self.contains_item_in_folders(id)

        if in_files or in_folders:
            self.__cursor.execute("""
                SELECT * FROM history 
                WHERE ItemId = %s AND Date < %s::timestamp AND Date >= %s::timestamp  
            """, (id, dateEnd, dateStart,))
            data = self.__cursor.fetchall()
            return data, True
        else:
            return None, False
    def __del__(self):
        self.__cursor.close()
