import postgresql

class DbWrapper:
    def __init__(self, db_string, table_name):
        self.db = postgresql.open(db_string)
        self.table_name = table_name
        self.st_get_user_by_password = self.db.prepare("SELECT id, mumble_username FROM {} WHERE mumble_authkey = $1".format(table_name))

    def get_user_by_password(self, password):
        assert(type(password) is str)
        s = self.st_get_user_by_password.first(password)

        return s
