from urllib import request
import requests
from flask import Flask,render_template,request,redirect,url_for,session,make_response
import firebase_admin
from firebase_admin import credentials,db


app=Flask(__name__)
app.secret_key="blah_dfdfgfcgx"
cred = credentials.Certificate("firebase_studyabroad.json")
firebase_admin.initialize_app(cred,{'databaseURL': 'https://studyabroadtestprep-ce307-default-rtdb.firebaseio.com'})


@app.route('/')
def home():
    return redirect(url_for("login"))

def SignIn(email,password):
    details={
        'email':email,
        'password':password,
        'returnSecureToken': True
    }
    #Post request
    apikey = "AIzaSyDk6zm-S2f2HV4Nagqc8NTyJsnHlXv4FzA"
    r=requests.post('https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={}'.format(apikey),data=details)
    #check for errors
    if 'error' in r.json().keys():
        return {'status':'error','message':r.json()['error']['message']}
    #success
    if 'idToken' in r.json().keys() :
            return {'status':'success','idToken':r.json()['idToken']}


def get_user_details(email):
    ref = db.reference("/users/")
    g = ref.get()
    for x,y in g.items():
        if y.get('email')==email:
            y['user_id']=x
            return y



@app.route('/login',methods=['GET',"POST"])
def login():
    if request.method=="GET":
        #if cookie found -> check email and password and if found correct render home page directly
        return render_template('login.html')
    else:
        #https://blog.icodes.tech/posts/python-firebase-authentication.html authentication using firebase
        email=request.form.get('email')
        password=request.form.get('password')
        signin_status=SignIn(email,password)
        if signin_status['status']=='error':
            return redirect(url_for('login'))
        else:
            session['email']=email
            user_details=get_user_details(email)
            session['user_id']=user_details['user_id']
            session['gre']=user_details.get('gre') #can be None
            session['ielts']=user_details.get('ielts') #can be None if not submitted
            pass #go to feed login success

def NewUser(email,password):
    details={
        'email':email,
        'password':password,
        'returnSecureToken': True
    }
    apikey="AIzaSyDk6zm-S2f2HV4Nagqc8NTyJsnHlXv4FzA"
    r=requests.post('https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={}'.format(apikey),data=details)
    #check for errors in result
    if 'error' in r.json().keys():
        return {'status':'error','message':r.json()['error']['message']}
    #if the registration succeeded
    if 'idToken' in r.json().keys() :
            return {'status':'success','idToken':r.json()['idToken']}


def add_user(username,email,password,gre,ielts):
    ref=db.reference('/users/')
    contents={'username':username,'email':email,'gre':gre,'ielts':ielts}
    ref.push().set(contents)

@app.route('/signup',methods=["POST","GET"])
def sign_up():
    if request.method=="GET":
        return render_template('signup.html')
    else:
        form=request.form
        signup_status=NewUser(form['email'],form['password'])
        if signup_status['status']=='error':
            return redirect(url_for('sign_up'))

        # resp = make_response(f"The Cookie has been Set")
        # resp.set_cookie('email', form['email'])
        #resp.set_cookie('password',form['password'])
        add_user(form['username'], form['email'],form['gre'],form['ielts'])
        user_details = get_user_details(form['email'])
        session['email']=form['email']
        session['user_id'] = user_details['user_id']
        session['gre'] = user_details.get('gre')  # can be None
        session['ielts'] = user_details.get('ielts')  # can be None if not submitted

        return redirect(url_for('login')) #redirect to feed







app.run(debug=True)