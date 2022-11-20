import ibm_db

from flask import *
from flask_mail import Mail, Message
app = Flask(__name__)
mail = Mail(app) # instantiate the mail class
   
# configuration of mail
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'karthikeyan.b2019@kgkite.ac.in'
app.config['MAIL_PASSWORD'] = '*************'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

donor_vs_patient_compatability = {
    'O+':"('O+','O-')",
    'O-':"('O+','O-')",
    "A+":"('O+','A+','O-','A-')",
    "A-":"('O+','A+','O-','A-')",
    "B+":"('O+','B+','O-','B-')",
    "B-":"('O+','B+','O-','B-')",
    "AB+":"('O+','A+','B+','AB+','O-','A-','B-','AB-')",
    "AB+":"('O+','A+','B+','AB+','O-','A-','B-','AB-')",
}

patient_vs_donor_compatability = {
    "O+":"('O+','A+','B+','AB+','O-','A-','B-','AB-')",
    "O-":"('O+','A+','B+','AB+','O-','A-','B-','AB-')",
    "A+":"('A+','AB+','A-','AB-')",
    "A-":"('A+','AB+','A-','AB-')",
    "B+":"('B+','AB+','B-','AB-')",
    "B-":"('B+','AB+','B-','AB-')",
    "AB+":"('AB+','AB-')",
    "AB-":"('AB+','AB-')",

}


@app.route('/')
def home():
      return render_template('index.html')


@app.route('/sign_up')
def signUp():
      return render_template('sign_up.html')


@app.route('/sign_in')
def signIn():
      return render_template('sign_in.html')


@app.route('/request')
def requests():
      email = request.cookies.get('email')  
      name = request.cookies.get('name') 
      if email != None:
            resp = make_response(render_template('request.html',email = email, name = name, logged_in = True))
      else:
            resp = make_response(render_template('request.html',email = email, name = name, logged_in = False))
      return resp


@app.route('/donor_registration')
def donor_registration():
      email = request.cookies.get('email')  
      name = request.cookies.get('name')
      isDonor = False
      if email != None:
            conn = ibm_db.connect(
                        'DATABASE=bludb;HOSTNAME=b1bc1829-6f45-4cd4-bef4-10cf081900bf.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud;PORT=32304;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=gfn00031;PWD=LITZUQj2tpFc3t0i', '', '')
            sql = 'select * from donors where email='+'\''+email+'\''
            stmt = ibm_db.exec_immediate(conn, sql)
            dictionary = ibm_db.fetch_assoc(stmt)
            isDonor = False

            if dictionary != False:
                  isDonor = True 
      
      if isDonor:
            resp = make_response(render_template('donor_registration.html',email = email, name = name, isDonor = True, logged_in = True))
      elif email != None:
            resp = make_response(render_template('donor_registration.html',email = email, name = name, logged_in = True))
      else:
            resp = make_response(render_template('donor_registration.html',email = email, name = name, logged_in = False))
      return resp





      
@app.route('/add_user', methods=['POST', 'GET'])
def add_user():
    if request.method == 'POST':
        try:
            
            name = request.form['name']
            email = request.form['email']
            password = request.form['pass']
            conn = ibm_db.connect(
                'DATABASE=bludb;HOSTNAME=b1bc1829-6f45-4cd4-bef4-10cf081900bf.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud;PORT=32304;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=gfn00031;PWD=LITZUQj2tpFc3t0i', '', '')
            
            sql = "select * from users where email = "+"'"+email+"'"
            stmt = ibm_db.exec_immediate(conn, sql)
            user = ibm_db.fetch_assoc(stmt)
            if user:
                  msg = "Account already exists"
            else:
                  sql = "insert into users values(?,?,?)"
                  param = name, email, password,
                  stmt = ibm_db.prepare(conn, sql)
                  ibm_db.execute(stmt, param)
                  msg = "You're successfully signed up!"
                  mail_msg = Message(
                  'Welcome to Planor',
                  sender ='karthikeyan.b2019@kgkite.ac.in',
                  recipients = [email]
                  )
                  mail_msg.body = "Hi "+name+" you have successfully signed up into planor."
                  mail.send(mail_msg)
        except Exception as e:
            print("exception occured!",e)
            msg = e

        finally:
            return render_template('post_signup.html', msg = msg)

@app.route('/validate_user',methods = ['POST', 'GET'])
def validate_user():
   if request.method == 'GET':
      try:
            args = request.args
            email = args.get('email')
            password = args.get('password')
   
            conn = ibm_db.connect(
                'DATABASE=bludb;HOSTNAME=b1bc1829-6f45-4cd4-bef4-10cf081900bf.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud;PORT=32304;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=gfn00031;PWD=LITZUQj2tpFc3t0i', '', '')
            sql = 'select * from users where email='+'\''+email+'\''
            stmt = ibm_db.exec_immediate(conn, sql)
            dictionary = ibm_db.fetch_assoc(stmt)
            print("executed")
            print(dictionary)
            if dictionary != False:
                        if(dictionary["PASSWORD"]== password):
                               print("success")
                               resp = make_response(render_template("post_signin.html"))  
                               resp.set_cookie('email', dictionary["EMAIL"]) 
                               resp.set_cookie('name',dictionary["NAME"])  
                               print("success")
                               return resp

                               
                        else:
                              return "Incorrect Password"
            else:
                  return "User does not exists"

      except Exception as e :
         print("error",e)
         return repr(e)


@app.route('/add_donor', methods=['POST', 'GET'])
def add_donor():
    if request.method == 'POST':
        try:
            
            name = request.form['name']
            email = request.form['email']
            blood_group = request.form['blood_group']
            contact_no = request.form['contact_no']
            location = request.form['city']
 
            conn = ibm_db.connect(
                'DATABASE=bludb;HOSTNAME=b1bc1829-6f45-4cd4-bef4-10cf081900bf.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud;PORT=32304;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=gfn00031;PWD=LITZUQj2tpFc3t0i', '', '')
            sql = "insert into donors values(?,?,?,?,?)"
            param = name, email,blood_group,contact_no, location,
            stmt = ibm_db.prepare(conn, sql)
            ibm_db.execute(stmt, param)
            msg = "You're successfully registered as donor"

        except Exception as e:
            print("exception occured!",e)
            msg = e

        finally:
            return render_template('donor_registration_status.html', msg = msg)

@app.route('/create_request', methods=['POST', 'GET'])
def create_request():
    if request.method == 'POST':
        try:
            
            name = request.form['name']
            email = request.form['email']
            blood_group = request.form['blood_group']
            contact_no = request.form['contact_no']
            location = request.form['city']
            request_status =  "Pending"
 
            conn = ibm_db.connect(
                'DATABASE=bludb;HOSTNAME=b1bc1829-6f45-4cd4-bef4-10cf081900bf.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud;PORT=32304;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=gfn00031;PWD=LITZUQj2tpFc3t0i', '', '')
            sql = "insert into requests (name, email, blood_group, contact_no, location, request_status) values(?,?,?,?,?,?)"
            param = name, email,blood_group,contact_no, location, request_status,
            stmt = ibm_db.prepare(conn, sql)
            ibm_db.execute(stmt, param)
            msg = "You're successfully made a request!"


            sql = "select email from donors where blood_group in "+patient_vs_donor_compatability[blood_group]+"and location= "+"'"+location+"'"
            print(sql)
            stmt = ibm_db.exec_immediate(conn, sql)
            donor_mails = []      
            dictionary = ibm_db.fetch_assoc(stmt)
            while dictionary != False:
                  donor_mails.append(dictionary["EMAIL"])
                  dictionary = ibm_db.fetch_assoc(stmt)

            mail_msg = Message(
                'New Plasma Request Received',
                sender ='karthikeyan.b2019@kgkite.ac.in',
                recipients = donor_mails
               )
            mail_msg.body = "Hello, A new request has been received. Kindly check it out!\nRequester mail id: "+email
            mail.send(mail_msg)
        except Exception as e:
            print("exception occured!",e)
            msg = e

        finally:
            return render_template('donor_registration_status.html', msg = msg)

            
@app.route('/accept_request', methods=['POST', 'GET'])
def accept_request():
    if request.method == 'POST':
        try:
            
            id = request.form['id']
            email = request.cookies.get('email')
            conn = ibm_db.connect(
                'DATABASE=bludb;HOSTNAME=b1bc1829-6f45-4cd4-bef4-10cf081900bf.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud;PORT=32304;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=gfn00031;PWD=LITZUQj2tpFc3t0i', '', '')
            sql = "update requests set request_status = 'Accepted' , accepted_by ="+"'"+email+"'"+"where id ="+"'"+id+"'"
            stmt = ibm_db.exec_immediate(conn, sql)

            #retrieving recipient contact details
            sql = 'select * from requests where id='+'\''+id+'\''
            stmt = ibm_db.exec_immediate(conn, sql)
            recipient_details = ibm_db.fetch_assoc(stmt)

            #retrieving donor contact details
            sql = 'select * from donors where email='+'\''+email+'\''
            stmt = ibm_db.exec_immediate(conn, sql)
            donor_details = ibm_db.fetch_assoc(stmt)


            mail_msg = Message(
                'Request Accpeted',
                sender ='karthikeyan.b',
                recipients = [recipient_details["EMAIL"]]
               )
            mail_msg.body = "Hi "+recipient_details["NAME"]+" you request has been accepted by "+donor_details["NAME"]+" \nContact Details:\nEmail: "+donor_details["EMAIL"]+"\nContact No.: "+donor_details["CONTACT_NO"]
            mail.send(mail_msg)


            mail_msg = Message(
                'Recipient Details',
                sender ='19eucs180@skcet.ac.in',
                recipients = [donor_details["EMAIL"]]
               )
            mail_msg.body = "Hi "+donor_details["NAME"]+". Request ID: "+id+" has been accepted by you\nContact Details of the recipient:\nName: "+recipient_details["NAME"]+"\nEmail: "+recipient_details["EMAIL"]+"\nContact No.: "+recipient_details["CONTACT_NO"]
            mail.send(mail_msg)

            

        except Exception as e:
            print("exception occured!",e)

        finally:
            return redirect(url_for('profile'))

@app.route('/profile')
def profile():
      email = request.cookies.get('email')  
      name = request.cookies.get('name') 
      if email != None:
            conn = ibm_db.connect(
                  'DATABASE=bludb;HOSTNAME=b1bc1829-6f45-4cd4-bef4-10cf081900bf.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud;PORT=32304;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=gfn00031;PWD=LITZUQj2tpFc3t0i', '', '')
            sql = 'select * from requests where email='+'\''+email+'\''
            stmt = ibm_db.exec_immediate(conn, sql)
            requests = []
            dictionary = ibm_db.fetch_assoc(stmt)
            
            while dictionary != False:
                  print(dictionary["ID"])
                  requests.append(dictionary)
                  dictionary = ibm_db.fetch_assoc(stmt)
            print(requests)

            sql = 'select * from donors where email='+'\''+email+'\''
            stmt = ibm_db.exec_immediate(conn, sql)
            dictionary = ibm_db.fetch_assoc(stmt)
            isDonor = False
            pending_requests = []
            if dictionary != False:
                  isDonor = True
                  donor_location = dictionary["LOCATION"]
                  donor_bloodgroup = dictionary["BLOOD_GROUP"]
                  sql = "select * from requests where blood_group="+"'"+donor_bloodgroup+"'"+"and location= "+"'"+donor_location+"'"+"and request_status= "+"'Pending'"
                  stmt = ibm_db.exec_immediate(conn, sql)
                  
                  dictionary = ibm_db.fetch_assoc(stmt)
                  while dictionary != False:
                        pending_requests.append(dictionary)
                        dictionary = ibm_db.fetch_assoc(stmt)
                  print(pending_requests)

            accepted_requests= []
            if isDonor:
                  sql = 'select * from requests where accepted_by='+'\''+email+'\''
                  stmt = ibm_db.exec_immediate(conn, sql)
                  dictionary = ibm_db.fetch_assoc(stmt)
                  
                  while dictionary != False:
                        accepted_requests.append(dictionary)
                        dictionary = ibm_db.fetch_assoc(stmt)
                  print(accepted_requests)
            return render_template('profile.html', name =name, email = email,requests_len = len(requests) ,requests = requests, pending_requestslen = len(pending_requests), pending_requests = pending_requests, accepted_requestslen = len(accepted_requests), accepted_requests = accepted_requests, logged_in=True)

      else:
            return render_template('profile.html', logged_in= False)

@app.route('/stats')
def stats():

            conn = ibm_db.connect(
                        'DATABASE=bludb;HOSTNAME=b1bc1829-6f45-4cd4-bef4-10cf081900bf.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud;PORT=32304;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=gfn00031;PWD=LITZUQj2tpFc3t0i', '', '')
            sql = 'select count(email) from donors'
            stmt = ibm_db.exec_immediate(conn, sql)
            donors= ibm_db.fetch_assoc(stmt)["1"]

            sql = "select count(email) from requests where request_status = 'Pending'"
            stmt = ibm_db.exec_immediate(conn, sql)
            pending_requests= ibm_db.fetch_assoc(stmt)["1"]

            sql = "select count(email) from requests where request_status = 'Accepted'"
            stmt = ibm_db.exec_immediate(conn, sql)
            accepted_requests= ibm_db.fetch_assoc(stmt)["1"]
            return render_template('stats.html', donors = donors, pending_requests = pending_requests, accepted_requests = accepted_requests)



@app.route('/logout')  
def logout():  
      
      email = request.cookies.get('email')
      if email != None:
            resp = make_response(render_template('logout.html',loggedin = True))
            resp.set_cookie('name', '', expires=0)
            resp.set_cookie('email', '', expires=0)
            
      else:
            resp = make_response(render_template('logout.html',loggedin = False))

      return resp




if __name__ == '__main__':
      app.run(debug=True)
