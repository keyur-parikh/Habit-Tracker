# This program here is a habit tracker that is going to keep track of your habits 

# I will first have to create a sqlite3 database that keep track of all of this. Maybe have a command line argument that asks for the username.
import csv
import sqlite3
import sys

conn = sqlite3.connect("habits.db")
cursor = conn.cursor()



def create_tables():
    """ Creates the tables if they dont exist in the databse"""
    cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL)")
    cursor.execute("CREATE TABLE IF NOT EXISTS users_habits (user_id INTEGER, day INTEGER NOT NULL, habit_id INTEGER NOT NULL, completed INTEGER NOT NULL, FOREIGN KEY(user_id) REFERENCES users(id), FOREIGN KEY(habit_id) REFERENCES habits(id))")
    cursor.execute("CREATE TABLE IF NOT EXISTS habits (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, habit TEXT NOT NULL UNIQUE, FOREIGN KEY(user_id) REFERENCES users(id))")

def get_username(username):
    """Returns the username by either pulling from the database or adding it.
    V1 is just basic functionality, no passwords implemented yet"""
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    check_user = cursor.fetchone()
    if check_user:
        return check_user[1]
    else:
        cursor.execute("INSERT INTO users(username) VALUES (?)", (username,))
        return username



def main():
    if __name__ == "__main__":
    # First, connect to the database

    # Check for command line arguments
        argc = sys.argv
        if len(argc) != 2:
            raise Exception("Usage habit.py 'username'")
        create_tables()
        username = get_username(argc[1])
        user_number = cursor.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
        user_number = user_number[0]
        # A While True loop: Ask the user for what they want to do. Options are add a new habit, update a new day of habits done, checks habit progress,  or q to quit
        while True:
            print(f"Welcome {username}, Your options are 'add' to add a new habit, 'update' to update your habits, 'check' to see your progress, or 'q' to quit")
            response = input("What would you like to do?: ")
            if response == 'q':
                break
        # If want to add a new habit. then we insert into sqlite3 habits table a new entry with their habit and habit id, where user_id is username, and then ask what is the habit they want to add.
        # Then, we insert the habits there, and ask the same question as above.
            elif response.lower() == "add":
                habit = input("What habit would you like to add: ")
                # If they write something for habit..
                if habit:
                    # ..we insert into the user_id, that habit and commit to the database
                    cursor.execute("INSERT INTO habits(user_id, habit) VALUES (?, ?)",(user_number, habit))
                    conn.commit()
                    print("Habit added")
                else:
                    # They must enter one, so if its empty this happens
                    print("Must enter a habit")
        # If they want to update their list of habits done. day variable becomes max day + 1. Then we loop through every habit that has their user_id in the habits table. Ask if they completed that or not. 
        # If they say yes, then we add a data entry to user_habits as 1 or 0 if the say no. 
            elif response.lower() == "update":
                # Fetch the max day they are on. and everytime the update, the program assumes that a day has passed
                day = cursor.execute("SELECT MAX(day) FROM users_habits WHERE user_id = (SELECT id FROM users WHERE username = ?)",(username,)).fetchone()
                if day[0] is not None:
                    day = day[0] + 1
                else:
                    day = 1
                # Fetch all the habits from their associated habits database
                habits = cursor.execute("SELECT * FROM habits WHERE user_id = (SELECT id FROM users WHERE username = ?)", (username,)).fetchall()
                # For each of the rows in habits, we first assign the indexes to the variables
                for row in habits:
                    habit = row[2]
                    habit_id = row[0]
                    user_id = row[1]
                    # Then for each we ask if they completed the habit or not
                    answer = input(f"Did you complete {habit}? (y or n)")
                    # If they did, then we insert 1
                    if answer.lower() == 'y':
                        cursor.execute("INSERT INTO users_habits(user_id, day, habit_id, completed) VALUES (?, ?, ?, 1)", (user_id, day, habit_id))
                        conn.commit()
                    # If they didnt, then we insert 0
                    elif answer.lower() == 'n':
                        cursor.execute("INSERT INTO users_habits(user_id, day, habit_id, completed) VALUES (?, ?, ?, 0)", (user_id, day, habit_id))
                        conn.commit()
                    else:
                        print("Please answer either y or n")
        # If they want to check their habit progress, we write all the data to a file, called habit progress - 'username'.
        # In this file, we create a CSV file titled , where the headers are Day, each one of their individual habits, Completed. With the values as.
        # We just select all data entries, and format it.
            elif response.lower() == "check":
                # Create a fieldnames dict with "Day" as the first value for now
                fieldnames = ["Day"]
                # Habits_dict to keep track of the id and the habit associated with the Id
                habit_dict = {}
                # Get all the things for habits table, just habit and habit id
                habits = cursor.execute("SELECT * FROM habits WHERE user_id = (SELECT id FROM users WHERE username = ?)",(username,)).fetchall()
                # Here, we do two things. First we append the habit name to the fieldnames so our headers can have the id, and associate the key value paur as well.
                for habit in habits:
                    habit_name = habit[2]
                    habit_id = habit[0]
                    fieldnames.append(habit_name)
                    habit_dict[habit_id] = habit_name
                # Now get us all the data from the user, this is where we updated whether they completed the habit or not
                rows = cursor.execute("SELECT * FROM users_habits WHERE user_id = (SELECT id FROM users WHERE username = ?)",(username,))
                # Create a day_tracker dictionary that tracks the habits done every day
                day_tracker = {}
                # Now iterate through what the query returned
                for row in rows:
                    day = row[1]
                    habit = habit_dict[row[2]]
                    completed = row[3]
                    # If the day is not in day_tracker dictionary, create an empty list as its value.
                    if day not in day_tracker:
                        day_tracker[day] = {}
                    # In that empty list, we store another dictionary with the habit as the key, and if they completed it or not as the value
                    day_tracker[day][habit] = completed
                # Open the file we want to write to 
                with open(f"Habits Progress {username}", "w") as f:
                    # Use the csv writer function and give the fieldnames list as the fieldnames
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    # Write the headers
                    writer.writeheader()
                    # For each day in the day_tracker dictionary we iterate
                    for day in day_tracker:
                        # Create another dictionary assocaited it with the fieldnames and the day
                        writer_dict = {}
                        writer_dict["Day"] = day
                        # And then for each key in the day, if they value is 1, then response is yes, if they didnt then resposne is no
                        for habit in day_tracker[day]:
                            if day_tracker[day][habit] == 1:
                                response = "Yes"
                            else:
                                response = "No"
                            # For the habit, we store the response
                            writer_dict[habit] = response
                        # Then we write out the response, associating it with their fieldnames
                        writer.writerow(writer_dict)
    # Close the connection with the database
    conn.close()
main()