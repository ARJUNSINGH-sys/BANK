
from database.databade import db as default_db


# decorator for auth 
def authorise(func):
    def wrapper(*args,**kawargs):
        main=func(*args,**kawargs) #this func asks password and vaildates it
        return main
    return wrapper

def logout(func):
    def wrapper(*args,**kwargs):
        log_out=func(*args,**kwargs)
        return log_out
    return wrapper
        

class AuthenticationCheck:
    def __init__(self, db=default_db, ID_no=None, PASSWORD=None):
        """Accept a shared `Database` instance and credentials.

        By default this uses the shared instance from `database.databade`.
        Custom instances can still be injected for tests or alternate DBs.
        """
        self.db = db
        self.__Account_no = ID_no
        self.__password = PASSWORD

    def get_Account_no(self):
        return self.__Account_no

    def set_Account_no(self, ID_no):
        self.__Account_no = ID_no

    def get_password(self):
        return self.__password

    def set_password(self, PASSWORD):
        self.__password = PASSWORD

    def login(self):
        row = self.db.fetchone_(
            "SELECT ID_no, password FROM customer WHERE ID_no = ? AND password = ?",
            self.get_Account_no(),
            self.get_password(),
        )
        if row is None:
            print("access denied, have you forget password? or please make sure you have an account")
            return False
        else:
            return True

    def logout(self):
        value = input("do you want to logout?? yes or no")
        return value.strip().lower() == "yes"

