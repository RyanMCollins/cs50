import cs50
import csv

from flask import Flask, jsonify, redirect, render_template, request

# Configure application
app = Flask(__name__)

# Reload templates when they are changed
app.config["TEMPLATES_AUTO_RELOAD"] = True


@app.after_request
def after_request(response):
    """Disable caching"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods=["GET"])
def get_index():
    return redirect("/form")


@app.route("/form", methods=["GET"])
def get_form():
    return render_template("form.html")


@app.route("/form", methods=["POST"])
def post_form():
    # Get values from form
    name = request.form.get("name")
    email = request.form.get("email")
    school = request.form.get("school")
    location = request.form.get("location")
    standing = request.form.get("standing")
    interest = request.form.getlist("interest")

    # Check if any values are missing
    if(not name or not email or not school or not location or not standing or not interest):
        message = "You are missing information for one or more fields. Please go back"
        return render_template("error.html", message=message)

    interest = ", ".join(interest)

    # Write values to .csv file
    with open("survey.csv", "a") as survey:
        writer = csv.writer(survey)
        writer.writerow([name] + [email] + [school] + [location] + [standing] + [interest])

    return redirect("/sheet")


@app.route("/sheet", methods=["GET"])
def get_sheet():
    # Read rows from csv
    with open("survey.csv", 'r') as survey:
        reader = csv.reader(survey)
        rows = list(reader)

    # Write rows to html format
    tableRows = ""
    for row in rows:
        tableRows += "<tr><th>" + "</th><th>".join(row) + "</th></tr>"

    return render_template("sheet.html", rows=tableRows)
