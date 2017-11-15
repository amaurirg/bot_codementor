import sqlite3


class DBHelper:
    def __init__(self, dbname="todo.sqlite"):
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname)

    def setup(self):
        tblstmt = "CREATE TABLE IF NOT EXISTS items (name text, owner text, description text)"
        itemidx = "CREATE INDEX IF NOT EXISTS itemIndex ON items (description ASC)"
        ownidx = "CREATE INDEX IF NOT EXISTS ownIndex ON items (owner ASC)"
        self.conn.execute(tblstmt)
        self.conn.execute(itemidx)
        self.conn.execute(ownidx)
        self.conn.commit()

    def add_item(self, name, owner, item_text):
        stmt = "INSERT INTO items (name, owner, description) VALUES (?, ?, ?)"
        args = (name, owner, item_text)
        self.conn.execute(stmt, args)
        self.conn.commit()

    def delete_item(self, owner, item_text):
        stmt = "DELETE FROM items WHERE owner = (?) AND description = (?)"
        args = (owner, item_text)
        self.conn.execute(stmt, args)
        self.conn.commit()

    def get_items(self, owner):
        stmt = "SELECT description FROM items WHERE owner = (?)"
        args = (owner,)
        return [x[0] for x in self.conn.execute(stmt, args)]

    def get_owner(self, owner = 200598266):
        stmt = "SELECT description FROM items WHERE owner = (?)"
        args = (owner,)
        return [x[0] for x in self.conn.execute(stmt, args)]

    def get_all(self):
        stmt = "SELECT description FROM items"
        return [x[0] for x in self.conn.execute(stmt)]
