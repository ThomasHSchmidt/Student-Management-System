""" Imports flask, geminiai and Needed functions from functions.py"""

from flask import Flask, flash, send_file, session, render_template, redirect, url_for, request
import google.generativeai as genai
import PyPDF2
from functions import *

# Page On Load, Landing page : from here one can choose which login to go to
@app.route("/", methods=["GET", "POST"])
def landing():


    return render_template("general/landingpage.html")


# Page On Load, Login Page : from here one can login or register for a new account
@app.route("/applicantlogin", methods=["GET", "POST"])
def applicantlogin():
    """Routes you based on signup or login, if signup go to the signup template, if login, the session variables are initialized and routed to the roles homepage"""

    if request.method == "POST":

        print(request.form)

        if "Signup" in request.form:

            return render_template("signup.html")

        if "Login" in request.form:

            email = request.form.get("Email")
            password = request.form.get("Password")

            if not all([email, password]):
                flash("Please fill in all required fields!", "Failed")
                return render_template("applicant/login.html")

            user = check_login_userid(email, password, connect_db())

            if user is None:
                flash("Authencation Failed! ", "Failed")
                return render_template("applicant/login.html")

            # Initialize Session Variables

            if "userid" not in session:
                session["userid"] = user["userid"]
            
            if "fname" not in session:
                session["fname"] = user["fname"]

            if "lname" not in session:
                session["lname"] = user["lname"]

            if "email" not in session:
                session["email"] = user["email"]

            if "role" not in session:
                session["role"] = user["role"]
            # Redirect to the right home based on the role

            if session["role"] == 'applicant':
                return redirect(url_for("applicanthome"))
            else:
                return redirect(url_for("userhome"))

    clear_session(session)

    return render_template("applicant/login.html")

# Page On Load, Login Page : from here one can login
@app.route("/mainlogin", methods=["GET", "POST"])
def mainlogin():
    """Routes you based on signup or login, if signup go to the signup template, if login, the session variables are initialized and routed to the roles homepage"""

    if request.method == "POST":

        print(request.form)

        if 'return' in request.form:
            return redirect('/')

        if "email" in request.form:

            email = request.form.get("email")
            password = request.form.get("password")

            print(email, password)

            if not all([email, password]):
                flash("Please fill in all required fields!", "Failed")
                return render_template("login.html")

            user = check_login_uid(email, password, connect_db())

            print("HERE:",user)

            if user is None:
                flash("Authencation Failed! ", "Failed")
                return render_template("login.html")

            # Initialize Session Variables

            if "uid" not in session:
                session["uid"] = user["uid"]

            if "fname" not in session:
                session["fname"] = user["fname"]
            
            if "lname" not in session:
                session["lname"] = user["lname"]

            if "email" not in session:
                session["email"] = user["email"]

            if "role" not in session:
                session["role"] = user["role"]
            # Redirect to the right home based on the role
            
            # if session['role'] == 'grad_student':
            #     return redirect(url_for('studentHome', uid = session['uid']))
            # else:
            #     return redirect(url_for('facultyHome', uid = session['uid']))
            return redirect(url_for("home", uid = user['uid']))

    clear_session(session)

    return render_template("login.html")

# Allows prospective users to create an account in the system
@app.route("/signup", methods=["GET", "POST"])
def signup():
    """Gets new registration formation, checks, then generates the new account information in the databasereg
    isitration"""

    if request.method == "POST":

        email = request.form.get("email")
        firstname = request.form.get("fname").capitalize()
        lastname = request.form.get("lname").capitalize()
        password = request.form.get("password")

        if not all([email, firstname, lastname, password]):
            flash("Please fill in all required fields!", "Failed")
            return render_template("applicant/signup.html")

        if check_email(email, connect_db()) is not None:

            flash("Email already exists!", "Failed")

            return render_template("applicant/signup.html")
        else:

            new_user = add_preapp(email, lastname, firstname, password, connect_db())

            if new_user:
                flash("Signup successful! Please login.", "Success")
                return render_template("applicant/login.html")
            else:
                flash("Signup failed. Please try again.", "Faied")
                return render_template("applicant/signup.html")

    return render_template("applicant/signup.html")


# Brings a user to their homepage depending on their role ONLY FOR UNIVERSITY USERS
@app.route("/home/<uid>", methods=["GET", "POST"])
def home(uid):
    db = connect_db()
    cursor = db.cursor(dictionary=True)

    """Brings the user the the correct home page based on
    the role saved within the session variable"""
    if "role" not in session:
        return redirect('/')

    primary = get_user_role(uid, connect_db())
    secondary_roles = get_secondary_roles(uid, connect_db())

    print(primary)

    if primary == "grad_student" or "grad_student" in secondary_roles:
        return redirect("/studentHome/"+str(uid))
    elif primary == "alumni" or "alumni" in secondary_roles:
        return redirect("/alumniHome/"+str(uid))
    else:
        return redirect("/facultyHome/"+str(uid))


# A section which allows the user to enter, save, correct, and submit
# all needed information for the application process.
@app.route("/application", methods=["GET", "POST"])
def application():
    """
    Returns:

    Returns template for application with user application data Retrieves
    information from the database whenever a template is loaded

    Functions:

    Retrieves and Loads user data for the application Handles POST (Save and
    Submit) Updates the database with new user data through forms Display Error
    Messages when fields are not properly filled

    Check:

    Contains a number of detailed checks which ensure the contents of
    all information being passed from the form, through python and
    eventually into the database

    """

    auth_users = ['user','applicant']
    

    userid = session["userid"]

    # Retrieve the application data for the user from the database and display
    # it by passing it into the template
    if "userid" in session:

        # Pass in any existing attributes about the user into the template

        priordegreeinfo = get_prior_degree_info(userid, connect_db())

        # When Submit or Save is pressed
        if request.method == "POST":

            userid = session["userid"]

            ## Get Personal Information ##

            firstname = request.form.get("firstname")
            lastname = request.form.get("lastname")
            address = request.form.get("address")
            ssn = request.form.get("ssn")
            phonenumber = request.form.get("phone")

            # Get Academic Information #
            degreessought = request.form.get("SoughtOptions")
            semester = request.form.get("Semester")
            year = request.form.get("Year")

            BS = request.form.getlist("BS")
            MS = request.form.getlist("MS")

            greverbal = request.form.get("greverbal")
            grequantitative = request.form.get("grequantitative")

            greyearofexam = request.form.get("greyearofexam")
            greadvancedscore = request.form.get("greadvancedscore")
            greadvancedsubject = request.form.get("greadvancedsubject")

            areas_interest = request.form.get("areas_interest")

            priorwork = request.form.get("priorwork")

            priorwork_edit = priorwork.replace("'", "\\'\\")

            # Initialize Prior Degrees to avoid errors
            priordegrees = None

            rec_name = request.form.get("rec_name")
            rec_email = request.form.get("rec_email")

            rec_name2 = request.form.get("rec_name2")
            rec_email2 = request.form.get("rec_email2")

            rec_name3 = request.form.get("rec_name3")
            rec_email3 = request.form.get("rec_email3")

            rec_data = [{'rec_name':rec_name, 'rec_email':rec_email},{'rec_name':rec_name2, 'rec_email':rec_email2},{'rec_name':rec_name3, 'rec_email':rec_email3}]

            print("HERE:", rec_data)

            # Degrees Sought Options Checks
            if degreessought is None:
                degreessought = None

            # Number of Prior Degrees Check

            # If BS is empty, then no prior degrees have been entered
            if len(BS) == 0:
                priordegrees = None

            # If MS contains information, then the user has a MS and a BS
            # (masters requires bachelors)
            if len(MS) > 0:
                priordegrees = degree_info(2, request.form)

            # Else if only the BS contains information, then the user has a
            # BS
            elif len(BS) > 0:
                priordegrees = degree_info(1, request.form)

            # Delete MS from PD if MS is sought

            if degreessought == "MS":
                if priordegrees is None:
                    flash("Please Select A Prior Degree!", "Failed")
                    save_app(
                        userid,
                        firstname,
                        lastname,
                        address,
                        ssn,
                        phonenumber,
                        priordegrees,
                        degreessought,
                        areas_interest,
                        greverbal,
                        grequantitative,
                        priorwork_edit,
                        greyearofexam,
                        greadvancedscore,
                        greadvancedsubject,
                        semester,
                        year,
                        rec_data
                    )
                    return render_template(
                        "applicant/application.html",
                        user_data=get_app_data(userid, connect_db()),
                        rec_data = get_rec_data(userid, connect_db()),
                        priordegreeinfoBS=get_degrees(userid)[0],
                        priordegreeinfoMS=get_degrees(userid)[1],
                    )

                if ("MS" in priordegrees) is True:
                    # for attribute in priordegrees.keys():
                    #     if attribute == "MS":
                    del priordegrees["MS"]

            # Check if the user is trying to save the current form information
            if "Save" in request.form:

                try:
                    # Save all current form information
                    save_app(
                        userid,
                        firstname,
                        lastname,
                        address,
                        ssn,
                        phonenumber,
                        priordegrees,
                        degreessought,
                        areas_interest,
                        greverbal,
                        grequantitative,
                        priorwork_edit,
                        greyearofexam,
                        greadvancedscore,
                        greadvancedsubject,
                        semester,
                        year,
                        rec_data
                    )
                except Exception as e:
                    print("Something went wrong:", e)
                    flash(e, "Failed")
                    save_app(
                        userid,
                        firstname,
                        lastname,
                        address,
                        '',
                        phonenumber,
                        priordegrees,
                        degreessought,
                        areas_interest,
                        greverbal,
                        grequantitative,
                        priorwork_edit,
                        greyearofexam,
                        greadvancedscore,
                        greadvancedsubject,
                        semester,
                        year,
                        rec_data
                    )
                    return render_template(
                        "applicant/application.html",
                        user_data=get_app_data(userid, connect_db()),
                        rec_data = get_rec_data(userid, connect_db()),
                        priordegreeinfoBS=get_degrees(userid)[0],
                        priordegreeinfoMS=get_degrees(userid)[1],
                    )

                flash("Progress Saved", "Success")

            # Check if the user is trying to submit the current form information
            elif "Submit" in request.form:

                print("RECDATA", rec_data)

                try:
                    save_app(
                        userid,
                        firstname,
                        lastname,
                        address,
                        ssn,
                        phonenumber,
                        priordegrees,
                        degreessought,
                        areas_interest,
                        greverbal,
                        grequantitative,
                        priorwork_edit,
                        greyearofexam,
                        greadvancedscore,
                        greadvancedsubject,
                        semester,
                        year,
                        rec_data
                    )
                except Exception as e:
                    print("Something went wrong:", e)
                    flash(e, "Failed")
                    return render_template(
                        "applicant/application.html",
                        user_data=get_app_data(userid, connect_db()),
                        rec_data = get_rec_data(userid, connect_db()),
                        priordegreeinfoBS=get_degrees(userid)[0],
                        priordegreeinfoMS=get_degrees(userid)[1],
                    )

                if priordegrees is None:
                    flash(
                        "Prior Degrees is empty!",
                        "Failed",
                    )
                    return render_template(
                        "applicant/application.html",
                        user_data=get_app_data(userid, connect_db()),
                        rec_data = get_rec_data(userid, connect_db()),
                        priordegreeinfoBS=get_degrees(userid)[0],
                        priordegreeinfoMS=get_degrees(userid)[1],
                    )

                if len(priordegrees) > 1:
                    if priordegrees["BS"]["year"] >= priordegrees["MS"]["year"]:
                        flash(
                            "A Masters Cannot Be Completed Before a Bachelors!",
                            "Failed",
                        )
                        return render_template(
                            "applicant/application.html",
                            user_data=get_app_data(userid, connect_db()),
                            rec_data = get_rec_data(userid, connect_db()),
                            priordegreeinfoBS=get_degrees(userid)[0],
                            priordegreeinfoMS=get_degrees(userid)[1],
                        )

                # Null check for all form fields (NOT PHD-REQUIRED FIELDS)
                if not all(
                    [
                        firstname,
                        lastname,
                        address,
                        ssn,
                        phonenumber,
                        priordegrees,
                        degreessought,
                    ]
                ):
                    flash("Please fill in all required fields!", "Failed")
                    return render_template(
                        "applicant/application.html",
                        user_data=get_app_data(userid, connect_db()),
                        rec_data = get_rec_data(userid, connect_db()),
                        priordegreeinfoBS=get_degrees(userid)[0],
                        priordegreeinfoMS=get_degrees(userid)[1],
                    )

                if all(x.isalpha() for x in (firstname + lastname)):
                    pass
                else:
                    flash(
                        "Incorrect Name Format, Make sure first name and last name consist of only alphabetical letters.",
                        "Failed",
                    )
                    return render_template(
                        "applicant/application.html",
                        user_data=get_app_data(userid, connect_db()),
                        rec_data = get_rec_data(userid, connect_db()),
                        priordegreeinfoBS=get_degrees(userid)[0],
                        priordegreeinfoMS=get_degrees(userid)[1],
                    )

                # Check if the user is seeking a MS, if so delete pd ms they
                # have a prior MS degree
                if degreessought == "MS":
                    if ("MS" in priordegrees) is True:
                        # for attribute in priordegrees.keys():
                        #     if attribute == "MS":
                        del priordegrees["MS"]

                        pass

                # PriorDegrees is a dictionary of dictionaries, we first need to
                # iterate through each dictionary, then we iterate through each
                # attribute and return a tuple of 2 values, from there we check
                # the second value and make sure it is not none or in our case,
                # empty string.
                for degree in priordegrees.keys():
                    for attribute in priordegrees[degree].items():
                        if attribute[1] == "":
                            flash(
                                "Please fill in all required fields under Prior Degrees!",
                                "Failed",
                            )
                            return render_template(
                                "applicant/application.html",
                                user_data=get_app_data(userid, connect_db()),
                                rec_data = get_rec_data(userid, connect_db()),
                                priordegreeinfoBS=get_degrees(userid)[0],
                                priordegreeinfoMS=get_degrees(userid)[1],
                            )

                # Check if the user is seeking a PHD
                if degreessought == "PHD":

                    # Null check for all form fields (INCLUDING PHD-REQUIRED
                    # FIELDS)
                    if not all(
                        [
                            firstname,
                            lastname,
                            address,
                            ssn,
                            phonenumber,
                            priordegrees,
                            degreessought,
                            greverbal,
                            grequantitative,
                        ]
                    ):
                        flash(
                            "Please fill in all required fields! (GRE Scores are required for PHD applicants)",
                            "Failed",
                        )
                        return render_template(
                            "applicant/application.html",
                            user_data=get_app_data(userid, connect_db()),
                            rec_data = get_rec_data(userid, connect_db()),
                            priordegreeinfoBS=get_degrees(userid)[0],
                            priordegreeinfoMS=get_degrees(userid)[1],
                        )

                    # Check if a PHD applicant has a Masters
                    if ("MS" in priordegrees) == False:
                        flash(
                            "Please fill in all required fields! (Masters and Bachelors degrees are required for PHD applicants)",
                            "Failed",
                        )
                        return render_template(
                            "applicant/application.html",
                            user_data=get_app_data(userid, connect_db()),
                            rec_data = get_rec_data(userid, connect_db()),
                            priordegreeinfoBS=get_degrees(userid)[0],
                            priordegreeinfoMS=get_degrees(userid)[1],
                        )

                    if (int(greverbal) < 1 or int(greverbal) > 170) or (
                        int(grequantitative) < 1 or int(grequantitative) > 170
                    ):
                        flash("Invalid GRE Score", "Failed")
                        return render_template(
                            "applicant/application.html",
                            user_data=get_app_data(userid, connect_db()),
                            rec_data = get_rec_data(userid, connect_db()),
                            priordegreeinfoBS=get_degrees(userid)[0],
                            priordegreeinfoMS=get_degrees(userid)[1],
                        )

                # End of PHD Applicant Check

                # Degrees Sought Options Checks
                if degreessought is None:
                    flash("You have to pursue a degree!", "Failed")
                    return render_template(
                        "applicant/application.html",
                        user_data=get_app_data(userid, connect_db()),
                        rec_data = get_rec_data(userid, connect_db()),
                        priordegreeinfoBS=get_degrees(userid)[0],
                        priordegreeinfoMS=get_degrees(userid)[1],
                    )

                # Prior Degree Check
                if len(BS) == 0:
                    flash("You must have a Prior Degree!", "Failed")
                    return render_template(
                        "applicant/application.html",
                        user_data=get_app_data(userid, connect_db()),
                        rec_data = get_rec_data(userid, connect_db()),
                        priordegreeinfoBS=get_degrees(userid)[0],
                        priordegreeinfoMS=get_degrees(userid)[1],
                    )

                if len(MS) > 0:
                    priordegrees = degree_info(2, request.form)
                elif len(BS) > 0:
                    priordegrees = degree_info(1, request.form)
                else:
                    flash("You must have a prior degree!", "Failed")
                    return render_template(
                        "applicant/application.html",
                        user_data=get_app_data(userid, connect_db()),
                        rec_data = get_rec_data(userid, connect_db()),
                        priordegreeinfoBS=get_degrees(userid)[0],
                        priordegreeinfoMS=get_degrees(userid)[1],
                    )

                # Check if inputs are formatted correctly

                # ssn format
                if (
                    len(ssn) == 11
                    and ssn[0:2].isnumeric()
                    and ssn[3] == "-"
                    and ssn[4:5].isnumeric()
                    and ssn[6] == "-"
                    and ssn[7:10].isnumeric()
                ):
                    pass
                else:
                    flash("Invalid SSN", "Failed")
                    return render_template(
                        "applicant/application.html",
                        user_data=get_app_data(userid, connect_db()),
                        rec_data = get_rec_data(userid, connect_db()),
                        priordegreeinfoBS=get_degrees(userid)[0],
                        priordegreeinfoMS=get_degrees(userid)[1],
                    )

                # phonenumber format
                if (
                    len(phonenumber) == 12
                    and phonenumber[0:2].isnumeric()
                    and phonenumber[3] == "-"
                    and phonenumber[4:6].isnumeric()
                    and phonenumber[7] == "-"
                    and phonenumber[8:11].isnumeric()
                ):
                    pass
                else:
                    flash("Invalid Phone Number", "Failed")
                    return render_template(
                        "applicant/application.html",
                        user_data=get_app_data(userid, connect_db()),
                        rec_data = get_rec_data(userid, connect_db()),
                        priordegreeinfoBS=get_degrees(userid)[0],
                        priordegreeinfoMS=get_degrees(userid)[1],
                    )
                if grequantitative:
                    if greverbal:
                        pass
                    else:
                        flash("Please fill out the other GRE Score!", "Failed")
                        return render_template(
                            "applicant/application.html",
                            user_data=get_app_data(userid, connect_db()),
                            rec_data = get_rec_data(userid, connect_db()),
                            priordegreeinfoBS=get_degrees(userid)[0],
                            priordegreeinfoMS=get_degrees(userid)[1],
                        )

                if greverbal:
                    if grequantitative:
                        pass
                    else:
                        flash("Please fill out the other GRE Score!", "Failed")
                        return render_template(
                            "applicant/application.html",
                            user_data=get_app_data(userid, connect_db()),
                            rec_data = get_rec_data(userid, connect_db()),
                            priordegreeinfoBS=get_degrees(userid)[0],
                            priordegreeinfoMS=get_degrees(userid)[1],
                        )

                if grequantitative:
                    if len(grequantitative) > 3 or grequantitative.isalpha():
                        flash("Invalid GRE Score", "Failed")
                        return render_template(
                            "applicant/application.html",
                            user_data=get_app_data(userid, connect_db()),
                            rec_data = get_rec_data(userid, connect_db()),
                            priordegreeinfoBS=get_degrees(userid)[0],
                            priordegreeinfoMS=get_degrees(userid)[1],
                        )
                    if int(grequantitative) < 1 or int(grequantitative) > 170:
                        flash("Invalid GRE Score", "Failed")
                        return render_template(
                            "applicant/application.html",
                            user_data=get_app_data(userid, connect_db()),
                            rec_data = get_rec_data(userid, connect_db()),
                            priordegreeinfoBS=get_degrees(userid)[0],
                            priordegreeinfoMS=get_degrees(userid)[1],
                        )
                if greverbal:
                    if len(greverbal) > 3 or greverbal.isalpha():
                        flash("Invalid GRE Score", "Failed")
                        return render_template(
                            "applicant/application.html",
                            user_data=get_app_data(userid, connect_db()),
                            rec_data = get_rec_data(userid, connect_db()),
                            priordegreeinfoBS=get_degrees(userid)[0],
                            priordegreeinfoMS=get_degrees(userid)[1],
                        )
                    if int(greverbal) < 1 or int(greverbal) > 170:
                        flash("Invalid GRE Score", "Failed")
                        return render_template(
                            "applicant/application.html",
                            user_data=get_app_data(userid, connect_db()),
                            rec_data = get_rec_data(userid, connect_db()),
                            priordegreeinfoBS=get_degrees(userid)[0],
                            priordegreeinfoMS=get_degrees(userid)[1],
                        )

                if greadvancedscore:
                    if (len(greadvancedscore) < 4) and greadvancedscore[
                        0:2
                    ].isnumeric():
                        pass
                    else:
                        flash("Invalid GRE Advanced Score", "Failed")
                        return render_template(
                            "applicant/application.html",
                            user_data=get_app_data(userid, connect_db()),
                            rec_data = get_rec_data(userid, connect_db()),
                            priordegreeinfoBS=get_degrees(userid)[0],
                            priordegreeinfoMS=get_degrees(userid)[1],
                        )
                    if int(greadvancedscore) < 1 or int(greadvancedscore) > 120:
                        flash("Invalid GRE Advanced Score", "Failed")
                        return render_template(
                            "applicant/application.html",
                            user_data=get_app_data(userid, connect_db()),
                            rec_data = get_rec_data(userid, connect_db()),
                            priordegreeinfoBS=get_degrees(userid)[0],
                            priordegreeinfoMS=get_degrees(userid)[1],
                        )

                    if greadvancedsubject == "":
                        flash("GRE Score must have a subject!", "Failed")
                        return render_template(
                            "applicant/application.html",
                            user_data=get_app_data(userid, connect_db()),
                            rec_data = get_rec_data(userid, connect_db()),
                            priordegreeinfoBS=get_degrees(userid)[0],
                            priordegreeinfoMS=get_degrees(userid)[1],
                        )

                if grequantitative and greverbal:
                    if greyearofexam == "":
                        flash("GRE Score's must have a year!", "Failed")
                        return render_template(
                            "applicant/application.html",
                            user_data=get_app_data(userid, connect_db()),
                            rec_data = get_rec_data(userid, connect_db()),
                            priordegreeinfoBS=get_degrees(userid)[0],
                            priordegreeinfoMS=get_degrees(userid)[1],
                        )
                    else:
                        if (
                            len(greyearofexam) == 4
                            and (greyearofexam)[0:3].isnumeric()
                            and (greyearofexam) < "2025"
                        ):
                            pass
                        else:
                            flash("Invalid GRE Year", "Failed")
                            return render_template(
                                "applicant/application.html",
                                user_data=get_app_data(userid, connect_db()),
                                rec_data = get_rec_data(userid, connect_db()),
                                priordegreeinfoBS=get_degrees(userid)[0],
                                priordegreeinfoMS=get_degrees(userid)[1],
                            )

                for degree in priordegrees.keys():
                    for attribute in priordegrees[degree].items():
                        if attribute[0] == "year":
                            if (
                                len(attribute[1]) == 4
                                and (attribute[1])[0:3].isnumeric()
                                and (attribute[1]) < "2025"
                            ):
                                pass
                            else:
                                flash("Invalid Prior Degree Year", "Failed")
                                return render_template(
                                    "applicant/application.html",
                                    user_data=get_app_data(userid, connect_db()),
                                    rec_data = get_rec_data(userid, connect_db()),
                                    priordegreeinfoBS=get_degrees(userid)[0],
                                    priordegreeinfoMS=get_degrees(userid)[1],
                                )

                for degree in priordegrees.keys():
                    for attribute in priordegrees[degree].items():
                        if attribute[0] == "gpa":
                            if (
                                len(attribute[1]) == 4
                                and (attribute[1])[0].isnumeric()
                                and (attribute[1])[1] == "."
                                and (attribute[1])[2:3].isnumeric()
                                and (attribute[1]) <= "4.00"
                            ):
                                pass
                            else:
                                flash("Invalid Prior Degree GPA", "Failed")
                                return render_template(
                                    "applicant/application.html",
                                    user_data=get_app_data(userid, connect_db()),
                                    rec_data = get_rec_data(userid, connect_db()),
                                    priordegreeinfoBS=get_degrees(userid)[0],
                                    priordegreeinfoMS=get_degrees(userid)[1],
                                )
                if not any([all([rec_name, rec_email]), all([rec_name2, rec_email2]), all([rec_name3, rec_email3])]):
                    flash("You must have 3 recommendations", "Failed")
                    return render_template(
                        "applicant/application.html",
                        user_data=get_app_data(userid, connect_db()),
                        rec_data = get_rec_data(userid, connect_db()),
                        priordegreeinfoBS=get_degrees(userid)[0],
                        priordegreeinfoMS=get_degrees(userid)[1],
                    )
                # end of checkformat

                submit_app(
                    userid,
                    connect_db(),
                )

                flash("Succesfully Submitted!", "Success")

                return redirect(url_for("applicanthome"))

            else:
                return
        print("HERE:",len(get_rec_data(userid, connect_db())))
        return render_template(
            "applicant/application.html",
            user_data=get_app_data(userid, connect_db()),
            rec_data = get_rec_data(userid, connect_db()),
            priordegreeinfoBS=get_degrees(userid)[0],
            priordegreeinfoMS=get_degrees(userid)[1],
        )

    return render_template(
        "applicant/application.html",
        user_data=get_app_data(userid, connect_db()),
        rec_data = get_rec_data(userid, connect_db()),
        priordegreeinfoBS=get_degrees(userid)[0],
        priordegreeinfoMS=get_degrees(userid)[1],
    )


# Where faculty reviewers are able to view the completed
# applications submitted by applicants
@app.route("/viewapplication/<applicationid>", methods=["GET", "POST"])
def viewapplication(applicationid):
    """Displays an application along with the contents entered by the applicant"""

    auth_users = ['admin', 'reviewer', 'gs', 'chair']

    if not session['uid']:
        return redirect("/")

    if not has_role(session['uid'], auth_users, connect_db()):
        flash("You do not have the necessary permissions to access this functionality", "Failed")
        return redirect (url_for("home", uid = session['uid']))

    return render_template(
        "faculty/viewapplication.html",
        user_data=get_app_data_appid(applicationid, connect_db()),
        priordegreeinfoBS=get_degrees_appid(applicationid)[0],
        priordegreeinfoMS=get_degrees_appid(applicationid)[1],
        rec_data = get_rec_data(get_userid(applicationid, connect_db()), connect_db())
    )


# Where a user is able to view their usernname, and email,
# and begin an application or logout
@app.route("/userhome", methods=["GET", "POST"])
def userhome():

    auth_users = ['user']

    """Contains the options that users will have : Only have the option of
    applying"""

    if request.method == "POST":

        if "Apply" in request.form:

            return redirect(url_for("application"))
        if "Logout" in request.form:

            return redirect(url_for("logout"))

    return render_template("applicant/userhome.html")

# Where a user is able to view their usernname, and email,
# and begin an application or logout
@app.route("/transcript", methods=["GET", "POST"])
def transcript():
    """Contains the options that users will have : Only have the option of
    applying"""

    if request.method == "POST":

        print(request.form)

        if "Submit" in request.form:
            # ImmutableMultiDict([('medium', 'mail'), ('transcript_link', ''), ('Submit', 'Submit')])
            medium = request.form.get('medium')
            link = request.form.get('transcript_link')

            if not medium:
                flash("Choose how you plan on sending your transcript!", "Failed")
                return redirect(url_for("transcript"))
            
            
            if medium == 'link' and len(link) == 0:
                flash("Please provide a link!", "Failed")
                return redirect(url_for("transcript"))

            set_transcript_method(session['userid'], medium, connect_db())

            if link:
                set_transcript_link(session['userid'], link, connect_db())

            set_transcript_status('received', session['userid'], connect_db())

            return redirect(url_for("applicanthome"))

    return render_template("applicant/transcript.html")

# Where a recommender is able to fill out a recommendation letter
@app.route("/recommendation", methods=["GET", "POST"])
def recommendation():

    #URL Variables
    email = request.args.get('email')
    name = request.args.get('name')
    letterid = request.args.get('id')
    print("TEST:",request.args)
    print(get_rec_info(letterid, connect_db()))

    if request.method == "POST":
        print("YUHHH:",request.form)

        #Form Variables
        rec_name = request.form.get("rec_name")
        rec_email = request.form.get("rec_email")
        rec_letter = request.form.get("rec_letter")

        #URL Variable
        letterid = request.args.get('id')
        userid = get_userid_letterid(letterid, connect_db())

        if "Submit" in request.form:

            # Checks for form
            if not all([rec_name, rec_email, rec_letter]):
                flash("Please fill in all required fields!", "Failed")
                return redirect(url_for("recommendation"))
            else:
                db = connect_db()
                cursor = db.cursor()
                print(rec_name, rec_email, rec_letter, letterid)

                updaterec = "UPDATE recommendationletter SET rec_letter = %s, status = 'received' WHERE letterid = %s"

                updaterecvalues = (rec_letter, letterid)

                cursor.execute(updaterec, updaterecvalues)

                flash("Recommendation Letter Submitted!", "Success")

                rec_data = get_rec_data(userid, connect_db())

                status = []
                for rec in rec_data:
                    if rec['status'] == 'not received':
                        return redirect("/")
                
            set_app_rec_status(userid, 'received', connect_db())

            # If there are no form errors
            return redirect("/")

        if "Return" in request.form:

            return redirect("/")

    return render_template(
        "applicant/recommendation.html", rec_info=get_rec_info(letterid, connect_db())
    )

@app.route('/matriculate',methods = ['GET','POST'])
def matriculate():

    auth_users = ['gs', 'admin']

    if not session['uid']:
        return redirect("/")

    if not has_role(session['uid'], auth_users, connect_db()):
        flash("You do not have the necessary permissions to access this functionality", "Failed")
        return redirect (url_for("home", uid = session['uid']))

    if 'users_to_matriculate' not in session:
        session['users_to_matriculate'] = []


    if request.method == 'POST':

        if 'return' in request.form:
            session.pop('users_to_matriculate')
            return redirect("/home")

        #add a student to the group of student to be matriculated
        if 'add' in request.form:
            userid_to_matriculate = request.form.get('add')

            choose_advisor(userid_to_matriculate, connect_db())

            if userid_to_matriculate:

                students_to_matriculate = session['users_to_matriculate']

                for i in range(len(students_to_matriculate)):
                    if int(students_to_matriculate[i]['data']['userid']) == int(userid_to_matriculate):
                        flash("Student Already Added", "Failed")
                        return render_template('faculty/matriculate.html', student_matriculate = get_students_to_matriculate(connect_db()))

                students_to_matriculate.append({'userid':userid_to_matriculate, 'data':get_app_data(userid_to_matriculate, connect_db())})
                session['users_to_matriculate'] = students_to_matriculate
                return render_template('faculty/matriculate.html', student_matriculate = get_students_to_matriculate(connect_db()))
        
        #Remove a student from the list of students to be matriculated
        if 'remove' in request.form:
            userid = request.form.get('remove')

            students_to_matriculate = session['users_to_matriculate']
            if len(students_to_matriculate) > 0:
                print(len(students_to_matriculate))
                for i in range(len(students_to_matriculate)):
                    print("i:",i)
                    if int(students_to_matriculate[i]['data']['userid']) == int(userid):
                        students_to_matriculate.pop(i)
                        break

                session['users_to_matriculate'] = students_to_matriculate
            else:
                return render_template('faculty/matriculate.html', student_matriculate = get_students_to_matriculate(connect_db()))

        #Matriculate all matricualtable students in tha main list
        if 'all' in request.form:
            for student in get_students_to_matriculate(connect_db()):
                try:
                    matriculate_student(student['data']['userid'], connect_db())
                except Exception as e:
                    print("Error Detected:", e)
                    return render_template('faculty/matriculate.html', student_matriculate = get_students_to_matriculate(connect_db()))
            session.pop('users_to_matriculate')
            return render_template('faculty/matriculate.html', student_matriculate = get_students_to_matriculate(connect_db()))

        #Matriculate all matricualtable students in tha main list
        if 'group' in request.form:
            students_to_matriculate = session['users_to_matriculate']
            print("HERE",students_to_matriculate)
            for student in students_to_matriculate:
                try:
                    matriculate_student(student['data']['userid'], connect_db())
                except Exception as e:
                    print("Error Detected:", e)
                    return render_template('faculty/matriculate.html', student_matriculate = get_students_to_matriculate(connect_db()))
            session.pop('users_to_matriculate')
            return render_template('faculty/matriculate.html', student_matriculate = get_students_to_matriculate(connect_db()))
                
        #Matriculate a single student NOW
        if 'now' in request.form:

            userid = request.form.get('now')

            students_to_matriculate = session['users_to_matriculate']
            if len(students_to_matriculate) > 0:
                for i in range(len(students_to_matriculate)):
                    if int(students_to_matriculate[i]['data']['userid']) == int(userid):
                        students_to_matriculate.pop(i)

                session['users_to_matriculate'] = students_to_matriculate
            try:
                matriculate_student(userid, connect_db())
            except Exception as e:
                print("Error Detected:", e)
                return render_template('faculty/matriculate.html', student_matriculate = get_students_to_matriculate(connect_db()))

            return render_template('faculty/matriculate.html', student_matriculate = get_students_to_matriculate(connect_db()))
        
        if 'clear' in request.form:
            session.pop('users_to_matriculate')
            return render_template('faculty/matriculate.html', student_matriculate = get_students_to_matriculate(connect_db()))

    return render_template('faculty/matriculate.html', student_matriculate = get_students_to_matriculate(connect_db()))

#edit user account profile
@app.route('/editInfo',methods = ['GET','POST'])
def editInfo():
    #connect to database 
    db = connect_db()
    cursor = db.cursor(dictionary = True)
    print("In Edit")

    #make sure method is POST
    if request.method == 'POST':
        print("In edit post")
        print("YUHHHH:",request.form)

        # Update each field individually 
        email = request.form.get('email')
        if email:
            cursor.execute("UPDATE users SET email = %s WHERE uid = %s", (email, session.get('uid')))  

        password = request.form.get('password')
        if password:
            cursor.execute("UPDATE users SET password = %s WHERE uid = %s", (password, session.get('uid')))

        address = request.form.get('address')
        if address:
            cursor.execute("UPDATE users SET address = %s WHERE uid = %s", (address, session.get('uid')))

        fname = request.form.get('fname')
        if fname:
            cursor.execute("UPDATE users SET fname = %s WHERE uid = %s", (fname, session.get('uid')))

        lname = request.form.get('lname')
        if lname:
            cursor.execute("UPDATE users SET lname = %s WHERE uid = %s", (lname, session.get('uid')))

        db.commit()
        print('Commited!')

        return redirect(url_for('home', uid = session['uid']))

    return render_template('editInfo.html')


@app.route('/advisingForm', methods=['GET', 'POST'])
def advisingForm():

    db = connect_db()
    cursor = db.cursor(dictionary=True)
    AF_courses = get_user_adform(session['uid'], db)
    all_courses = get_all_course_info(connect_db())
    error = ""
    studInfo = get_studinfo(session['uid'], db)
    print(request.form)

    # Adding a course to the advisingForm
    if 'crn' in request.form:
        # get user info
        userInfo = get_user_info(session['uid'], db)
    
        # check that user exists
        if userInfo != None: 
            # get the corresponding trancript
            cursor.execute('SELECT crn FROM transcripts WHERE uid = %s', (session['uid'],))
            transcript = cursor.fetchall()
        
            # get all courses added by the logged in user
            AF_courses = get_user_adform(session['uid'], db)
            
            crn = request.form['crn']
            error = ""

            if crn:
                # verify that course exists in courses
                if check_existing_course(crn, db) == False:
                    error = "Please add a valid course"
                    return render_template('advisingForm.html', AF_courses = AF_courses, error = error, studInfo=studInfo, courses=all_courses)

            # verify that course does not already exist in advisingForm
            cursor.execute("SELECT * FROM advisingForm WHERE uid = %s and crn = %s", (session['uid'], crn,))
            if cursor.fetchone() != None:
                error = "Course already added"
                return render_template('advisingForm.html', AF_courses = AF_courses, error = error, studInfo=studInfo, courses=all_courses)
            
            cursor.execute("SELECT prereq_ID FROM prerequisites WHERE crn = %s", (crn,))
            prereqs = cursor.fetchall()
            # Prereq Check
            not_found = []
            if prereqs != None:
                print("prereqs", prereqs)
                for req in prereqs:
                    found = False
                    print("check", req['prereq_ID'])
                    for course_num in transcript:
                        if req['prereq_ID'] == course_num['crn']:
                            found = True
                    if not found:
                        print("NUTHING", req['prereq_ID'])
                        not_found.append(req['prereq_ID']) 
                        print(not_found)  

                if len(not_found) > 0:
                    for course in not_found:
                        print("course",course)
                        missing_course = get_course_info(course, db)
                        print("missing course:", missing_course)
                        flash("Missing pre-req: " + missing_course['title'] + " (" + missing_course['dept'] + " "+\
                        missing_course['cid'] + ") CRN: " + str(missing_course['crn']))
                        print("ERROR", error)
                    return render_template('advisingForm.html', AF_courses = AF_courses, error = error, studInfo=studInfo, courses=all_courses)

            print("MOVING ON")
            # add the course into the advisingForm table
            cursor.execute("INSERT INTO advisingForm (uid, crn) VALUES (%s, %s)", (session['uid'], crn))
            db.commit()
            flash("Course Added", "Success")
            print("Inserted into DB!!")
            
            # get updated advisingForm table
            cursor.execute("SELECT advisingForm.crn, courses.cid, courses.dept, courses.title, courses.credits FROM advisingForm INNER JOIN courses ON advisingForm.crn = courses.crn WHERE advisingForm.uid = %s", (session['uid'],))
            AF_courses = cursor.fetchall()
            db.commit()
            
            return render_template('advisingForm.html', AF_courses = AF_courses, error = error, studInfo=studInfo, courses=all_courses)

    # Removing a course from the advisingForm
    elif 'remove' in request.form:
        # get user info
        userInfo = get_user_info(session['uid'], db)
    
        # check that user exists
        if userInfo != None: 
            # get the corresponding trancript
            cursor.execute('SELECT crn FROM transcripts WHERE uid = %s', (session['uid'],))
            transcript = cursor.fetchall()
        
            # get all courses added by the logged in user
            f1_courses = get_user_courses(session['uid'], db)
            
            crn = request.form['remove']
            error = ""


            # verify that course does not already exist in advisingForm
            cursor.execute("SELECT * FROM advisingForm WHERE uid = %s and crn = %s", (session['uid'], crn,))
            if cursor.fetchone() == None:
                print("Transcript problem")
                error = "Course not on advising form. How did you even do that?"
                return render_template('advisingForm.html', AF_courses = AF_courses, error = error, studInfo=studInfo, courses=all_courses)


            for course in transcript:
                cursor.execute("SELECT prereq_ID FROM prerequisites WHERE crn = %s", (course['crn'],))
                prereqs = cursor.fetchall()
            
            cursor.execute("SELECT crn FROM prerequisites WHERE prereq_ID = %s", (crn,))
            havePrereq = cursor.fetchall()


            for course in havePrereq:
                cursor.execute("DELETE FROM advisingForm WHERE uid = %s AND crn = %s", (session['uid'], crn))

            # add the course into the advisingForm table
            cursor.execute("DELETE FROM advisingForm WHERE uid = %s AND crn = %s", (session['uid'], crn))
            db.commit()
            flash("Course Deleted", "Success")
            print("Deleted from DB!!")
            
            # get updated advisingForm table
            cursor.execute("SELECT advisingForm.crn, courses.cid, courses.dept, courses.title, courses.credits FROM advisingForm INNER JOIN courses ON advisingForm.crn = courses.crn WHERE advisingForm.uid = %s", (session['uid'],))
            AF_courses = cursor.fetchall()
            db.commit()
            
            return render_template('advisingForm.html', AF_courses = AF_courses, error = error, studInfo=studInfo, courses=all_courses)

        return render_template('advisingForm.html', AF_courses = AF_courses, error = error, studInfo=studInfo, courses=all_courses)
    else:
        return render_template('advisingForm.html', AF_courses = AF_courses, error = error, studInfo=studInfo, courses=all_courses)

@app.route('/updateAdvisor', methods=['GET', 'POST'])
def updateAdvisor():
    db = connect_db()
    cursor = db.cursor(dictionary=True)


    if request.method == 'POST':
        print(request.form)
        new_fid = request.form['fid']
        uid = request.form['uid']

        cursor.execute("UPDATE studInfo SET fid = %s WHERE uid = %s", (new_fid, uid,))
        db.commit()

        return render_template('/updateAdvisor.html', studentList = advisor_student_dict(connect_db()), facultyList = get_advisors(connect_db()))
        
    return render_template('/updateAdvisor.html', studentList = advisor_student_dict(connect_db()), facultyList = get_advisors(connect_db()))


@app.route('/alumniHome/<uid>', methods = ['GET', 'POST'])
def alumniHome(uid):
    db = connect_db()
    cursor = db.cursor(dictionary=True)

    userdata = get_user_info(session['uid'], connect_db())

    studInfo = get_studinfo(session['uid'], connect_db())

    query = "SELECT transcripts.crn, grade, semester, section, title AS course_title, credits, tid FROM transcripts JOIN courses ON transcripts.crn = courses.crn WHERE transcripts.uid = %s ORDER BY transcripts.semester DESC"
    cursor.execute(query, (uid,))
    transcripts = cursor.fetchall()
    gpa = calculate_gpa(transcripts)
    roundedgpa = round(gpa, 2)

    if roundedgpa == None:
        roundedgpa = 0.00
    cursor.execute("UPDATE studInfo SET gpa = %s WHERE uid = %s", (roundedgpa, uid,))

    # query to get transcripts for the student uid
    query = "SELECT transcripts.crn, grade, semester, section, title AS course_title, credits, tid FROM transcripts JOIN courses ON transcripts.crn = courses.crn WHERE transcripts.uid = %s ORDER BY transcripts.semester DESC"
    cursor.execute(query, (uid,))
    transcripts = cursor.fetchall()  # get all rows of the query result

    if not session['uid']:
        return redirect("/")
    
    return render_template("alumniHome.html", session = session, studentID = uid, userdata = userdata, studInfo = studInfo, program = studInfo['program'], transcripts = transcripts)

get_program_stats(connect_db())
app.run(debug=True, host="0.0.0.0", port=8080)
