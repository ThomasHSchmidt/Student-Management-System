"""
these will be all the functions that we need for main.py
"""

import sqlite3
import random
import mysql.connector
import mysql.connector.cursor
import subprocess
from email.message import EmailMessage
import ssl
import smtplib
from flask import flash



def connect_db():
    """connect to the mysql database"""
    db = mysql.connector.connect(
        host="apps23-londono.cgoehxa9ic3y.us-east-1.rds.amazonaws.com",
        user="admin",
        passwd="youarecooked12!",
        database="University",
        autocommit=True,
    )
    ##pointer to mysql database

    return db

def check_login_uid(
    email: str, password: str, db: mysql.connector.connection.MySQLConnection
) -> dict:
    """checks the login, then returns all data related to the user
    (UserID, Email, Username, Password, Role)"""

    cursor = db.cursor(dictionary=True)

    checklogin = "SELECT * FROM users WHERE email = %s AND password = %s"
    checkloginvalues = (email, password)

    cursor.execute(checklogin, checkloginvalues)

    print("EMAIL", email, "PASS", password)

    userdata = cursor.fetchone()
    if userdata is not None:
        cursor.close()
        return userdata

    return None

def check_login_userid(email: str, password: str, db: mysql.connector.connection.MySQLConnection
) -> dict:
    """checks the login, then returns all data related to the user
    (UserID, Email, Username, Password, Role)"""

    cursor = db.cursor(dictionary=True)

    checklogin = "SELECT * FROM pre_app WHERE email = %s AND password = %s"
    checkloginvalues = (email, password)

    cursor.execute(checklogin, checkloginvalues)

    userdata = cursor.fetchone()
    if userdata is not None:
        cursor.close()
        return userdata

    return None


def grab_role(userid, db: mysql.connector.connection.MySQLConnection) -> dict:
    """grabs the role related to the user"""

    cursor = db.cursor(dictionary=True)
    cursor.execute(f"SELECT role FROM pre_app WHERE userid = '{userid}'")
    role = cursor.fetchone()

    return role


def check_email(email: str, db: mysql.connector.connection.MySQLConnection) -> dict:
    """Validates the existence of an email in the database"""

    cursor = db.cursor(dictionary=True)

    cursor.execute(f"SELECT email FROM pre_app WHERE email = '{email}'")
    email = cursor.fetchone()

    return email


def add_user(
    email: str,
    firstname: str,
    lastname: str,
    password: str,
    roles:list,
    db: mysql.connector.connection.MySQLConnection
) -> bool:
    """Add a user to the USER table in the database"""

    cursor = db.cursor(dictionary=True)

    role_list = remove_none(roles)
    primary_role = role_list[-1] #Get the last role in the list (the highest permission role)

    print("MORE THAN ONE ", role_list)
    uid = generate_uid()

    #INSERT INTO users (uid, fname, lname, email, password, role, address) VALUES (55555555, 'Paul', 'McCartney', 'paul@gmail.com', 'pass', 'grad_student', 'OffCampus');
    adduser = (
        "INSERT INTO users (uid, fname, lname, email, password, role) VALUES (%s, %s, %s, %s, %s, %s)"
    )
    adduservalues = (uid, firstname, lastname, email, password, primary_role)

    cursor.execute(adduser, adduservalues)

    for role in role_list:
        cursor.execute(f"INSERT INTO role_assign (uid, role) VALUES ({uid}, '{role}')")

    return True


def get_userid(app_id:int, db: mysql.connector.connection.MySQLConnection) -> int:

    cursor = db.cursor(dictionary=True)

    cursor.execute(f"SELECT userid FROM application WHERE applicationid = {app_id}")
    id = cursor.fetchone()

    if not id:
        return None

    return id['userid']

def submit_app(userid: str, db: mysql.connector.connection.MySQLConnection) -> None:
    """Submits current application info"""

    cursor = db.cursor(dictionary=True)


    uid = generate_uid()
    # Change application status
    cursor.execute(
        f"UPDATE application \
        SET status = 'application complete and under review',\
        submission_date = CURRENT_TIMESTAMP, uid = '{uid}' \
        WHERE userid = '{userid}'"
    )

    app_id = get_app_id(connect_db(), userid)

    transcript_check = validate_transcript(app_id, connect_db())

    print("check:", transcript_check)

    if transcript_check:
        cursor.execute(
            f"INSERT INTO app_transcript (userid, transcriptstatus) VALUES ('{userid}', 'not received')"
        )

    #Send out recommendation letters
    emails = get_rec_emails(userid, connect_db())
    user_info = get_user_info_app(userid, connect_db())
    name = user_info['fname'] + " " + user_info['lname']

    for email in emails:
        try:
            send_email(name, email['rec_name'], email['rec_email'], email['letterid'])
            print("sent to", email['rec_email'])
        except Exception as e:
            print("Error emailing recipients", e)

    return

def app_exists(userid: str, db: mysql.connector.connection.MySQLConnection) -> dict:
    """Validates the existence of an application in the database for a specified
    userid"""

    cursor = db.cursor(dictionary=True)

    cursor.execute(
        f"SELECT COUNT(applicationid) AS count FROM application WHERE userid = '{userid}'"
    )

    result = cursor.fetchone()

    return result


def get_app_status(db: mysql.connector.connection.MySQLConnection, userid: str) -> str:
    """Fetches the status of an application given a userid"""
    cursor = db.cursor(dictionary=True)

    cursor.execute(f"SELECT status FROM application WHERE userid = {userid}")
    status = cursor.fetchone()

    return status["status"]


def get_app_id(db: mysql.connector.connection.MySQLConnection, userid: str) -> str:
    """Fetches the applicationid for a given userid"""

    cursor = db.cursor(dictionary=True)

    cursor.execute(f"SELECT applicationid FROM application WHERE userid = {userid}")
    app_id = cursor.fetchone()

    if not app_id:
        return None

    return app_id["applicationid"]

def clear_session(session) -> None:
    """Clears all session variables"""

    if "fname" in session:
        session.pop("fname")
    if "lname" in session:
        session.pop("lname")
    if "email" in session:
        session.pop("email")
    if "role" in session:
        session.pop("role")
    if "question_history" in session:
        session.pop("question_history")
    if "response_history" in session:
        session.pop("response_history")
    if "uid" in session:
        session.pop("uid")
    if "status" in session:
        session.pop("status")

    session.clear()

    return


def check_uid(id: int, db: mysql.connector.connection.MySQLConnection) -> bool:
    """Checks to see if a uid exists in the application table"""

    cursor = db.cursor(dictionary=True)

    cursor.execute(f"SELECT * FROM application WHERE uid = '{id}'")
    check = cursor.fetchall()

    # If an application entry contains the specified uid, then return true
    if len(check) > 0:
        return True

    return False


def generate_uid() -> int:
    """Generates a unique uid"""

    # The generated uid has not be checked against the application table
    notchecked = True

    while notchecked:

        # Generate an 8 digit number
        uid = random.randint(10000000, 99999999)
        # Check to see if the generated uid exists in the database If not,
        # then break out of the while loop and return the newly generated
        # uid
        if not check_uid(uid, connect_db()):
            notchecked = False

    return uid


def get_uid(userid, db):
    """Retrieves a user's UID given a userid"""
    cursor = db.cursor(dictionary=True)

    cursor.execute(f"SELECT uid FROM application WHERE userid = '{userid}'")

    uid = cursor.fetchone()

    return uid

def get_user_info_app(userid: str, db: mysql.connector.connection.MySQLConnection) -> dict:
    """Get User Info"""

    cursor = db.cursor(dictionary=True)

    cursor.execute(f"SELECT * FROM pre_app WHERE userid = '{userid}'")
    user_info = cursor.fetchone()

    return user_info

def get_user_info(uid: int, db: mysql.connector.connection.MySQLConnection) -> dict:
    """Get User Info"""

    cursor = db.cursor(dictionary=True)

    cursor.execute(f"SELECT * FROM users WHERE uid = {uid}")
    user_info = cursor.fetchone()

    return user_info

def get_studinfo(uid:int, db:mysql.connector.connection.MySQLConnection) -> dict:

    cursor = db.cursor(dictionary=True)

    cursor.execute(f"SELECT * FROM studInfo WHERE uid = {uid}")
    stud_info = cursor.fetchone()

    return stud_info


def get_users_app(db) -> dict:
    """Retrieves all user's and their corresponding information within the pre_app table"""

    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM pre_app")
    users = cursor.fetchall()

    return users

def get_users(db)-> dict:
    """Retrieves all user's and their corresponding information within the user table"""
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()

    return users

def delete_user(
    uid: str, role: str, db: mysql.connector.connection.MySQLConnection
) -> None:
    """Deletes a user from the database"""

    cursor = db.cursor()

    #'admin''grad_student','professor','advisor
    print("HERE3", role)
    if role in ["reviewer", "chair"]:
        # Delete user from the been_reviewed table
        cursor.execute(f" DELETE FROM been_reviewed WHERE reviewerid = '{uid}'")
        # Delete user from the reviewform table
        cursor.execute(f" DELETE FROM reviewform WHERE reviewerid = '{uid}'")
    else:
       
        
        # Delete user from the reviewform table
        cursor.execute(f" DELETE FROM form1 WHERE uid = '{uid}'")
        # Delete user from the recommendationletter table
        cursor.execute(f" DELETE FROM studInfo WHERE uid = '{uid}'")
        # Delete user from the transcript table
        cursor.execute(f" DELETE FROM advisingForm WHERE uid = '{uid}'")
        # Delete user from the transcript table
        cursor.execute(f" DELETE FROM transcripts WHERE uid = '{uid}'")
        # Delete user from the priordegrees table
        cursor.execute(f" DELETE FROM role_assign WHERE uid = '{uid}'")
        # Delete user from the application table
        cursor.execute(f" DELETE FROM users WHERE uid = '{uid}'")

    db.commit()

def change_user_role(
    userid: str, role: str, db: mysql.connector.connection.MySQLConnection
) -> str:
    """Changes the role of a user in the database"""

    cursor = db.cursor(dictionary=True)

    # Change user's role
    cursor.execute(f"UPDATE pre_app SET role = '{role}' WHERE userid = '{userid}'")

    db.commit()

    cursor.close()


def get_user_role_app(userid: str, db: mysql.connector.connection.MySQLConnection) -> str:
    """Retrieves the specified user's role given a userid"""

    cursor = db.cursor(dictionary=True)
    cursor.execute(f"SELECT role FROM pre_app WHERE userid = '{userid}'")
    role = cursor.fetchone()

    if role:
        return role["role"]

    return None

def get_user_role(uid: str, db: mysql.connector.connection.MySQLConnection) -> str:
    """Retrieves the specified user's role given a userid"""

    cursor = db.cursor(dictionary=True)
    cursor.execute(f"SELECT role FROM users WHERE uid = '{uid}'")
    role = cursor.fetchone()

    if role:
        return role["role"]

    return None


def update_session_variables(userid: str, session) -> None:
    """Updates all session variables using current data"""

    user_data = get_user_info_app(userid, connect_db())

    session["userid"] = user_data["userid"]
    session["fname"] = user_data["fname"]
    session["lname"] = user_data["lname"]
    session["email"] = user_data["email"]
    session["role"] = user_data["role"]

    return

def validate_transcript(
    app_id: str, db: mysql.connector.connection.MySQLConnection
) -> bool:
    """Checks to see if a transcript with the given application id exists in tshe database
    if True, then there are no transcript, if False, then transcripts exist"""

    cursor = db.cursor(dictionary=True)
    cursor.execute(f"SELECT * FROM app_transcript WHERE transcriptid = '{app_id}'")
    info = cursor.fetchall()

    if len(info) == 0:
        return True
    else:
        return False

def get_rec_letterids(userid:str, db: mysql.connector.connection.MySQLConnection) -> list:

    cursor = db.cursor(dictionary=True)
    cursor.execute(
        f"SELECT letterid FROM recommendationletter WHERE userid = '{userid}'"
    )
    letterids = cursor.fetchall()

    return letterids


def get_review_info(
    app_id: str, db: mysql.connector.connection.MySQLConnection
) -> dict:
    """Retreives all data associated with an application (application, transcript, recommendation, review form) as a dict"""

    cursor = db.cursor(dictionary=True)
    cursor.execute(
        f"SELECT * FROM application LEFT JOIN app_transcript ON application.applicationid = app_transcript.transcriptid LEFT JOIN recommendationletter ON application.applicationid = recommendationletter.letterid INNER JOIN reviewform ON application.applicationid = reviewform.reviewid WHERE application.applicationid = '{app_id}'"
    )
    info = cursor.fetchone()

    return info


def get_review_for_reviewer(app_id, reviewerid, db):
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        f"SELECT * FROM application LEFT JOIN app_transcript ON application.applicationid = app_transcript.transcriptid LEFT JOIN recommendationletter ON application.applicationid = recommendationletter.letterid INNER JOIN reviewform ON application.applicationid = reviewform.reviewid WHERE applicationid = '{app_id}' and reviewerid = '{reviewerid}'"
    )
    info = cursor.fetchone()

    return info


def get_reviewer_id(userid: str, db) -> str:

    cursor = db.cursor(dictionary=True)
    cursor.execute(f"SELECT reviewerid FROM reviewform WHERE userid = '{userid}'")
    result = cursor.fetchone()

    return result["reviewerid"]


def get_review_status(
    app_id: str, db: mysql.connector.connection.MySQLConnection
) -> str:
    """Retrievews the status of a particular review given a userid"""

    cursor = db.cursor(dictionary=True)
    cursor.execute(f"SELECT review_status FROM reviewform WHERE reviewid = '{app_id}'")
    status = cursor.fetchone()

    if not status or len(status) == 0:
        return "not reviewed"

    return status["review_status"]

def set_final_decision(
    decision: str, app_id: str, db: mysql.connector.connection.MySQLConnection
) -> None:
    """Sets the final decision for the given user's application"""

    cursor = db.cursor(dictionary=True)

    cursor.execute(
        f"UPDATE application SET decision = '{decision}', status = 'decision', decision_date = CURRENT_TIMESTAMP WHERE applicationid = '{app_id}'"
    )

    cursor.execute(
        f"UPDATE reviewform SET finaldecision = '{decision}' WHERE reviewid = '{app_id}'"
    )

    info = get_user_info_app(get_userid(app_id, connect_db()), connect_db())

    send_email_decision(info['fname'], info['email'])

    return

def get_decision(userid: str, db: mysql.connector.connection.MySQLConnection) -> str:
    """Retrieves the application decision for the given user's application"""

    cursor = db.cursor(dictionary=True)
    cursor.execute(f"SELECT decision FROM application WHERE userid = '{userid}'")
    decision = cursor.fetchone()

    return decision["decision"]

# true means that they haven't taken all the required prereqs 
def notDonePrereq(courseID, session):
    db = connect_db()
    cursor = db.cursor(dictionary=True)
    studentID = session['uid']
    
    # fetch the prerequisites for the class
    cursor.execute("SELECT prereq_ID FROM prerequisites WHERE crn = %s",(courseID,))
    prereqs = cursor.fetchall()
    
    # indicates that there's no prerequisites for this course 
    if prereqs is None:
        return False
    
    prereqlist = []
    for course in prereqs:
        crn = course['prereq_ID']
        prereqlist.append(crn)
    
    # fetch all past transcripts 
    cursor.execute("SELECT crn FROM transcripts WHERE uid = %s AND semester != %s", (studentID, "Fall 2024"))
    pastTranscript = cursor.fetchall()
    
    db.commit()
    db.close()
    count = 0
    for course in pastTranscript:
        for item in prereqlist:
            if course['crn'] == item:
                count+=1
                
     # they have completed all required 
    if count == len(prereqlist):
         return False
    # they havent completed all necessary prereqs 
    else:
        return True 
    # compare if the two prerequisites exist 
    # checks for Transcript

# checking for their currently registered courses 
## if true, this will cause an error 
def checkRegisteredDupe(uid, dictThing):
    db = connect_db()
    cursor = db.cursor(dictionary=True)
    # does this class exist in the currently registered transcripts 
    
    cursor.execute("SELECT * FROM transcripts WHERE uid = %s AND crn = %s and semester = %s", (uid, dictThing['crn'], "Fall 2024"))
    duplicate = cursor.fetchone()
    db.commit()
    db.close()

    
    # If the query returned a course, the student has taken it before thus there will be an error
    if duplicate is not None:
        return True
    else:
        return False

    
# function that checks if the user has already taken the class 
def hasTakenCourseBefore(courseID, studentID):
   # Checks if the student has already taken the specified course by querying the student's transcript.
   # #True if the student has taken the course before false if he hasent.
    db = connect_db()
    cursor = db.cursor(dictionary=True)


    cursor.execute("SELECT * FROM transcripts WHERE uid = %s AND crn = %s AND semester != %s", (studentID, courseID, "Fall 2024"))

    # get result
    course = cursor.fetchone()
    
    db.commit()
    db.close()
    # If the query returned a course, the student has taken it before thus there will be an error
    if course is not None:
        return True
    else:
        return False


# check if the person is at their limit of scheduling classes 
# third check before appending 
def checkCreditLimit(session):
    limit = 18
    current = 0
    studentID = session['uid']
    current = calculateTotal(studentID, session)
    # that they can keep adding 
    if current < limit:
        return False
    # they can't add more courses 
    return True

# check for time conflict with existing schedule
def parse_time(time_str):
    start_str, end_str = time_str.split('-')
    return int(start_str), int(end_str)

def is_time_overlap(start1, end1, start2, end2):
    return max(start1, start2) < min(end1, end2)

def previousTimeConflict(registered_courses, new_course, session):
    check_day = new_course['classDay']
    check_start, check_end = parse_time(new_course['classTime'])

    def check_conflict(courses):
        for course in courses:
            if course['classDay'] == check_day:
                start, end = parse_time(course['classTime'])
                if is_time_overlap(check_start, check_end, start, end):
                    return True
        return False

    # Check against already registered courses
    if check_conflict(registered_courses):
        return True

    # Check against mock schedule if it exists
    if 'mocksched' in session:
        if check_conflict(session['mocksched']):
            return True

    return False

# helper function to calculate the total credits they're taking 
# this function now needs to also calculate it with the courses they're already registered for 
def calculateTotal(uid, session):
    db = connect_db()
    cursor = db.cursor(dictionary=True)

    # this checks the amount of courses they're registered for the future semester 
    cursor.execute(" SELECT credits FROM transcripts JOIN courses ON transcripts.crn = courses.crn WHERE semester = %s AND uid = %s", ("Fall 2024", uid))
    currentCreds = cursor.fetchall()
    total = 0
    db.commit()
    db.close()
    
    # the already registered 
    for course in currentCreds:
        creds = int(course['credits'])
        total = total + creds
    
    if 'mocksched' in session:
        mockschedule = session['mocksched']
        for newcourse in mockschedule:
            creds = int(newcourse['credits'])
            total = total + creds
            
    return total

# GPA Calculator
def gpaCalc(uid, db):
    cursor = db.cursor(dictionary = True)
    # Fetch all grades of the student from the transcript_courses table
    cursor.execute("SELECT grade FROM transcripts WHERE uid = %s AND grade != 'IP'", (uid,))
    grades = cursor.fetchall()
    
    print("Grades:", grades)  # Debug print to check the fetched grades

    gpaCalc = {
        'A': 4.0,
        'A-': 3.66,
        'B+': 3.33,
        'B': 3.0,
        'B-': 2.66,
        'C+': 2.33,
        'C': 2.0,
        'C-': 1.66,
        'D+': 1.33,
        'D': 1.00,
        'D-': 0.66,
        'F': 0.00
    }
    points = 0
    gpa = 0
    
    # If grades exist
    if grades:
        # Iterate through them
        for grade in grades:
            # Change the letter grade into the point grade using the dict
            points += gpaCalc.get(grade['grade'].upper(), 0)
        # Divide the total by the amount of grades then round 2 decimal places
        gpa = points / len(grades)
        gpa = round(gpa, 2)
        return gpa
    else:
        return None