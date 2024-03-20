import mysql.connector as mysql

DEFAULT_ADMIN_USERNAME = 'admin'
DEFAULT_ADMIN_PASSWORD = 'admin'

# Database class for managing database connections and operations
class Database:
    def __init__(self):
        # Establishing a connection to the MySQL database
        self.db = mysql.connect(host='localhost', user='root', password='', database='school')
        # Creating a cursor object for executing SQL queries
        self.command_handler = self.db.cursor(buffered=True)

    # Method to execute SQL queries with or without parameters
    def execute_query(self, query, values=None):
        if values:
            self.command_handler.execute(query, values)
        else:
            self.command_handler.execute(query)

    # Method to fetch all records returned by a query
    def fetch_all(self):
        return self.command_handler.fetchall()

    # Method to commit changes to the database
    def commit(self):
        self.db.commit()

# User base class representing a generic user
class User:
    def __init__(self, username, password):
        self.username = username
        self.password = password

    # Method to authenticate user based on provided password
    def authenticate(self, provided_password):
        return self.password == self._hash_password(provided_password)

    # Method to hash a password
    def _hash_password(self, password):
        # Simple hashing using Python's built-in hash function
        return hash(password)

# Subclass of User representing a student
class Student(User):
    def __init__(self, username, password, student_id):
        super().__init__(username, password)
        self.student_id = student_id

# Subclass of User representing a teacher
class Teacher(User):
    def __init__(self, username, password, teacher_id):
        super().__init__(username, password)
        self.teacher_id = teacher_id

# Subclass of User representing an admin user
class Admin(User):
    pass

# Class representing attendance records
class Attendance:
    def __init__(self, username, date, status):
        self.username = username
        self.date = date
        self.status = status

# Session class for handling user sessions
class Session:
    def __init__(self, db):
        self.db = db

    # Method to register a new user
    def register_user(self, username, password, privilege):
        query = "INSERT INTO users (username, password, privilege) VALUES (%s, %s, %s)"
        hashed_password = self._hash_password(password)
        values = (username, hashed_password, privilege)
        self.db.execute_query(query, values)
        self.db.commit()

    # Method to authenticate a user
    def authenticate_user(self, username, password):
        query = "SELECT password FROM users WHERE username = %s"
        self.db.execute_query(query, (username,))
        result = self.db.fetch_all()
        if result:
            stored_password = result[0][0]
            return stored_password == self._hash_password(password)
        return False

    # Method to hash a password
    def _hash_password(self, password):
        # Simple hashing using Python's built-in hash function
        return hash(password)

# Subclass of Session for handling student sessions
class StudentSession:
    def __init__(self, db):
        self.db = db

    # Method to view attendance register for a student
    def view_register(self, username):
        query = "SELECT date, status FROM attendance WHERE username = %s"
        self.db.execute_query(query, (username,))
        records = self.db.fetch_all()
        for record in records:
            print(record)

# Subclass of Session for handling teacher sessions
class TeacherSession:
    def __init__(self, db):
        self.db = db

    # Method to handle teacher session
    def handle_teacher_session(self):
        while True:
            print("Teacher Menu")
            print("1. Mark student register")
            print("2. View register")
            print("3. Delete record")
            print("4. Logout")
            user_option = input("Option : ")
            if user_option == "1":
                self.mark_register()
            elif user_option == "2":
                self.view_register()
            elif user_option == "3":
                self.delete_record()
            elif user_option == "4":
                print("Logging out...")
                break
            else:
                print("Invalid option. Please select a valid option.")

    # Method to mark student attendance
    def mark_register(self):
        date = input("Date (DD/MM/YYYY): ")
        query = "SELECT username FROM users WHERE privilege = 'student'"
        self.db.execute_query(query)
        students = self.db.fetch_all()
        for student in students:
            student_username = student[0]
            status = input(f"Status for {student_username} (P/A/L): ")
            query = "INSERT INTO attendance (username, date, status) VALUES (%s, %s, %s)"
            self.db.execute_query(query, (student_username, date, status))
            self.db.commit()
        print("Register marked successfully.")

    # Method to view attendance register
    def view_register(self):
        date = input("Date (DD/MM/YYYY): ")
        query = "SELECT username, status FROM attendance WHERE date = %s"
        self.db.execute_query(query, (date,))
        register_records = self.db.fetch_all()
        if register_records:
            print("Student Register for", date)
            for record in register_records:
                username, status = record
                print(f"{username}: {status}")
        else:
            print("No register records found for", date)

    # Method to delete attendance record
    def delete_record(self):
        date = input("Date (DD/MM/YYYY): ")
        query = "SELECT username, status FROM attendance WHERE date = %s"
        self.db.execute_query(query, (date,))
        register_records = self.db.fetch_all()
        if register_records:
            print("Students with records for", date)
            for i, record in enumerate(register_records, 1):
                username, status = record
                print(f"{i}. {username}: {status}")
            selection = input("Select the number corresponding to the student you want to delete: ")
            try:
                selection_index = int(selection) - 1
                if 0 <= selection_index < len(register_records):
                    username, _ = register_records[selection_index]
                    delete_query = "DELETE FROM attendance WHERE username = %s AND date = %s"
                    self.db.execute_query(delete_query, (username, date))
                    self.db.commit()
                    print("Record for", username, "on", date, "has been deleted.")
                else:
                    print("Invalid selection.")
            except ValueError:
                print("Invalid input. Please enter a number.")
        else:
            print("No register records found for", date)

# Subclass of Session for handling admin sessions
class AdminSession(Session):
    def __init__(self, db):
        super().__init__(db)

    # Method to handle admin session
    def handle_admin_session(self):
        while True:
            print("Admin Menu")
            print("1. Register new Student")
            print("2. Register new Teacher")
            print("3. Delete Existing Student")
            print("4. Delete Existing Teacher")
            print("5. Logout")
            user_option = input("Option : ")
            if user_option == "1":
                username = input("Enter the username of the student: ")
                password = input("Enter the password for the student: ")
                self.register_student(username, password)
            elif user_option == "2":
                username = input("Enter the username of the teacher: ")
                password = input("Enter the password for the teacher: ")
                self.register_teacher(username, password)
            elif user_option == "3":
                username = input("Enter the username of the student you want to delete: ")
                self.delete_student(username)
            elif user_option == "4":
                username = input("Enter the username of the teacher you want to delete: ")
                self.delete_teacher(username)
            elif user_option == "5":
                print("Logging out...")
                break
            else:
                print("Invalid option. Please select a valid option.")

    # Method to register a new student
    def register_student(self, username, password):
        self.register_user(username, password, 'student')
        print(username + " has been registered as a student")

    # Method to register a new teacher
    def register_teacher(self, username, password):
        self.register_user(username, password, 'teacher')
        print(username + " has been registered as a teacher")

    # Method to delete a student
    def delete_student(self, username):
        query = "DELETE FROM users WHERE username = %s AND privilege = 'student'"
        self.db.execute_query(query, (username,))
        self.db.commit()
        if self.db.command_handler.rowcount < 1:
            print("User not found")
        else:
            print(username + " has been deleted")

    # Method to delete a teacher
    def delete_teacher(self, username):
        query = "DELETE FROM users WHERE username = %s AND privilege = 'teacher'"
        self.db.execute_query(query, (username,))
        self.db.commit()
        if self.db.command_handler.rowcount < 1:
            print("User not found")
        else:
            print(username + " has been deleted")

# Main function for starting the application
def main():
    db = Database()
    session = Session(db)
    while True:
        print("Welcome to the school system")
        print("1. Login as student")
        print("2. Login as teacher")
        print("3. Login as admin")
        print("4. Exit system")
        user_option = input("Option : ")
        if user_option == "1":
            username = input("Username : ")
            password = input("Password : ")
            if session.authenticate_user(username, password):
                student_session = StudentSession(db)
                student_session.view_register(username)
            else:
                print("Invalid login details")
        elif user_option == "2":
            username = input("Username : ")
            password = input("Password : ")
            if session.authenticate_user(username, password):
                teacher_session = TeacherSession(db)
            else:
                print("Invalid login details")
        elif user_option == "3":
            username = input("Username : ")
            password = input("Password : ")
            if username == DEFAULT_ADMIN_USERNAME and password == DEFAULT_ADMIN_PASSWORD:
                admin_session = AdminSession(db)
                admin_session.handle_admin_session()
            else:
                print("Invalid login details")
        elif user_option == "4":
            print("Exiting system...")
            break
        else:
            print("No valid option was selected")

if __name__ == "__main__":
    main()
