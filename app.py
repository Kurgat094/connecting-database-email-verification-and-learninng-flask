from flask import Flask,redirect,render_template,url_for,request,session,flash
import re
from flask_mysqldb import MySQL
from flask_mail import Mail,Message 
import random



app=Flask(__name__)
app.secret_key="secrets"

app.config["MAIL_SERVER"]='smtp.gmail.com'
app.config["MAIL_PORT"]=465
app.config["MAIL_USERNAME"]='tobiaskipkogei@gmail.com'
app.config["MAIL_PASSWORD"]='himfefhwbqyfhekg'
app.config["MAIL_USE_TLS"]=False
app.config["MAIL_USE_SSL"]=True
mail=Mail(app)

app.config["MYSQL_HOST"]='localhost'
app.config["MYSQL_USER"]='root'
app.config["MYSQL_PASSWORD"]=''
app.config["MYSQL_DB"]='medics'
app.config["MYSQL_CHARSET"]='latin1'

mysql=MySQL(app)

@app.route('/home')
def home():
    return render_template("home.html")

@app.route('/',methods=['POST','GET'])
def register():
    if 'username' in session:
        return redirect(url_for('home'))
    else:
        if request.method=='POST':
            username=request.form['username']
            email=request.form['email']
            password=request.form['password']
            confirm=request.form['confirm']
            occupation=request.form['role']
            if confirm != password:
                flash("password do not match","danger")
                return render_template("register.html",username=username,email=email,password=password,confirm=confirm)
            elif len(password)<7 :
                flash("password should be more than 7 ","danger")
                return render_template("register.html",username=username,email=email,password=password,confirm=confirm)
            elif not re.search("[a-z]",password):
                flash("password should have aleast one smalllettter ","danger")
                return render_template("register.html",username=username,email=email,password=password,confirm=confirm)
            elif not re.search("[A-Z]",password):
                flash("password should have aleast one capital lettter ","danger")
                return render_template("register.html",username=username,email=email,password=password,confirm=confirm)
            else:
                cur=mysql.connection.cursor()
                cur.execute("INSERT INTO users(username,email,password,occupation)VALUES(%s,%s,%s,%s)",(username,email,password,occupation))
                mysql.connection.commit()
                cur.close()
                msg=Message(subject='Account creation',sender="tobiaskipkogei@gmail.com",recipients=[email])
                msg.body=f"""Welcome to Tobby's Hospital
                            Your account credentials are
                            username:{username}
                            password:{password}"""
                mail.send(msg)
                flash(f"account create successfully for {username}","success")
                return redirect (url_for('login'))
        
    return render_template("register.html")
  
  
  
@app.route('/login',methods=["POST","GET"])
def login():
    if 'username' in session:
        return redirect(url_for('home'))
    else:
        if request.method=='POST':
            username=request.form['username']
            password=request.form['password']
            
            cur=mysql.connection.cursor() 
            cur.execute("SELECT * FROM users WHERE (username OR email)=%s AND password=%s",(username,password))
            mysql.connection.commit()
            data=cur.fetchone()
            if data:
                session['username']=data[1]
                session['userid']=data[0]
                session['role']=data[4]
                session['email']=data[2]
                flash(f" Your have logged in as {username} ","success")
                return redirect (url_for('home'))
            else:
                flash(f"Your have entered wrong credentials","danger")
                return render_template("login.html",username=username,password=password)
    return render_template("login.html")

@app.route('/occupation')
def occupation():
    return render_template("occupation.html")





@app.route('/logout')
def logout():
    session.clear()
    flash(f" Your have been logged out ","danger")
    return redirect(url_for('login'))



@app.route('/dashboard')
def dashboard():
    
    return render_template("dashboard.html")



@app.route('/appointments')
def appointments():
    cur=mysql.connection.cursor()
    cur.execute("SELECT * FROM  appointments")
    data=cur.fetchall()
    return render_template("appointments.html",data=data)

    return render_template("appointments.html")


@app.route('/tests')
def tests():
    return render_template("tests.html")

@app.route('/otp')
def otp():
    return render_template("otp.html")

@app.route('/profile')
def profile():
    return render_template("profile.html")



@app.route('/doctor',methods=['POST','GET'])
def doctor():
    if request.method=='POST':
        patientname=request.form['patientname']
        email=request.form['email']
        disease=request.form['disease']
        medication=request.form['medication']
        test=request.form['test']
        date=request.form['date']
        time=request.form['time']
    
        cur=mysql.connection.cursor()
        cur.execute("INSERT INTO appointments(patientname,email,disease,medication,test,date,time)VALUES(%s,%s,%s,%s,%s,%s,%s)",(patientname,email,disease,medication,test,date,time))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('appointments'))
    return render_template("doctor.html")



@app.route('/delete/<id>')
def delete(id):
    cur=mysql.connection.cursor()
    cur.execute("SELECT * FROM appointments WHERE id=%s",(id,))
    data=cur.fetchone()
    flash("Data deleted successfully","danger")
    if data:
        email=data[2] 
        msg=Message(subject='Account creation',sender="tobiaskipkogei@gmail.com",recipients=[email])
        msg.body=f"""Thanks for visiting Tobby's Hospital
                        Your have been discharge Today
                        ❤thanks for visiting our health care"""
        mail.send(msg)
        cur.execute("DELETE FROM appointments WHERE id=%s",(id,))
    return redirect(url_for('appointments'))

@app.route('/update/<id>',methods=['POST','GET'])
def update(id):
    if request.method=='POST':
        patientname=request.form['patientname']
        email=request.form['email']
        disease=request.form['disease']
        medication=request.form['medication']
        test=request.form['test']
        date=request.form['date']
        time=request.form['time']
        cur=mysql.connection.cursor()
        cur.execute("UPDATE appointments SET patientname=%s,email=%s,disease=%s,medication=%s,test=%s,date=%s,time=%s WHERE id=%s",(patientname,email,disease,medication,test,date,time,id))
        mysql.connection.commit()
        cur.close
        flash("Data updated successfully","success")
        return redirect(url_for('appointments'))
     
    cur=mysql.connection.cursor()
    cur.execute("SELECT * FROM appointments WHERE id=%s",(id,))
    data=cur.fetchone()
    mysql.connection.commit()
    cur.close()
    return render_template("update.html",update=data)
        
        
if __name__=='__main__':
    app.run(debug=True)