from auth.AUTH import AuthenticationCheck


class Customer(AuthenticationCheck):
    def __init__(self, db, ID_no, password):
        # do not initialize a new Database here; accept the shared instance
        AuthenticationCheck.__init__(self, db, ID_no, password)

    def addaccount(self,*args):
        pas = input("Enter your password: ")
        new = range(100000000000, 999999999999)
        # use Database wrapper methods
        self.db.execute_(
            "INSERT INTO customer (ID_NO,password, name, personal_id_type, personal_id, address, Phone_No, Email, Branch_NO) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            new,
            pas,
            args
        )
        self.db.commit_()
        return True

    # def update_pass( self,personal_id_type,personal_id):
    #     per_id_type=input("Enter personal id type: ")
    #     per_id=input("enter personal id: ")
    #     if per_id_type==personal_id_type and per_id==personal_id:
    #         new_pass=input("enter new password: ")
    #         self.db.cursor.execute(
    #         "UPDATE password FROM customer WHERE personal_id_type= ? AND personal_id = ?",
    #         (self.personal_id_type, self.personal_id)
    #     )

    def update_pass(self):
        """Update a customer's password by verifying personal id type and personal id.

        Prompts for `personal_id_type` and `personal_id`, verifies a matching
        customer row exists, then updates the `password` column.
        Returns True on success, False if no matching customer found.
        """
        per_id_type = input("Enter personal id type: ")
        per_id = input("Enter personal id: ")

        # Verify the customer exists
        row = self.db.fetchone_(
            "SELECT ID_NO FROM customer WHERE personal_id_type = ? AND personal_id = ?",
            per_id_type,
            per_id,
        )
        if not row:
            print("No customer found with the provided personal id type and id.")
            return False

        new_pass = input("Enter new password: ")
        self.db.execute_(
            "UPDATE customer SET password = ? WHERE personal_id_type = ? AND personal_id = ?",
            new_pass,
            per_id_type,
            per_id,
        )
        # Commit the change
        self.db.commit_()

        print("Password updated successfully.")

        return True

    def delete_acc(self):
        acc_no = input("Enter ID_no: ")
        # Verify account exists
        row = self.db.fetchone_(
            "SELECT ID_NO FROM customer WHERE ID_NO = ?",
            acc_no,
        )
        if not row:
            print("No customer found with the provided ID_no.")
            return False

        # Delete the customer
        self.db.execute_(
            "DELETE FROM customer WHERE ID_NO = ?",
            acc_no,
        )
        self.db.commit_()
        print("Account deleted successfully.")
        return True