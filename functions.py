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

def add_preapp(email:str, lastname:str, firstname:str, password:str, db:mysql.connector.connection.MySQLConnection):
    print("JUST ONE")

    try:
        adduser = (
            "INSERT INTO pre_app (email, fname, lname, password, role) VALUES (%s, %s, %s, %s, %s)"
        )
        adduservalues = (email, lastname, firstname, password, 'user')
    except Exception as e:
        print("Error:",e)
        return False

    cursor = db.cursor(dictionary=True)
    cursor.execute(adduser, adduservalues)

    return True


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


def get_app_data(userid: str, db: mysql.connector.connection.MySQLConnection) -> dict:
    """Retrieves all application data for the specified user"""

    cursor = db.cursor(dictionary=True)

    cursor.execute(
        f"SELECT * FROM application WHERE application.userid = '{userid}'"
    )
    user_data = cursor.fetchone()

    # Send back the user data
    return user_data

def get_rec_data(userid: str, db: mysql.connector.connection.MySQLConnection) -> list:
    """Retrieves all recommendation letters and info for the specified user"""

    cursor = db.cursor(dictionary=True)

    cursor.execute(
        f"SELECT * FROM recommendationletter WHERE userid = '{userid}'"
    )
    rec_data = cursor.fetchall()

    if len(rec_data) == 0:
        return ['', '', '']

    return rec_data

def get_userid(app_id:int, db: mysql.connector.connection.MySQLConnection) -> int:

    cursor = db.cursor(dictionary=True)

    cursor.execute(f"SELECT userid FROM application WHERE applicationid = {app_id}")
    id = cursor.fetchone()

    if not id:
        return None

    return id['userid']


def get_app_data_appid(
    applicationid: str, db: mysql.connector.connection.MySQLConnection
) -> dict:
    """Retrieves all application data for the specified application"""
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        f"SELECT * FROM application WHERE application.applicationid = '{applicationid}'"
    )

    user_data = cursor.fetchone()
    print("aaron:", user_data)

    # Send back the user data
    return user_data


def get_degrees_appid(applicationid: str) -> tuple:
    """Generates a tuple containing information for the BS and MS in the
    following order (BS_Info, MS_Info)"""

    priordegreeinfo = get_prior_degree_info_appid(applicationid, connect_db())
    priordegreeinfoBS = []
    priordegreeinfoMS = []

    # Check the amount of priordegrees, and pass in all the values to the
    # respective variable (priordegreeinfoBS or priordegreeinfoMS ) i.e. If
    # there are 2 rows in priordegrees, it means they have 2 a BS and a MS
    if len(priordegreeinfo) == 2:
        priordegreeinfoBS = priordegreeinfo[0]
        priordegreeinfoMS = priordegreeinfo[1]
    elif len(priordegreeinfo) == 1:
        priordegreeinfoBS = priordegreeinfo[0]
    else:
        print("No Prior Degrees found")

    # return a tuple containing info for both degrees (BS_Info, MS_Info)
    return priordegreeinfoBS, priordegreeinfoMS


def get_prior_degree_info_appid(
    applicationid: str, db: mysql.connector.connection.MySQLConnection
) -> dict:
    """Fetches the prior_degree info for a given userid from the database"""

    cursor = db.cursor(dictionary=True)

    cursor.execute(
        f"SELECT * FROM priordegrees WHERE applicationid = '{applicationid}'"
    )
    info = cursor.fetchall()

    return info


def get_pending_review_apps(
    uid: str, db: mysql.connector.connection.MySQLConnection
) -> dict:
    """Retrieves all applications that are pending review"""
    cursor = db.cursor(dictionary=True)

    # cursor.execute(
    #     f"SELECT * FROM application WHERE applicationid NOT IN (SELECT reviewid FROM been_reviewed WHERE reviewerid = 2) ORDER BY timestamp ASC"
    # )

    cursor.execute(
        f"SELECT * FROM application LEFT JOIN pre_app ON application.userid = pre_app.userid INNER JOIN app_transcript ON application.applicationid = app_transcript.transcriptid WHERE applicationid NOT IN (SELECT reviewid FROM been_reviewed WHERE reviewerid = '{uid}') AND application.status = 'application complete and under review' AND role = 'applicant' AND transcriptstatus = 'received' ORDER BY submission_date ASC;"
    )
    apps = cursor.fetchall()

    return apps


def num_applications(db: mysql.connector.connection.MySQLConnection) -> str:
    """Checks for the current number of applications. Takes the cursor and
    returns (Number of Applications)"""
    cursor = db.cursor(dictionary=True)
    number = 0

    cursor.execute("SELECT COUNT(applicationid) FROM application")
    number = cursor.fetchone()

    return number[0]


def save_app(
    userid: str,
    firstname: str,
    lastname: str,
    address: str,
    ssn: str,
    phonenumber: str,
    priordegrees: dict,
    degreessought: str,
    areas_interest: str,
    greverbal: str,
    grequantitative: str,
    priorwork: str,
    greyearofexam: str,
    greadvancedscore: str,
    greadvancedsubject: str,
    semester: str,
    year: str,
    rec_data:list
) -> None:
    """Saves all current progress from the application form into the application
    table"""

    db = connect_db()
    cursor = db.cursor(dictionary=True)

    # if the prior degree is not specified, then continue with num_degrees = 0
    if priordegrees is not None:
        num_degrees = len(priordegrees.keys())
    else:
        num_degrees = 0

    # 2 degrees implies MS is the highest
    if num_degrees == 2:
        priordegree = "MS"
    # 1 degree implies BS is the highest
    elif num_degrees == 1:
        priordegree = "BS"
    else:
        priordegree = None

    validate = app_exists(userid, connect_db())["count"]

    # if there are no application entries for the specified user
    if validate == 0:
        """
          ___                  __   _              __    _                    ____         ___    
         / _ |   ___    ___   / /  (_) ____ ___ _ / /_  (_) ___   ___        /  _/  ___   / _/ ___
        / __ |  / _ \  / _ \ / /  / / / __// _ `// __/ / / / _ \ / _ \      _/ /   / _ \ / _/ / _ 
       /_/ |_| / .__/ / .__//_/  /_/  \__/ \_,_/ \__/ /_/  \___//_//_/     /___/  /_//_//_/   \___/
              /_/    /_/                                                                          
        """

        saveinsertapp = """
        INSERT INTO application
        (userid, status, decision, submission_date, firstname, lastname,
        address, ssn, phonenumber, degreessought, areas_interest, priordegrees,
        greverbal, grequantitative, greyearofexam, greadvancedscore, greadvancedsubject,
        priorwork, semester, year)
        VALUES
        (%s, %s, %s, CURRENT_TIMESTAMP, %s, %s,
        %s, %s, %s, %s, %s, %s,
        %s, %s, %s, %s, %s,
        %s, %s, %s)
    """

        saveinsertappvalues = (
            userid,
            "application incomplete",
            "undecided",
            firstname,
            lastname,
            address,
            ssn,
            phonenumber,
            degreessought,
            areas_interest,
            priordegree,
            greverbal,
            grequantitative,
            greyearofexam,
            greadvancedscore,
            greadvancedsubject,
            priorwork,
            semester,
            year,
        )

        cursor.execute(saveinsertapp, saveinsertappvalues)

        """
           ___          _                    ___                                     ____         ___    
          / _ \  ____  (_) ___   ____       / _ \ ___   ___ _  ____ ___  ___        /  _/  ___   / _/ ___
         / ___/ / __/ / / / _ \ / __/      / // // -_) / _ `/ / __// -_)/ -_)      _/ /   / _ \ / _/ / _ \
        /_/    /_/   /_/  \___//_/        /____/ \__/  \_, / /_/   \__/ \__/      /___/  /_//_//_/   \___/
                                                      /___/                                              
        """

        app_id = get_app_id(connect_db(), userid)

        # loop through prior degrees and add each one to prior degrees table
        for i in range(num_degrees):
            degree_type = list(priordegrees.keys())[i]
            degree_dict = priordegrees[degree_type]
            cursor.execute(
                f"INSERT into priordegrees \
                (applicationid, userid, degree_type, year, \
                gpa, school, major) \
                VALUES ('{app_id}', '{userid}', '{degree_type}', '{degree_dict['year']}', \
                '{degree_dict['gpa']}', '{degree_dict['university']}', '{degree_dict['major']}')"
            )

        """
           ___                                              __        __    _                    __        __   __            
          / _ \ ___  ____ ___   __ _   __ _  ___   ___  ___/ / ___ _ / /_  (_) ___   ___        / /  ___  / /_ / /_ ___   ____
         / , _// -_)/ __// _ \ /  ' \ /  ' \/ -_) / _ \/ _  / / _ `// __/ / / / _ \ / _ \      / /__/ -_)/ __// __// -_) / __/
        /_/|_| \__/ \__/ \___//_/_/_//_/_/_/\__/ /_//_/\_,_/  \_,_/ \__/ /_/  \___//_//_/     /____/\__/ \__/ \__/ \__/ /_/  
                                                                                                                     
        """
        # letter_ids = get_rec_letterids(userid, connect_db())
        # print("LETTERIDS",letter_ids)

        print("recdata in app", len(rec_data))
        print("USERID:", userid)


        for rec in rec_data:
            print("HERE2")
            if all([rec['rec_name'], rec['rec_email']]):
                cursor.execute(
                    f"INSERT INTO recommendationletter (userid, rec_name, rec_email, status) VALUES ('{userid}', '{rec['rec_name']}', '{rec['rec_email']}', 'not received')"
                )

    else:

        """
          ___                  __   _              __    _                    ____         ___    
         / _ |   ___    ___   / /  (_) ____ ___ _ / /_  (_) ___   ___        /  _/  ___   / _/ ___
        / __ |  / _ \  / _ \ / /  / / / __// _ `// __/ / / / _ \ / _ \      _/ /   / _ \ / _/ / _ \
       /_/ |_| / .__/ / .__//_/  /_/  \__/ \_,_/ \__/ /_/  \___//_//_/     /___/  /_//_//_/   \___/
              /_/    /_/                                                                          
        """

        saveupdateapp = """
        UPDATE application
        SET firstname = %s, lastname = %s, address = %s,
        ssn = %s, phonenumber = %s, degreessought = %s,
        areas_interest = %s, priordegrees = %s,
        greverbal = %s, grequantitative = %s,
        priorwork = %s, semester = %s, year = %s,
        greyearofexam = %s, greadvancedscore = %s,
        greadvancedsubject = %s
        WHERE userid = %s
    """

        saveupdateappvalues = (
            firstname,
            lastname,
            address,
            ssn,
            phonenumber,
            degreessought,
            areas_interest,
            priordegree,
            greverbal,
            grequantitative,
            priorwork,
            semester,
            year,
            greyearofexam,
            greadvancedscore,
            greadvancedsubject,
            userid,
        )

        cursor.execute(saveupdateapp, saveupdateappvalues)

        # Delete previous entries
        cursor.execute(f"DELETE FROM priordegrees WHERE userid = '{userid}'")
        # Prior degree info insertion
        app_id = get_app_id(connect_db(), userid)

        """
           ___          _                    ___                                     ____         ___    
          / _ \  ____  (_) ___   ____       / _ \ ___   ___ _  ____ ___  ___        /  _/  ___   / _/ ___
         / ___/ / __/ / / / _ \ / __/      / // // -_) / _ `/ / __// -_)/ -_)      _/ /   / _ \ / _/ / _ \
        /_/    /_/   /_/  \___//_/        /____/ \__/  \_, / /_/   \__/ \__/      /___/  /_//_//_/   \___/
                                                      /___/                                              
        """

        # loop through prior degrees and add each one to prior degrees table
        for i in range(num_degrees):
            degree_type = list(priordegrees.keys())[i]
            degree_dict = priordegrees[degree_type]

            savepd = """
    INSERT INTO priordegrees
    (applicationid, userid, degree_type, year, gpa, school, major)
    VALUES
    (%(app_id)s, %(userid)s, %(degree_type)s, %(year)s, %(gpa)s, %(school)s, %(major)s)
"""

            savepdvalues = {
                "app_id": app_id,
                "userid": userid,
                "degree_type": degree_type,
                "year": degree_dict["year"],
                "gpa": degree_dict["gpa"],
                "school": degree_dict["university"],
                "major": degree_dict["major"],
            }

            cursor.execute(savepd, savepdvalues)

        """
           ___                                              __        __    _                    __        __   __            
          / _ \ ___  ____ ___   __ _   __ _  ___   ___  ___/ / ___ _ / /_  (_) ___   ___        / /  ___  / /_ / /_ ___   ____
         / , _// -_)/ __// _ \ /  ' \ /  ' \/ -_) / _ \/ _  / / _ `// __/ / / / _ \ / _ \      / /__/ -_)/ __// __// -_) / __/
        /_/|_| \__/ \__/ \___//_/_/_//_/_/_/\__/ /_//_/\_,_/  \_,_/ \__/ /_/  \___//_//_/     /____/\__/ \__/ \__/ \__/ /_/  
                                                                                                                     
        """

        letter_ids = get_rec_letterids(userid, connect_db())
        print("LETTERIDS",letter_ids)

        num_of_rec = len(get_rec_data(userid, connect_db()))

        if len(rec_data) > num_of_rec:
            cursor.execute(f"DELETE FROM recommendationletter WHERE userid = {userid}")
            for rec in rec_data:
                if all([rec['rec_name'], rec['rec_email']]):
                    cursor.execute(
                        f"INSERT INTO recommendationletter (userid, rec_name, rec_email, status) VALUES ('{userid}', '{rec['rec_name']}', '{rec['rec_email']}', 'not received')"
                    )


        for rec, id in zip(rec_data, letter_ids):
            if all([rec['rec_name'], rec['rec_email']]):
                cursor.execute(
                    f"UPDATE recommendationletter SET rec_name = '{rec['rec_name']}', rec_email = '{rec['rec_email']}' WHERE letterid = '{id['letterid']}'"
                )

    change_user_role(userid, "applicant", connect_db())

    cursor.close()

    return


def submit_app(userid: str, db: mysql.connector.connection.MySQLConnection) -> None:
    """Submits current application info (Work in Progress)"""

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


def submit_review(
    userid,
    reviewerid,
    rec_ratings,
    gas_decision,
    missing_course,
    reasons_reject,
    reviewer_comment,
    recommended_advisor,
    final_decision,
    db,
):

    cursor = db.cursor(dictionary=True)

    reviewid = get_app_id(connect_db(), userid)

    print("REVIEWID:", reviewid)
    print("USERID", userid)

    if not final_decision:
        final_decision = "undecided"
    else:
        cursor.execute(
            f"UPDATE application SET status = 'decision', decision = '{final_decision}' WHERE userid = '{userid}'"
        )

    cursor.execute(
        f"INSERT into reviewform (reviewid, userid, reviewerid, gas_decision, missing_course, reasons_reject, reviewer_comment, recommended_advisor, review_status, finaldecision, timestamp) VALUES ('{reviewid}', '{userid}', '{reviewerid}', '{gas_decision}', '{missing_course}', '{reasons_reject}', '{reviewer_comment}', '{recommended_advisor}', 'reviewed', '{final_decision}', CURRENT_TIMESTAMP)"
    )

    for rec in rec_ratings:
        print("userid", userid)
        print("recid", rec['id'])
        cursor.execute(f"UPDATE recommendationletter SET rating = '{rec['rating']}', generic = '{rec['generic']}', credible = '{rec['credible']}' WHERE letterid = {rec['id']} AND userid = {userid}")

    cursor.execute(
        f"INSERT into been_reviewed (reviewerid, reviewid) VALUES ('{reviewerid}', '{reviewid}')"
    )

    return


def degree_info(num_degree: int, form):
    """Generates a dictionary of information for a specfied users prior degree
    info"""

    if num_degree == 1:
        result = {
            "BS": {
                "year": form.get("yearreceived_bs"),
                "major": form.get("major_bs"),
                "gpa": form.get("gpa_bs"),
                "university": form.get("university_bs"),
            }
        }
    else:
        result = {
            "BS": {
                "year": form.get("yearreceived_bs"),
                "gpa": form.get("gpa_bs"),
                "university": form.get("university_bs"),
                "major": form.get("major_bs"),
            },
            "MS": {
                "year": form.get("yearreceived_ms"),
                "gpa": form.get("gpa_ms"),
                "university": form.get("university_ms"),
                "major": form.get("major_ms"),
            },
        }

    return result


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


def get_prior_degree_info(
    userid: str, db: mysql.connector.connection.MySQLConnection
) -> dict:
    """Fetches the prior_degree info for a given userid from the database"""

    cursor = db.cursor(dictionary=True)

    cursor.execute(f"SELECT * FROM priordegrees WHERE userid = '{userid}'")
    info = cursor.fetchall()

    return info


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


def get_degrees(userid: str) -> tuple:
    """Generates a tuple containing information for the BS and MS in the
    following order (BS_Info, MS_Info)"""

    priordegreeinfo = get_prior_degree_info(userid, connect_db())
    priordegreeinfoBS = []
    priordegreeinfoMS = []

    # Check the amount of priordegrees, and pass in all the values to the
    # respective variable (priordegreeinfoBS or priordegreeinfoMS ) i.e. If
    # there are 2 rows in priordegrees, it means they have 2 a BS and a MS
    if len(priordegreeinfo) == 2:
        priordegreeinfoBS = priordegreeinfo[0]
        priordegreeinfoMS = priordegreeinfo[1]
    elif len(priordegreeinfo) == 1:
        priordegreeinfoBS = priordegreeinfo[0]
    else:
        print("No Prior Degrees found")

    # return a tuple containing info for both degrees (BS_Info, MS_Info)
    return priordegreeinfoBS, priordegreeinfoMS


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


def delete_user_pre(
    userid: str, role: str, db: mysql.connector.connection.MySQLConnection
) -> None:
    """Deletes a user from the database"""

    cursor = db.cursor()

    if role in ["reviewer", "chair"]:
        # Delete user from the been_reviewed table
        cursor.execute(f" DELETE FROM been_reviewed WHERE reviewerid = '{userid}'")
        # Delete user from the reviewform table
        cursor.execute(f" DELETE FROM reviewform WHERE reviewerid = '{userid}'")
    else:
        # app_id = reviewid, need review id to remove from been_reviewed
        review_id = get_app_id(connect_db(), userid)

        # Delete user from the been_reviewed table
        cursor.execute(f" DELETE FROM been_reviewed WHERE reviewid = '{review_id}'")
        # Delete user from the reviewform table
        cursor.execute(f" DELETE FROM reviewform WHERE userid = '{userid}'")
        # Delete user from the recommendationletter table
        cursor.execute(f" DELETE FROM recommendationletter WHERE userid = '{userid}'")
        # Delete user from the transcript table
        cursor.execute(f" DELETE FROM app_transcript WHERE userid = '{userid}'")
        # Delete user from the priordegrees table
        cursor.execute(f" DELETE FROM priordegrees WHERE userid = '{userid}'")
        # Delete user from the application table
        cursor.execute(f" DELETE FROM application WHERE userid = '{userid}'")

    # Delete user from the user table
    cursor.execute(f"DELETE FROM pre_app WHERE userid = '{userid}'")

    db.commit()

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


def get_rec_info(letterid:int, db: mysql.connector.connection.MySQLConnection) -> dict:
    """Retrieves all information from the recommendationletter table given a userid and letterid"""

    cursor = db.cursor(dictionary=True)

    cursor.execute(f"SELECT * FROM recommendationletter WHERE letterid = {letterid}")
    info = cursor.fetchone()

    return info


def validate_review(
    app_id: str, db: mysql.connector.connection.MySQLConnection
) -> bool:
    """Checks to see if a review with the given application id exists in the database
    True means no reviews, False means there exists reviews"""

    cursor = db.cursor(dictionary=True)
    cursor.execute(f"SELECT * FROM reviewform WHERE reviewid = '{app_id}'")
    info = cursor.fetchall()

    if len(info) == 0:
        return True
    else:
        return False


def validate_review_reviewer(reviewid, reviewerid, db) -> bool:
    """Checks to see if a review with the given application id and reviewer id exists in the database
    True means yes reviews, False means no reviews"""

    cursor = db.cursor(dictionary=True)
    cursor.execute(
        f"SELECT reviewid, reviewerid FROM reviewform WHERE reviewid = '{reviewid}' AND reviewerid = '{reviewerid}'"
    )
    result = cursor.fetchall()

    if len(result) > 0:
        return True
    else:
        return False


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


def get_all_reviewed_info(db: mysql.connector.connection.MySQLConnection) -> dict:
    """Returns the info for all reviewed applications"""

    cursor = db.cursor(dictionary=True)
    cursor.execute(
        f"SELECT * FROM application JOIN app_transcript ON application.userid = app_transcript.userid JOIN reviewform ON application.applicationid = reviewform.reviewid WHERE review_status = 'reviewed'"
    )
    info = cursor.fetchall()

    return info


def get_pending_review_form(db: mysql.connector.connection.MySQLConnection) -> dict:
    """This returns the review form info for undecided applications"""

    cursor = db.cursor(dictionary=True)
    cursor.execute(
        f"SELECT application.applicationid, COUNT(reviewerid) AS count,\
        application.userid, application.firstname, \
        application.lastname, reviewform.review_status, \
        reviewform.reviewerid FROM reviewform INNER \
        JOIN application ON finaldecision = decision \
        and reviewid = applicationid LEFT JOIN app_transcript \
        ON app_transcript.transcriptid = applicationid LEFT JOIN \
        recommendationletter ON applicationid = letterid WHERE finaldecision = \
        'undecided' AND review_status = 'reviewed' AND transcriptstatus = 'received' \
        AND recommendationletter.status = 'received' GROUP BY reviewform.userid"
    )
    info = cursor.fetchall()

    return info


def set_transcript_status(
    status: str, userid: str, db: mysql.connector.connection.MySQLConnection
) -> None:
    """Sets the app_transcript status for the given users application"""

    cursor = db.cursor(dictionary=True)
    cursor.execute(
        f"UPDATE app_transcript SET transcriptstatus = '{status}' WHERE userid = '{userid}'"
    )

    return


def get_transcript_status(
    userid: str, db: mysql.connector.connection.MySQLConnection
) -> str:
    """Retreives the app_transcript status for the given user's application"""

    cursor = db.cursor(dictionary=True)
    cursor.execute(f"SELECT transcriptstatus FROM app_transcript WHERE userid = '{userid}'")
    status = cursor.fetchone()

    if not status:
        return "not received"

    return status["transcriptstatus"]


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


def get_transcript_info(db: mysql.connector.connection.MySQLConnection) -> list:
    """Get all transcript data that is not received, needs to be updated before reviewform can be submitted"""

    cursor = db.cursor(dictionary=True)
    cursor.execute(
        f"SELECT application.userid, firstname, lastname, transcriptstatus FROM application JOIN app_transcript ON application.userid = app_transcript.userid WHERE transcriptstatus = 'not received'"
    )
    info = cursor.fetchall()

    return info


def delete_reviewform(
    reviewerid: str, reviewid: str, db: mysql.connector.connection.MySQLConnection
) -> None:
    """Deletes the reviewform corresponding to the given reviewerid and reviewid"""

    cursor = db.cursor(dictionary=True)
    cursor.execute(
        f"DELETE FROM been_reviewed WHERE (reviewerid = '{reviewerid}') AND (reviewid = '{reviewid}')"
    )
    cursor.execute(
        f"DELETE FROM reviewform WHERE (reviewerid = '{reviewerid}') AND (reviewid = '{reviewid}')"
    )

    return


def get_decision(userid: str, db: mysql.connector.connection.MySQLConnection) -> str:
    """Retrieves the application decision for the given user's application"""

    cursor = db.cursor(dictionary=True)
    cursor.execute(f"SELECT decision FROM application WHERE userid = '{userid}'")
    decision = cursor.fetchone()

    return decision["decision"]


def get_rec_status(userid: str, db: mysql.connector.connection.MySQLConnection) -> str:
    """Retrieves the recommendation letter status for the given user's application"""

    cursor = db.cursor(dictionary=True)
    cursor.execute(f"SELECT status FROM recommendationletter WHERE userid = '{userid}'")
    status = cursor.fetchone()

    return status["status"]


def get_history(db: mysql.connector.connection.MySQLConnection) -> dict:
    """Retrieves all the decided applications"""

    cursor = db.cursor(dictionary=True)
    cursor.execute(f"SELECT * from application WHERE status = 'decision'")
    history = cursor.fetchall()

    return history

def has_perm(uid:int, perm: str, db: mysql.connector.connection.MySQLConnection) -> bool:

    cursor = db.cursor(dictionary=True)
    cursor.execute(f"SELECT perm FROM user JOIN role ON user.uid = role.uid WHERE uid = {uid} AND perm = '{perm}'")
    check = cursor.fetchall()

    for perm in check:
        if perm['perm'] == perm:
            return True

    return False

#ADDING NEW FUNCTIONS

def search_roster(query:str, session, crn = None, type = None):
    db = connect_db()
    cursor = db.cursor(dictionary=True)

    search_roster = []

    if session['role'] == 'gs' or session['role'] == 'admin' or session['role'] == 'registrar':
        if query:
            cursor.execute("SELECT uid, fname, lname FROM users WHERE role = 'grad_student' AND (fname LIKE %s OR lname LIKE %s OR uid LIKE %s) ORDER BY lname",
                    ('%' + query + '%', '%' + query + '%', '%' + query + '%'))
            search_roster = cursor.fetchall()
        else:
            cursor.execute("SELECT uid, fname, lname FROM users WHERE role = 'grad_student' ORDER BY lname")
            search_roster = cursor.fetchall()
    
    if session['role'] == 'admin':
        if type == 'student':
            if query:
                cursor.execute("SELECT uid, fname, lname FROM users WHERE role = 'grad_student' AND (fname LIKE %s OR lname LIKE %s OR uid LIKE %s) ORDER BY lname",
                        ('%' + query + '%', '%' + query + '%', '%' + query + '%'))
                search_roster = cursor.fetchall()
            else:
                cursor.execute("SELECT uid, fname, lname FROM users WHERE role = 'grad_student' ORDER BY lname")
                search_roster = cursor.fetchall()
        if type == 'professor':
            if query:
                cursor.execute("SELECT uid, fname, lname FROM users WHERE role = 'professor' AND (fname LIKE %s OR lname LIKE %s OR uid LIKE %s) ORDER BY lname",
                        ('%' + query + '%', '%' + query + '%', '%' + query + '%'))
                search_roster = cursor.fetchall()
            else:
                cursor.execute("SELECT uid, fname, lname FROM users WHERE role = 'professor' ORDER BY lname")
                search_roster = cursor.fetchall()
        if type == 'secretary':
            if query:
                cursor.execute("SELECT uid, fname, lname FROM users WHERE role = 'secretary' AND (fname LIKE %s OR lname LIKE %s OR uid LIKE %s) ORDER BY lname",
                        ('%' + query + '%', '%' + query + '%', '%' + query + '%'))
                search_roster = cursor.fetchall()
            else:
                cursor.execute("SELECT uid, fname, lname FROM users WHERE role = 'secretary' ORDER BY lname")
                search_roster = cursor.fetchall()
        if type == 'course':
            if query:
                cursor.execute("SELECT crn, dept, cid, title, credits FROM courses WHERE (dept LIKE %s OR title LIKE %s OR cid LIKE %s) ORDER BY crn",
                        ('%' + query + '%', '%' + query + '%', '%' + query + '%'))
                search_roster = cursor.fetchall()
            else:
                cursor.execute("SELECT crn, dept, cid, title, credits FROM courses ORDER BY crn")
                search_roster = cursor.fetchall()

    if session['role'] == 'professor':
        if query:
            cursor.execute("SELECT users.uid as uid, users.fname, users.lname, transcripts.grade, grade_edited FROM transcripts JOIN users ON transcripts.uid = users.uid WHERE transcripts.crn = %s AND (users.fname LIKE %s OR users.lname LIKE %s) ORDER BY users.lname",
                        (crn, '%' + query + '%', '%' + query + '%'))
            search_roster = cursor.fetchall()
        else:
            cursor.execute("SELECT users.uid as uid, users.fname, users.lname, transcripts.grade FROM transcripts JOIN users ON transcripts.uid = users.uid WHERE transcripts.crn = %s ORDER BY users.lname",
                       (crn,))
            search_roster = cursor.fetchall()
    #search_roster = cursor.fetchall()
    print(search_roster)
    
    db.commit()
    db.close()
    return search_roster

def email_exists(email):
    db = connect_db()
    cursor = db.cursor(dictionary=True)
    
    # query to check if email exists (if exists count = 1)
    #cursor.execute("SELECT COUNT (*) FROM Users WHERE email = %s", (email,))
    cursor.execute("SELECT COUNT(*) AS count FROM users WHERE email = %s", (email,))
    #cursor.execute("SELECT COUNT(*) FROM Users WHERE email = %s", (email,))

    result = cursor.fetchone()
    count = result['count'] if result and 'count' in result else 0
    
    db.commit()
    db.close()
    
    return count > 0

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

#second check before appending 
def checkDuplicate(mocksched, dictThing):
    for course in mocksched:
        if (course['crn'] == dictThing['crn']):
            return False
    return True

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

def checkRegisteredVsMockConflict(registered_courses, session):
    if 'mocksched' not in session:
        return False  # No mock schedule to compare to

    for reg_course in registered_courses:
        reg_day = reg_course['class_day']
        reg_start, reg_end = parse_time(reg_course['class_time'])
        for mock_course in session['mocksched']:
            if mock_course['classDay'] == reg_day:
                mock_start, mock_end = parse_time(mock_course['classTime'])
                if is_time_overlap(reg_start, reg_end, mock_start, mock_end):
                    return True  # Conflict found
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

#gpa calculator
def grade_to_points(grade):
    grade_points = {
        'A': 4.0,
        'A-': 3.7,
        'B+': 3.3,
        'B': 3.0,
        'B-': 2.7,
        'C+': 2.3,
        'C': 2.0,
        'F': 0.0
    }
    return grade_points.get(grade)

def calculate_gpa(transcripts):
    total_points = 0
    total_credits = 0
    for transcript in transcripts:
        grade = transcript['grade']
        credit = transcript['credits']
        if grade == 'IP':
            continue
        
        points = grade_to_points(grade) * credit
        total_points += points
        total_credits += credit
    if total_credits == 0:
        return 0.0

    return total_points / total_credits
    
#gpa calculator
def grade_to_points(grade):
    grade_points = {
        'A': 4.0,
        'A-': 3.7,
        'B+': 3.3,
        'B': 3.0,
        'B-': 2.7,
        'C+': 2.3,
        'C': 2.0,
        'F': 0.0
    }
    return grade_points.get(grade)

def calculate_gpa(transcripts):
    total_points = 0
    total_credits = 0
    for transcript in transcripts:
        grade = transcript['grade']
        credit = transcript['credits']
        if grade == 'IP':
            continue
        
        points = grade_to_points(grade) * credit
        total_points += points
        total_credits += credit
    if total_credits == 0:
        return 0.0

    return total_points / total_credits
    
def matriculate_student(userid, db):

    uid = get_uid(userid, db)['uid']
    cursor = db.cursor(dictionary=True)
    user_info = get_user_info_app(userid, db)
    app_info = get_app_data(userid, db)

    # studinfo, and role need to be updated when a student is moved from pre_app to users (users -> role, transcript, studinfo)

    #users
    cursor.execute(f"INSERT INTO users (uid, fname, lname, email, password, role, address) VALUES ({uid}, '{app_info['firstname']}', '{app_info['lastname']}', '{user_info['email']}', '{user_info['password']}', 'grad_student', '{app_info['address']}')")

    #role
    # cursor.execute(f"INSERT INTO role")

    fid = choose_advisor(userid, connect_db())

    if app_info['degreessought'] == 'MS':
        degree_sought = 'Masters'
    else:
        degree_sought = 'Doctorate'

    #studinfo
    # assign advisor when transferring from apps to ads
    cursor.execute(f"INSERT INTO studInfo (uid, program, gpa, grad_status, fid) VALUES ({uid}, '{degree_sought}', 0.0, 'Graduate', {fid})")

    #Remove them from pre_app
    # cursor.execute(f"DELETE FROM pre_app WHERE userid = {userid}")

    #set matriculated to 1
    cursor.execute(f"UPDATE application SET matriculated = 1 WHERE userid = {userid}")

    print("Student matricualted!")
    return

def add_role_user(uid:int, role:str, db:mysql.connector.connection.MySQLConnection) -> None:

    cursor = db.cursor(dictionary=True)

    cursor.execute(f"INSERT INTO role (uid, role) VALUES ({uid}, '{role}')")

    return

def remove_none(list:list) -> list:

    result = []

    for x in list:
        if x:
            result.append(x)
    
    return result

def valid_uid(uid:int, db:mysql.connector.connection.MySQLConnection) -> bool:

    cursor = db.cursor(dictionary=True)
    cursor.execute(f"SELECT uid FROM users WHERE uid = {uid}")
    uid = cursor.fetchone()
    
    if uid:
        print("CHECK:", uid)
        return True
    
    return False

def reset_database() -> None:
    """Clears all info in all tables, and inserts default accounts/dummy data"""

    command = "mysql -h apps23-londono.cgoehxa9ic3y.us-east-1.rds.amazonaws.com -P 3306 -u admin -p'youarecooked12!' --default-character-set=utf8 --ssl-mode=DISABLED University <'create.sql'"
    subprocess.run(command, shell=True)
    print("Database Reset")

    return

def get_user_courses(uid:int, db:mysql.connector.connection.MySQLConnection) -> list:
    """ Gets course info using the uid associated with a form1 """

    cursor = db.cursor(dictionary=True)
    # get all courses added by the logged in user
    cursor.execute(f"SELECT * FROM courses INNER JOIN form1 ON courses.crn = form1.crn WHERE form1.uid = {uid}")
    f1_courses = cursor.fetchall()

    return f1_courses

def get_course_info(crn:int, db:mysql.connector.connection.MySQLConnection) -> dict:

    cursor = db.cursor(dictionary=True)
    cursor.execute(f"SELECT * FROM courses WHERE crn = {crn}")
    course_info = cursor.fetchone()

    return course_info

def update_student_decision(decision:str, userid:int, db:mysql.connector.connection.MySQLConnection) -> None:


    cursor = db.cursor(dictionary = True)
    cursor.execute(f"UPDATE application SET student_decision = '{decision}' WHERE userid = {userid}")

    return

def get_student_decision(userid:int, db:mysql.connector.connection.MySQLConnection):

    cursor = db.cursor(dictionary=True)
    cursor.execute(f"SELECT student_decision FROM application WHERE userid = {userid}")
    decision = cursor.fetchone()

    return decision['student_decision']

def get_all_courses(db:mysql.connector.connection.MySQLConnection):

    cursor = db.cursor(dictionary=True)
    cursor.execute(f"SELECT crn FROM courses")
    courses = cursor.fetchall()

    return courses

def get_prereq(crn:int, db:mysql.connector.connection.MySQLConnection) -> list:

    cursor = db.cursor(dictionary=True)
    cursor.execute(f"SELECT crn, prereq_ID FROM prerequisites WHERE crn = {crn}")
    pre_reqs = cursor.fetchall()

    return pre_reqs

def set_deposit(status:str, userid:int, db:mysql.connector.connection.MySQLConnection) -> None:

    cursor = db.cursor(dictionary=True)
    cursor.execute(f"UPDATE application SET deposit = '{status}' WHERE userid = {userid}")

    return

def get_deposit(userid:int, db: mysql.connector.connection.MySQLConnection) -> str:
    
    cursor = db.cursor(dictionary=True)
    cursor.execute(f"SELECT deposit FROM application WHERE userid = {userid}")
    deposit = cursor.fetchone()

    return deposit['deposit']

def set_transcript_link(userid:int, link:str, db:mysql.connector.connection.MySQLConnection) -> None:

    cursor = db.cursor(dictionary=True)
    cursor.execute(f"UPDATE app_transcript SET link = '{link}' WHERE userid = {userid}")


    return

def set_transcript_method(userid:int, method:str, db:mysql.connector.connection.MySQLConnection) -> None:

    cursor = db.cursor(dictionary=True)
    cursor.execute(f"UPDATE app_transcript SET method = '{method}' WHERE userid = {userid}")

    return


# def format_pre(db:mysql.connector.connection.MySQLConnection) -> dict:


#     courses = get_all_courses(connect_db())
    
#     result = {}

#     for course in courses:
#         pre_reqs = get_prereq(course['crn'], connect_db())
#         if len(pre_reqs) > 0:
#             for pre in pre_reqs:
#                 course_info = get_course_info(pre['crn'], connect_db())
#                 print("PRE-REQ COURSE INFO: ", result)
#                 if course['crn'] in result.keys():
#                     print("IN", result.keys())
#                     result[pre['crn']] = result[pre['crn']] + " Pre-req #2 = " + str(course_info['dept']) + " " + course_info['cid']
#                 else:
#                     result[pre['crn']] = "Pre-req #1 = " + str(course_info['dept']) + " " + course_info['cid']
    
#     return result

def checkMasters(uid:int, db:mysql.connector.connection.MySQLConnection):

    reqs = False 

    cursor = db.cursor(dictionary = True)

    gpa = gpaCalc(uid, db)

    if not gpa:
        return False

    # Check that student has a faculty advisor
    studInfo = get_studinfo(uid, db)

    if studInfo['fid'] != None:
        hasAdvisor = True
    else:
        hasAdvisor = False

    # Check MS degree requirements
    courseReqs = ['1', '2', '3']

    #count of how many courseReqs are completed 
    courseReqs_count = 0

    # Checks if student has completed the 3 required courses
    cursor.execute("SELECT crn FROM transcripts WHERE uid = %s", (uid,))
    completed_courses = cursor.fetchall()

    coursesReq = False
    #goes through the complted courses by the student
    for course in completed_courses:
        print(course['crn'])  # Add this line to check the 'crn' values being iterated over
        if course['crn'] in courseReqs:
            courseReqs_count += 1
            coursesReq = courseReqs_count == 3
    
    # Checks if student has the required min GPA
    gpaReq = gpa >= 3.0
    print("Min GPA Met: ", gpaReq)

    # Checks if the student has the credit hours requirement
    cursor.execute("SELECT COUNT(*) FROM transcripts WHERE uid = %s", (uid,))
    credsDone = cursor.fetchone()['COUNT(*)'] * 3
    credHours = credsDone >= 30

    # Check if the student has taken at most 2 courses outside the CS department
    cursor.execute("SELECT COUNT(*) FROM transcripts t JOIN courses c ON t.crn = c.crn WHERE c.dept != 'CSCI' AND t.uid = %s", (uid,))
    nonCScourses = cursor.fetchone()['COUNT(*)'] <= 2
    print(nonCScourses)

    #check if there are more than two B's in the transcript
    cursor.execute("SELECT COUNT(grade) FROM transcripts WHERE uid = %s AND grade IN ('B-', 'C+', 'C', 'C-', 'D+', 'D', 'D-', 'F')", (uid,))
    gBelowB = cursor.fetchone()['COUNT(grade)'] < 3


    print(coursesReq, gpaReq, credHours, nonCScourses, gBelowB, hasAdvisor)

    print('Min GPA Met:', gpaReq)
    #checks if all the requirments are met 
    if coursesReq and gpaReq and credHours and nonCScourses and gBelowB and hasAdvisor:
        reqs = True
        print('I can Graduate!')

    return reqs


def checkDoctorate(uid:int, db:mysql.connector.connection.MySQLConnection):

    cursor = db.cursor(dictionary = True)

    gpa = gpaCalc(uid, db)

    if gpa == None:
        gpa = 0.00

    reqs = False

    # Check that student has a faculty advisor
    studInfo = get_studinfo(uid, db)

    if studInfo['fid'] != None:
        hasAdvisor = True
    else:
        hasAdvisor = False

    gpaReq = gpa >= 3.5

    # Check MS degree requirements
    courseReqs = [1, 2, 3]

    #count of how many courseReqs are completed 
    courseReqs_count = 0

    # Checks if student has completed the 3 required courses
    cursor.execute("SELECT crn FROM transcripts WHERE uid = %s", (uid,))
    completed_courses = cursor.fetchall()

    print(completed_courses)

    coursesReq = False
    #goes through the complted courses by the student
    for course in completed_courses:
        print(course['crn'])  # Add this line to check the 'crn' values being iterated over
        if course['crn'] in courseReqs:
            courseReqs_count += 1
            coursesReq = courseReqs_count == 3
    
    print(coursesReq)

    # Checks if the student has the general credit hours requirement
    cursor.execute("SELECT COUNT(*) FROM transcripts WHERE uid = %s", (uid,))
    credsDone = cursor.fetchone()['COUNT(*)'] * 3
    print(credsDone)
    genCreds = credsDone >= 36
    

    # Checks if the student has the CS credit hours requirement
    cursor.execute("SELECT COUNT(*) FROM transcripts t JOIN courses c ON t.crn = c.crn WHERE c.dept = 'CSCI' AND t.uid = %s", (uid,))
    credsDone = cursor.fetchone()['COUNT(*)'] * 3
    print(credsDone)
    csCreds = credsDone >= 30

    #checks if there are more than one B in the transcript
    cursor.execute("SELECT COUNT(grade) FROM transcripts WHERE uid = %s AND grade IN ('B-', 'C+', 'C', 'C-', 'D+', 'D', 'D-', 'F')", (uid,))
    below_b_count = cursor.fetchone()
    count = below_b_count['COUNT(grade)']

    gBelowB = count < 2

    thesisApp = False
    # THESIS DEFENSE APPROVAL
    cursor.execute("SELECT thesisApp FROM studInfo WHERE uid = %s", (uid,))
    if cursor.fetchone()['thesisApp'] == 1:
        thesisApp = True

    print(coursesReq, gpaReq, genCreds, csCreds, gBelowB, thesisApp, hasAdvisor)


    if coursesReq and gpaReq and genCreds and csCreds and gBelowB and thesisApp and hasAdvisor:
        reqs = True
        print('I can Graduate!')

    return reqs

def get_students_to_matriculate(db:mysql.connector.connection.MySQLConnection) -> list:

    cursor = db.cursor(dictionary = True)
    cursor.execute("SELECT * FROM application JOIN pre_app ON application.userid = pre_app.userid WHERE application.deposit = 'received' AND application.student_decision = 'accept' AND application.decision LIKE '%admit%'AND application.matriculated = 0")
    students = cursor.fetchall()

    return students

def send_email(user_name:str ,rec_name: str, email:str, letterid:int)-> None : 

    #Learned in part from https://www.youtube.com/watch?v=zxFXnLEmnb4 and https://www.geeksforgeeks.org/how-to-send-beautiful-emails-in-python/

    email_sender = 'londonogustavo984@gmail.com'
    email_password = 'hipg djbq fmva wlrq'

    email_receiver = email

    subject = 'Recommendation letter for ' + user_name

    body = f" {user_name} has requested a Recommendation Letter From you as a portion of their application to The George Washington University. \n Please follow this link and fill out the given form: http://127.0.0.1:8080/recommendation?name={rec_name}&email={email}&id={letterid}"


    em = EmailMessage()

    em['From'] = email_sender
    em['To'] = email_receiver
    em['Subject'] = subject
    em.set_content("""
    <!DOCTYPE html>
    <html>
    <head>
        <link rel="stylesheet" type="text/css" hs-webfonts="true" href="https://fonts.googleapis.com/css?family=Lato|Lato:i,b,bi">
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style type="text/css">
          h1{font-size:56px}
          h2{font-size:28px;font-weight:900}
          p{font-weight:100}
          td{vertical-align:top}
          #email{margin:auto;width:600px;background-color:#fff}
        </style>"""+
    f"""</head>
    <body bgcolor="#F5F8FA" style="width: 100%; font-family:Lato, sans-serif; font-size:18px;">
    <div id="email">
        <table role="presentation" width="100%">
            <tr>
                <td bgcolor="rgb(2, 25, 49)" align="center" style="color: white;">
                    <h1> The George Washington University </h1>
                </td>
        </table>
        <table role="presentation" border="0" cellpadding="0" cellspacing="10px" style="padding: 30px 30px 30px 60px;">
            <tr>
                <td>
                    <h2>You Have Been Chosen...To Recommend!</h2>
                    <p>
                        {user_name} has requested a recommendation letter from you as a part of their application to The George Washington University. Please follow the link:http://127.0.0.1:8080/recommendation?name={rec_name}&email={email}&id={letterid}
                    </p>
                </td>
            </tr>
        </table>
    </div>
    </body>
    </html>
""", subtype='html')

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context = context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.sendmail(email_sender, email_receiver, em.as_string())

    return

def send_email_decision(user_name:str ,email:str)-> None : 

    email_sender = 'londonogustavo984@gmail.com'
    email_password = 'hipg djbq fmva wlrq'

    email_receiver = email

    subject = 'Final Decision for ' + user_name

    body = f" {user_name} your decision from The George Washington University is in! Access it here: http://127.0.0.1:8080/applicantlogin"

    em = EmailMessage()

    em['From'] = email_sender
    em['To'] = email_receiver
    em['Subject'] = subject
    em.set_content(body)

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context = context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.sendmail(email_sender, email_receiver, em.as_string())

    return


def get_rec_emails(userid:int, db:mysql.connector.connection.MySQLConnection) -> list:

    cursor = db.cursor(dictionary=True)
    cursor.execute(f"SELECT rec_name, rec_email, letterid FROM recommendationletter WHERE userid = {userid}")
    emails = cursor.fetchall()


    return emails


def get_user_adform(uid:int, db:mysql.connector.connection.MySQLConnection) -> list:
    """ Gets course info using the uid associated with a advising form """

    cursor = db.cursor(dictionary=True)
    # get all courses added by the logged in user
    cursor.execute(f"SELECT * FROM courses INNER JOIN advisingForm ON courses.crn = advisingForm.crn WHERE advisingForm.uid = {uid}")
    AF_courses = cursor.fetchall()

    return AF_courses

def get_advisors(db:mysql.connector.connection.MySQLConnection) -> list:

    cursor = db.cursor(dictionary=True)
    cursor.execute(f"SELECT fname, lname, role_assign.uid FROM users JOIN role_assign ON users.uid = role_assign.uid WHERE users.role = 'advisor' or role_assign.role = 'advisor'")
    advisors = cursor.fetchall()

    return advisors

def get_user_review_forms(userid: int, db:mysql.connector.connection.MySQLConnection) -> list:

    cursor = db.cursor(dictionary=True)
    cursor.execute(f"SELECT * FROM reviewform INNER JOIN application ON finaldecision = decision and reviewid = applicationid LEFT JOIN app_transcript ON app_transcript.transcriptid = applicationid LEFT JOIN recommendationletter ON applicationid = letterid WHERE finaldecision = 'undecided' AND review_status = 'reviewed' AND transcriptstatus = 'received' AND recommendationletter.status = 'received' AND userid = {userid}")
    reviews = cursor.fetchall()

    return

def get_review_count(userid: int, db:mysql.connector.connection.MySQLConnection) -> int:

    cursor = db.cursor(dictionary=True)
    cursor.execute(f"SELECT COUNT(reviewerid) AS count FROM reviewform WHERE userid = {userid}")
    count = cursor.fetchone()

    return count['count']

def get_primary_role(uid:int, db:mysql.connector.connection.MySQLConnection) -> str:

    cursor = db.cursor(dictionary=True)
    cursor.execute(f"SELECT role FROM users WHERE uid = {uid}")
    role = cursor.fetchone()

    return role['role']

def get_secondary_roles(uid:int, db:mysql.connector.connection.MySQLConnection) -> list:

    cursor = db.cursor(dictionary=True)
    cursor.execute(f"SELECT role FROM role_assign WHERE uid = {uid}")
    roles = cursor.fetchall()

    return roles

def has_role(uid:int, auth_users:list, db:mysql.connector.connection.MySQLConnection) -> bool:

    roles = []

    #Get a user's primary roles, as dictated in the users table
    primary_role = get_primary_role(uid, connect_db())
    #Get a user's secondary role as dictated in role_assign
    secondary_roles = get_secondary_roles(uid, connect_db())

    #Add the primary role to a list of roles
    roles.append(primary_role)

    #add secondary roles into the list
    for role in secondary_roles:
        if not role:
            continue
        else:
            roles.append(role['role'])

    #Get rid of duplicates by going from list -> set
    new_roles = set(roles)

    #check if the desired role is in the user's list
    for role in auth_users:
        if role in new_roles:
            return True

    #it isn't
    return False


def get_all_students(db:mysql.connector.connection.MySQLConnection) -> dict:

    cursor = db.cursor(dictionary=True)
    cursor.execute(f"SELECT * FROM users WHERE role = 'grad_student'")
    students = cursor.fetchall()

    return students

def get_userid_letterid(letterid:int, db:mysql.connector.connection.MySQLConnection) -> int:

    cursor = db.cursor(dictionary=True)
    cursor.execute(f"SELECT userid FROM recommendationletter WHERE letterid = {letterid}")
    letter_id = cursor.fetchone()


    return letter_id['userid']


def set_app_rec_status(userid:int, status:str, db:mysql.connector.connection.MySQLConnection) -> None:

    cursor = db.cursor(dictionary=True)
    cursor.execute(f"UPDATE application SET rec_status = '{status}' WHERE userid = {userid}")

    return

def choose_advisor(userid:int, db:mysql.connector.connection.MySQLConnection) -> int:

    top_advisor = 11111125
    low_advisor = 11111128

    app_data = get_app_data(userid, connect_db())
    last_name = app_data['lastname']
    print(ord(last_name[0].lower()))
    
    #If the student's last name is before M, give them top_advisor.
    #Otherwise, give them low_advisor
    if ord(last_name[0].lower()) < 109:
        return top_advisor
    else:
        return low_advisor

def get_student_advisor(uid:int, db:mysql.connector.connection.MySQLConnection) -> dict:

    cursor = db.cursor(dictionary=True)
    cursor.execute(f"SELECT * FROM users WHERE uid IN(SELECT fid FROM studInfo WHERE uid = {uid});")
    advisor = cursor.fetchone()

    return advisor

def advisor_student_dict(db:mysql.connector.connection.MySQLConnection) -> list:

    students = get_all_students(connect_db())

    list = []

    for student in students:
        # print("Student",student)
        advisor = get_student_advisor(student['uid'], connect_db())
        # print("Advisor",advisor)
        if advisor:
            list.append(student)
            student['advisor'] = advisor

    return list


def add_course(db, crn, prof_uid, cid, dept, title, credits):
    cursor = db.cursor()
    
    cursor.execute("SELECT crn FROM courses WHERE crn = %s", (crn,))
    if cursor.fetchone() is not None:
        flash("CRN already exists", 'error')
        return False  
    
    cursor.execute("SELECT uid FROM users WHERE uid = %s", (prof_uid,))
    result = cursor.fetchone()  

    
    query = "INSERT INTO courses (crn, prof_uid, cid, dept, title, credits) VALUES (%s, %s, %s, %s, %s, %s)"
    cursor.execute(query, (crn, prof_uid, cid, dept, title, credits))
    db.commit()
    flash("Course added successfully", 'success')
    return True

def schedule_course(db, cid, class_day, class_time, semester, section, class_size, crn):
    cursor = db.cursor()
    query = "INSERT INTO scheduling (cid, class_day, class_time, semester, section, class_size, crn) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    cursor.execute(query, (cid, class_day, class_time, semester, section, class_size, crn))
    db.commit()

def check_existing_course(crn:int, db:mysql.connector.connection.MySQLConnection) -> bool:
    ''' Checks if a course exists based on the crn '''
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM courses WHERE crn = %s", (crn,))
    course_to_add = cursor.fetchone()
    if course_to_add != None:
        return True
    return False
    
    
def getallcourses(db:mysql.connector.connection.MySQLConnection):
    cursor = db.cursor(dictionary=True)
    query = "SELECT title, dept, courses.crn, credits, class_day, class_time, semester, section, class_size FROM courses JOIN scheduling ON courses.crn = scheduling.crn"
    cursor.execute(query)
    courses = cursor.fetchall()
    cursor.close() 
    return courses

def get_form1(uid:int, db:mysql.connector.connection.MySQLConnection):
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT crn FROM form1 WHERE uid = %s", (uid, ))
    form1 = cursor.fetchall()

    return form1

def get_all_course_info(db:mysql.connector.connection.MySQLConnection):

    cursor = db.cursor(dictionary=True)
    cursor.execute(f"SELECT * FROM courses ORDER BY crn ASC;")
    courses = cursor.fetchall()

    return courses

def delete_coursefunc(db:mysql.connector.connection.MySQLConnection, crn):
    cursor = db.cursor()
    cursor.execute("DELETE FROM scheduling WHERE crn = %s", (crn,))


    db.commit()


def get_program_stats(db:mysql.connector.connection.MySQLConnection) -> tuple:

    cursor = db.cursor(dictionary=True)

    #Get total
    cursor.execute(f"SELECT COUNT(*) AS count FROM studInfo")
    total = cursor.fetchone()['count']
    #Get number of masters
    cursor.execute(f"SELECT COUNT(*) AS count FROM studInfo WHERE program = 'Masters'")
    masters = cursor.fetchone()['count']
    #Get number of doctorate
    cursor.execute(f"SELECT COUNT(*) AS count FROM studInfo WHERE program = 'Doctorate'")
    doctorate = cursor.fetchone()['count']

    masters_percentage = (int(masters)/int(total))*100

    doctorate_precentage = (int(doctorate)/int(total))*100

    print("Total:", total, "Masters:", masters, "Doctorate:", doctorate)
    print("Masters:", str(masters_percentage))
    print("Doctorate:", str(doctorate_precentage))


    return [masters_percentage, doctorate_precentage]

def get_all_apps(db:mysql.connector.connection.MySQLConnection, table=None, filter=None) -> list:

    cursor = db.cursor(dictionary=True)

    if filter and table == 'applicant':
        print(filter)
        cursor.execute(f"SELECT * FROM application ORDER BY {filter} DESC")
        apps = cursor.fetchall()
        return apps
    elif filter and table == 'user':
        print(filter)
        cursor.execute(f"SELECT u.uid, u.fname, u.lname, u.email, a.year, a.degreessought, COALESCE(a.semester, 'N/A') AS semester FROM users u LEFT JOIN application a ON u.uid = a.uid WHERE u.role != ('alumni') ORDER BY COALESCE(a.{filter}, 'N/A');")
        apps = cursor.fetchall()
        return apps
    elif filter and table =='alumni':
        print(filter)
        cursor.execute(f"SELECT u.uid, u.fname, u.lname, u.email, a.year, a.degreessought, COALESCE(a.semester, 'N/A') AS semester FROM users u LEFT JOIN application a ON u.uid = a.uid WHERE u.role == ('alumni') ORDER BY COALESCE(a.{filter}, 'N/A');")
        apps = cursor.fetchall()
        return apps

    if table == 'user':
        cursor.execute("SELECT u.uid, u.fname, u.lname, u.email, a.year, a.degreessought FROM users u JOIN application a ON u.uid = a.uid;")
        result = cursor.fetchall()
        return result

    cursor.execute("SELECT * FROM application")
    apps = cursor.fetchall()

    return apps

from fpdf import FPDF

def generate_pdf(transcripts, student_name, student_id, gpa):
    # landscape or portraist????
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_font("Times", size=12)

    # this is the top part (the title and stuff)
    pdf.cell(100, 10, txt="THE GEORGE WASHINGTON UNIVERSITY", ln=False, align='C')
    pdf.cell(0, 10, txt="OFFICE OF THE REGISTRAR", ln=True, align='R')
    pdf.line(10, 30, 287, 30) 
    
    pdf.cell(0, 10, txt=f"Record of {student_name} (Student ID: {student_id})", ln=True, align='C')
    pdf.cell(0, 10, txt=f"GPA: {gpa}", ln=True)

    # this is the table header
    header_widths = [30, 100, 15, 15, 30, 15] 
    headers = ["Course CRN", "Course Title", "Credits", "Grade", "Semester", "Section"]
    #iterate through headers to get the info
    for i, header in enumerate(headers):
        pdf.cell(header_widths[i], 10, header, border=1, align='C')
    pdf.ln()

    #row formatin
    for row in transcripts:
        pdf.cell(header_widths[0], 10, str(row['crn']), border=1)
        pdf.cell(header_widths[1], 10, row['course_title'], border=1)
        pdf.cell(header_widths[2], 10, str(row['credits']), border=1)
        pdf.cell(header_widths[3], 10, str(row['grade']), border=1)
        pdf.cell(header_widths[4], 10, row['semester'], border=1)
        pdf.cell(header_widths[5], 10, str(row['section']), border=1)
        pdf.ln()

    pdf_file_path = f"transcripts_{student_id}.pdf"
    pdf.output(pdf_file_path)

    return pdf_file_path


