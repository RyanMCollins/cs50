import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""

    # Get user id
    user_id = session["user_id"]

    # Get account balance
    user_balance = getuserbalance(user_id)

    # Get user stock info from db
    stocks = db.execute("SELECT stock, shares FROM shares WHERE user_id = :user_id", user_id=user_id)

    total_share_value = 0
    rows = ""

    # For each stock
    for stock in stocks:

        # Get stock name, sumbol and share value
        name, symbol, share_price = getstockinfo(stock["stock"])

        # Calculate value of all owned shares
        shares = stock["shares"]
        user_shares_value = share_price * shares

        # Add value of all owned shares to total share value
        total_share_value += user_shares_value

        # Add stock name, symbol, shares owned, share value and value of all owned shares to html sequence
        rows += "<tr><th>" + name + "</th><th>" + symbol + "</th><th>" + str(shares) + "</th><th>" + usd(share_price) \
                + "</th><th>" + usd(user_shares_value) + "</th></tr>"

    # Add total share value to account balance for total value
    total_value = usd(total_share_value + user_balance)
    user_balance = usd(user_balance)

    return render_template("index.html", rows=rows, cash=user_balance, portfolio=total_value)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Get username
        user_id = session["user_id"]

        # Get form data
        symbol = request.form.get("symbol")
        shares = request.form.get("shares")

        if not symbol:
            return apology("Stock not specified. Your order was cancelled")
        elif not shares:
            return apology("Number of shares not specified. Your order was cancelled")

        if not shares.isnumeric():
            return apology("Illegal character in shares field. Your order was cancelled")

        if "." in shares:
            return apology("Number of shares must be an integer. Your order was cancelled")

        shares = int(shares)

        if shares < 1:
            return apology("Not a valid number of shares. Your order was cancelled")

        # Get share price and symbol
        _, symbol, share_price = getstockinfo(symbol)
        if symbol == None:
            return apology("Stock Symbol Invalid")

        price = share_price * shares

        # Check that user can afford transaction
        user_balance = getuserbalance(user_id)
        if price > user_balance:
            return apology("Account balance is insufficient. Your order was cancelled")

        # Subtract transaction price from user's account
        new_balance = user_balance - price
        updateusercash(new_balance, user_id)

        # Add transaction to database
        addtransaction(user_id, symbol, shares, share_price, "buy")

        # Check if the user has shares of that stock
        has_shares = check_shares(user_id, symbol)

        if has_shares:

            # Update share count
            prev_shares = getshares(symbol, user_id)
            new_shares = shares + prev_shares
            updateshares(new_shares, user_id, symbol)

        else:

            # Insert information
            insertshares(user_id, symbol, shares)

        return redirect("/")

    else:
        return render_template("buy.html")


@app.route("/check", methods=["GET"])
def check():
    """Return true if username available, else false, in JSON format"""

    username = request.args.get("username")

    # Check that username is not taken
    is_taken = not (0 == db.execute("SELECT COUNT(id) FROM users WHERE username = :username",
                                    username=username)[0]['COUNT(id)'])

    is_valid = (not is_taken) and len(username) > 0
    if is_valid:
        return jsonify(True)
    else:
        return jsonify(False)


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""

    # Get user id
    user_id = session["user_id"]

    # Get user transaction info from db
    transactions = db.execute("SELECT * FROM transactions WHERE user_id = :user_id", user_id=user_id)

    rows = ""

    # For each transaction
    for transaction in transactions:

        # Extract information
        date_time = transaction["date_time"]
        symbol = transaction["stock"]
        shares = transaction["shares"]
        share_price = transaction["share_price"]
        order_type = transaction["order_type"]

        # Get stock name
        name, _, _ = getstockinfo(symbol)

        # Calculate order value
        order_value = share_price * shares

        # Add date/time, stock name, symbol, shares exchanged, share value, order value, order type to html sequence
        rows += "<tr><th>" + date_time + "</th><th>" + name + "</th><th>" + symbol + "</th><th>" + str(shares) + "</th><th>" \
            + usd(share_price) + "</th><th>" + usd(order_value) + "</th><th>" + order_type + "</th></tr>"

    return render_template("history.html", rows=rows)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""

    if request.method == "POST":

        # Get symbol
        symbol = request.form.get("symbol")

        # Lookup stock information
        name, symbol, price = getstockinfo(symbol)

        if name == None:
            return apology("Stock Symbol Invalid")

        return render_template("quoted.html", name=name, symbol=symbol, price=usd(price))

    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password")

        # Ensure confirmation was submitted
        elif not request.form.get("confirmation"):
            return apology("must provide password confirmation")

        # Forget any user_id
        session.clear()

        # Get username and password
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Check that username is not taken
        is_taken = not (0 == db.execute("SELECT COUNT(id) FROM users WHERE username = :username",
                                        username=username)[0]['COUNT(id)'])

        if is_taken:
            return apology("username is already in use.")

        # Check that passwords match
        if password != confirmation:
            return apology("passwords do not match")

        # Create password hash
        password = generate_password_hash(password)

        # Add new user to database
        db.execute("INSERT INTO users ('username', 'hash') VALUES (:username, :password)", username=username, password=password)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=username)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        return render_template("quote.html")

    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""

    # Get user_id
    user_id = session["user_id"]

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Get form data
        symbol = request.form.get("symbol")
        shares = request.form.get("shares")

        if not symbol:
            return apology("Stock not specified. Your order was cancelled")
        elif not shares:
            return apology("Number of shares not specified. Your order was cancelled")

        shares = int(shares)

        if shares < 1:
            return apology("Not a valid number of shares. Your order was cancelled")

        # Get share price and symbol
        _, symbol, share_price = getstockinfo(symbol)
        if symbol == None:
            return apology("Stock Symbol Invalid")

        price = share_price * shares

        # Check if the user has shares of that stock
        has_shares = check_shares(user_id, symbol)

        if not has_shares:
            return apology("You do not own any shares of this stock. Your order was cancelled")

        # Check that user has sufficient shares
        shares_owned = getshares(symbol, user_id)

        if shares > shares_owned:
            return apology("You do not own enough shares. Your order was cancelled")

        # Add transaction price to user's account
        user_balance = getuserbalance(user_id)
        new_balance = user_balance + price
        updateusercash(new_balance, user_id)

        # Add transaction to database
        addtransaction(user_id, symbol, shares, share_price, "sell")

        # Update user's shares in database
        if shares == shares_owned:
            deleteshares(user_id, symbol)
        else:
            new_shares = shares_owned - shares
            updateshares(new_shares, user_id, symbol)

        return redirect("/")

    else:

        # Get list of user stocks from database
        stocks = db.execute("SELECT stock FROM shares WHERE user_id = :user_id", user_id=user_id)

        options = ""

        for stock in stocks:
            symbol = stock["stock"]

            # Add symbol to select menu
            options += "<option value='" + symbol + "'>" + symbol + "</option>"

        return render_template("sell.html", options=options)


@app.route("/transfer", methods=["GET", "POST"])
@login_required
def transfer():
    """Transfer shares to another user"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Get user_id
        user_id = session["user_id"]

        # Get form data
        symbol = request.form.get("symbol")
        shares = request.form.get("shares")
        transferee = request.form.get("transferee")

        if not symbol:
            return apology("Stock not specified. Your order was cancelled")
        elif not shares:
            return apology("Number of shares not specified. Your order was cancelled")
        elif not transferee:
            return apology("Username not specified. Your order was cancelled")

        shares = int(shares)

        # Get updated symbol and share price
        _, symbol, share_price = getstockinfo(symbol)
        if symbol == None:
            return apology("Stock Symbol Invalid")

        # Check that transferee exists
        is_user = not (0 == db.execute("SELECT COUNT(username) FROM users WHERE username = :username",
                                       username=transferee)[0]["COUNT(username)"])

        if not is_user:
            return apology("User does not exist. Your transfer was cancelled")

        transferee_id = db.execute("SELECT id FROM users WHERE username = :username",
                                   username=transferee)[0]["id"]

        # Check that user is not transferring to self
        if user_id == transferee_id:
            return apology("You cannot transfer to yourself")

        # Check if the user has shares of that stock
        has_shares = check_shares(user_id, symbol)

        if not has_shares:
            return apology("You do not own any shares of this stock. Your order was cancelled")

        # Check that user has sufficient shares
        shares_owned = getshares(symbol, user_id)

        if shares > shares_owned:
            return apology("You do not own enough shares. Your order was cancelled")

        # Update user's shares in database
        if shares == shares_owned:
            deleteshares(user_id, symbol)
        else:
            new_shares = shares_owned - shares
            updateshares(new_shares, user_id, symbol)

        # Add transaction to database for user
        addtransaction(user_id, symbol, shares, share_price, "transfer_send")

        # Update transferee's shares in database
        has_shares = check_shares(transferee_id, symbol)

        if has_shares:

            # Update share count
            prev_shares = getshares(symbol, transferee_id)
            new_shares = shares + prev_shares
            updateshares(new_shares, transferee_id, symbol)

        else:

            # Insert information
            insertshares(transferee_id, symbol, shares)

        # Add transaction to database for transferee
        addtransaction(transferee_id, symbol, shares, share_price, "transfer_receive")

        return redirect("/history")
    else:
        return render_template("transfer.html")


def getuserbalance(id):
    """Return cash balance of id"""
    return db.execute("SELECT cash FROM users WHERE id = :user_id", user_id=id)[0]["cash"]


def getstockinfo(symbol):
    """Get name, proper symbol, and share price of stock"""

    stockInfo = lookup(symbol)

    if stockInfo == None:
        return (None, None, None)

    name = stockInfo["name"]
    symbol = stockInfo["symbol"]
    share_price = stockInfo["price"]

    return (name, symbol, share_price)


def updateusercash(balance, id):
    """Update the user's cash balance"""
    db.execute("UPDATE users SET cash = :balance WHERE id = :user_id", balance=balance, user_id=id)
    return True


def updateshares(new_shares, user_id, symbol):
    """Update shares in database"""
    db.execute("UPDATE shares SET shares = :new_shares WHERE user_id = :user_id AND stock = :symbol",
               new_shares=new_shares, user_id=user_id, symbol=symbol)


def addtransaction(user_id, symbol, shares, share_price, order_type):
    """Add transaction to database"""
    return db.execute("INSERT INTO transactions ('user_id', 'stock', 'shares', 'share_price', 'order_type') \
                        VALUES (:user_id, :symbol, :shares, :share_price, :order_type)",
                      user_id=user_id, symbol=symbol, shares=shares, share_price=share_price, order_type=order_type)


def check_shares(user_id, symbol):
    """Check if user has any shares of stock"""
    return not (0 == db.execute("SELECT COUNT(stock) FROM shares WHERE user_id = :user_id AND stock = :symbol",
                                user_id=user_id, symbol=symbol)[0]['COUNT(stock)'])


def getshares(symbol, user_id):
    """Get number of shares user has of stock"""
    return db.execute("SELECT shares FROM shares WHERE stock = :symbol AND user_id = :user_id",
                      symbol=symbol, user_id=user_id)[0]["shares"]


def insertshares(user_id, symbol, shares):
    """Insert new share info into database"""
    return db.execute("INSERT INTO shares ('user_id', 'stock', 'shares') VALUES (:user_id, :symbol, :shares)",
                      user_id=user_id, symbol=symbol, shares=shares)


def deleteshares(user_id, symbol):
    """Delete share info from database"""
    db.execute("DELETE FROM shares WHERE user_id = :user_id AND stock = :symbol", user_id=user_id, symbol=symbol)


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
