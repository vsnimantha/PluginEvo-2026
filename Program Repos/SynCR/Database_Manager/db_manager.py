import sqlite3

class DatabaseManager:
    def __init__(self, db_name):
        """Initialize and connect to the SQLite database."""
        self.db_name = db_name
        self.connection = sqlite3.connect(self.db_name)
        self.cursor = self.connection.cursor()

    def create_table(self):
        """Create the 'users' table if it doesn't already exist."""
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER
        )
        """)
        self.connection.commit()

    def insert_user(self, name, age):
        """Insert a new user into the 'users' table."""
        self.cursor.execute("INSERT INTO users (name, age) VALUES (?, ?)", (name, age))
        self.connection.commit()

    def get_all_users(self):
        """Retrieve all users from the 'users' table."""
        self.cursor.execute("SELECT * FROM users")
        return self.cursor.fetchall()

    def update_user(self, user_id, name, age):
        """Update a user's information by ID."""
        self.cursor.execute("""
        UPDATE users
        SET name = ?, age = ?
        WHERE id = ?
        """, (name, age, user_id))
        self.connection.commit()

    def delete_user(self, user_id):
        """Delete a user from the 'users' table by ID."""
        self.cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        self.connection.commit()

    def close_connection(self):
        """Close the database connection."""
        self.connection.close()


# Example usage of the class:
if __name__ == "__main__":
    db = DatabaseManager("Database_Manager/Database/program_data.db")
    db.create_table()
    
    # Add users
    db.insert_user("Alice", 25)
    db.insert_user("Bob", 30)

    # Fetch and display all users
    users = db.get_all_users()
    for user in users:
        print(user)

    # Update a user
    db.update_user(user_id=1, name="Alice", age=26)

    # Delete a user
    db.delete_user(user_id=2)

    # Close the connection
    db.close_connection()
