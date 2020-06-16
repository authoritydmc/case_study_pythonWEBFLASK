# import this line in every new module you create this will give access to app with required library
# for more info check __init__.py file
from retail_banking import *

from time import gmtime, strftime
import time
from flask import redirect, render_template, url_for, json, flash

import hashlib

from retail_banking.DATABASES import customerdb as cdb
from retail_banking.DATABASES import executive as edb


@app.route('/')
def home():
    return render_template('home.html', home=True)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if isLoggedin():
        # redirect in case user is already logged In
        return(redirect(url_for('home')))
    if request.method == "GET":
        # show when default this url is loaded ..
        return render_template('login.html', login=True)
    else:
        # after user submit his username and password we get to this...
        uid = request.form.get('uid', "userNotFound")
        password = request.form.get('psw', "passwordNotfound")
        passhax = hashlib.sha256(password.encode()).hexdigest()

        filter = {'ssn_id': uid, 'pass': passhax}

        result = edb.find(filter)

        if result == None:
            flash("Wrong UserName or Password retry", "danger")
            return redirect(url_for('login'))
        else:
            # setup session~~~
            session_login(uid, result['name'])
            if isLoggedin():
                flash("Successfully Logged in", "success")
            else:
                flash("Can not setup session ", "danger")
            # end setup

            return redirect(url_for('home'))


@app.route('/registerExecutive', methods=['get', 'post'])
def registerExecutive():

    if request.method == "GET":
        return render_template('registerExecutive.html', registerExecutive=True)

    regdata = {}

    regdata['ssn_id'] = request.form.get('ssn')
    regdata['name'] = request.form.get('name')
    regdata['email'] = request.form.get('email')
    regdata['pass'] = hashlib.sha256(
        request.form.get('psw').encode()).hexdigest()

    regdata['creation_time'] = time.strftime(
        "%a,%d %b %Y %I:%M:%S %p %Z", time.gmtime())
    result, err = edb.register(regdata)

    if result:
        flash("Executive Registered Successfully ...    Login Now", "success")
        return redirect(url_for('login'))
    else:
        flash("Failed to Register :"+err, "danger")
        return redirect(url_for('registerExecutive'))

    return redirect('login.html')


@app.route('/registerCustomer', methods=['get', 'post'])
def registerCustomer():

    if not isLoggedin():
        # if there is no one loggedIn disallow this route
        flash("Login first to access it ", "danger")
        return redirect(url_for('home'))

    if request.method == "GET":
        return render_template('registerCustomer.html')

    regdata = {}

    regdata['ssn_id'] = request.form.get('ssn')
    regdata['name'] = request.form.get('name')
    regdata['age'] = request.form.get('age')
    regdata['state'] = request.form.get('state')
    regdata['city '] = request.form.get('city')
    regdata['address'] = request.form.get('address')

    print(regdata)  # Simulating database insertion

    result, err = cdb.registerSSN(regdata)

    if result:
        flash("Customer Registered Successfully", "success")
        return redirect(url_for('viewCustomerDetail')+"/"+regdata['ssn_id'])
    else:
        flash("Failed to Register Customer "+err, "danger")

    return render_template('registerCustomer.html')


@app.route('/logout')
def logout():
    if isLoggedin():
        # log out by invalidating session
        session_logout()
        flash("You have been successfully logged out", "success")
    else:
        flash("You are already Logged out..", "success")

    return redirect(url_for('home'))

# Utility Function


def session_logout():
    session.pop('ssn_id', None)
    session.pop('username', None)


def session_login(ssn_val, username):
    session['ssn_id'] = ssn_val
    session['username'] = username


def isLoggedin():
    if 'ssn_id' in session.keys():
        return True
    else:
        return False

# Search customer by SSN ID to delete or update details
@app.route('/searchCustomer', methods=['get', 'post'])
def searchCustomer():
    if not isLoggedin():
        return redirect(url_for('login'))

    if request.method == "GET":
        return render_template('searchCustomer.html')

        # when ssn_id is passed ..so

    # make a rediection while post ..
    return redirect(url_for('updateCustomer')+"/"+request.form.get('ssn_id'))


@app.route('/updateCustomer/<ssn_id>')
@app.route('/updateCustomer', methods=['get', 'post', 'update'])
def updateCustomer(ssn_id=None):

    if not isLoggedin():
        return redirect(url_for('login'))

    if request.method == "GET":
        if ssn_id == None:
            return redirect(url_for('searchCustomer'))
        else:
            # when ssn_id is passed ..so
            filter = {'ssn_id': ssn_id}

            # Retrieving details of customer
            result = cdb.findSSN(filter)
            if result:
                args = {}
                args['ssn_id'] = result['ssn_id']
                args['oldAge'] = result['age']
                args['oldAddress'] = result['address']
                args['oldName'] = result['name']
                return render_template('updateCustomer.html', **args)
            else:
                flash(
                    "Unable to find customer. Try again by entering valid SSN ID.", "danger")
                return redirect(url_for('searchCustomer'))

    regdata = {}

    regdata['ssn_id'] = request.form.get('ssn_id')
    regdata['name'] = request.form.get('newName')
    regdata['age'] = request.form.get('newAge')
    regdata['address'] = request.form.get('newAddress')

    result, err = cdb.updateSSN(regdata)

    if result:
        flash("Customer Details Updated Successfully", "success")
        return redirect(url_for('viewCustomerDetail')+"/"+regdata['ssn_id'])

    else:
        flash("Failed to Update  Customer  Details "+err, "danger")

    return redirect(url_for('searchCustomer'))


@app.errorhandler(404)
def not_found(e):
    return render_template('error404.html')


@app.route('/viewCustomerDetail/<ssn_id>')
@app.route('/viewCustomerDetail', methods=["GET", "POST"])
def viewCustomerDetail(ssn_id=None):
    if not isLoggedin():
        return redirect(url_for('login'))

    filter = {}
    if request.method == "GET":
        if ssn_id == None:
            redirect(url_for('searchCustomer'))
        else:
            filter = {'ssn_id': ssn_id}
    else:  # if it is a post request..
        filter = {'ssn_id': request.form.get('ssn_id')}

    # Retrieving details of customer
    result = cdb.findSSN(filter)
    print("ssn is ", ssn_id)
    print(result)

    if result:
        args = {}
        args['titleDetail'] = ":Customer SSN Detail"
        args['age'] = result['age']
        args['name'] = result['name']
        args['address'] = result['address']
        args['ssn_id'] = result['ssn_id']
        return render_template('viewCustomerDetail.html', **args)
    else:
        flash("Unable to find customer. Try again by entering valid SSN ID.", "danger")
        return redirect(url_for('searchCustomer'))


@app.route('/viewAllCustomer')
def viewAllCustomer():

    if not isLoggedin():
        return redirect(url_for('login'))

    customers_data = []
    for dat in cdb.findSSN_all():
        customers_data.append(dat)

    return render_template('viewAllCustomer.html', datas=customers_data)


@app.route('/deleteCustomer',methods=['GET','POST'])
def deleteCustomer():
    if not isLoggedin():
        return redirect(url_for('login'))

    if request.method == "GET":
        ssn_id = request.args.get('ssn_id')
        result = cdb.findSSN({'ssn_id': ssn_id})

        if result:
            args = {}
            args['ssn_id'] = result['ssn_id']
            args['oldAge'] = result['age']
            args['oldAddress'] = result['address']
            args['oldName'] = result['name']
            flash(" Customer found! Please confirm the details before deletion.")
            return render_template('confirmDeleteCustomer.html',**args)

        else:
            flash("Customer not found! Please enter a valid SSN ID.")
            return redirect(url_for('searchCustomer'))

    filter = {'ssn_id':request.form.get('ssn_id')}

    result = cdb.deleteSSN(filter)

    if result:
        print(result)
        flash("Successfully deleted customer!", "success")
        return render_template('home.html')
    else:
        flash("Unable to delete customer. Try again by entering valid SSN ID.", "danger")
        return redirect(url_for('searchCustomer'))


@app.route('/createAccount',methods=['get','post'])
def createAccount():
    if not isLoggedin():
        return redirect(url_for('login'))

    if request.method=="GET":
        return render_template('createAccount.html')

    # if request id POST
    data = {}

    # check if customer exists or not and return flash accordingly

    data['ssn_id'] = request.form.get('ssn_id')
    data['type'] = request.form.get('type')
    data['deposit'] = request.form.get('deposit')

    print(data)
    # save data to database.

    return data