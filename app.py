from operator import add
from re import A
from flask import Flask, render_template, url_for , request, redirect , session, g
from flask.helpers import send_file
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_mail import Mail,Message
# from flask.ext.session import Session
from datetime import datetime
from sqlalchemy.orm import backref
from io import BytesIO

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///recruitment1.db'
app.static_folder = 'static'
app.config['SECRET_KEY']= '185001112'
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'edhukkuindhamail@gmail.com'
app.config['MAIL_PASSWORD'] = 'Dummyp@ssw0rd'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
db = SQLAlchemy(app)
mail = Mail(app)
ma = Marshmallow(app)

class Resume(db.Model):
    __tablename__='resume'
    id = db.Column(db.Integer,primary_key=True)
    filename = db.Column(db.String(30))
    data = db.Column(db.LargeBinary)
    user = db.relationship("Applicant", backref=backref("user", uselist=False))

class Applicant(db.Model):
    __tablename__ = 'applicant'
    id = db.Column(db.Integer,primary_key=True)
    Name = db.Column(db.String(50),nullable=False)
    Password = db.Column(db.String(50),nullable=False)
    Email_id = db.Column(db.String(200),nullable=False)
    Contact = db.Column(db.String(15))
    Address = db.Column(db.String(30))
    Education = db.Column(db.String(30))
    Specialization = db.Column(db.String(30))
    College = db.Column(db.String(200))
    CGPA = db.Column(db.Float)
    resume_id = db.Column(db.Integer,db.ForeignKey( 'resume.id'))

class Company(db.Model):
    __tablename__ = 'company'
    id = db.Column(db.Integer,primary_key=True)
    Name = db.Column(db.String(50),nullable=False)
    Password = db.Column(db.String(50),nullable=False)
    Email_id = db.Column(db.String(200),nullable=False)
    Contact = db.Column(db.String(15))
    Address = db.Column(db.String(30))
    Domain = db.Column(db.String(30))
    Jobs = db.relationship('Job', backref=backref("company", uselist=False),lazy=True)

class Job(db.Model):
    __tablename__ = 'job'
    id = db.Column(db.Integer,primary_key=True)
    job_name = db.Column(db.String(50),nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    last_date = db.Column(db.DateTime)
    job_role = db.Column(db.String(50),nullable=False)
    skills_required = db.Column(db.String(100),nullable=False)
    experience = db.Column(db.Integer)
    salary = db.Column(db.Integer)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'),nullable=False)

class Help(db.Model):
    __tablename__= 'help'
    id = db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(50),nullable=False)
    issue = db.Column(db.String(100),nullable=False)

applied = db.Table('applied',
    db.Column('job_id', db.Integer, db.ForeignKey('job.id'), primary_key=True),
    db.Column('applicant_id', db.Integer, db.ForeignKey('applicant.id'), primary_key=True),
    db.Column('reason',default='None')
)

@app.before_first_request
def before_first_request():
    session['type']=0
    session['user']=0
    session['msg']=''

@app.before_request
def before_request():
    # g.user=session['user']
    if session.get('type') is not None:
        type=session['type']
        id=session['user']
        if type==1:
            g.user = Applicant.query.filter_by(id=id).first()
            # if g.user:
            #     print(g.user.id)
            # else:
            #     print("no user",type,id)
        elif type==2:
            g.user = Company.query.filter_by(id=id).first()
            # if g.user:
            #     print(g.user.id)
            # else:
            #     print("no user")
    else:
        session['type']=0
        session['user']=0
        return redirect(url_for("login",error="Session Timed Out. Login again"))

@app.route('/', methods=['POST', 'GET'])
def index():
    return render_template('index.html')

@app.route('/logout', methods=['POST', 'GET'])
def logout():
    session['type']=0
    return redirect("/login")

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['uname']
        passwd = request.form['passwd']
        selectapplicant = Applicant.query.filter_by(Email_id=username).first()
        selectcompany = Company.query.filter_by(Email_id=username).first()
        if selectapplicant and selectapplicant.Password == passwd:
            # session['user']=selectapplicant
            # print(session['user'])
            session['type']=1
            session['user']=selectapplicant.id
            session['msg']='LOGGED IN SUCCESSFULLY'
            return redirect(url_for('student'))
        elif selectcompany and selectcompany.Password == passwd:
            # session['user']=selectcompany
            # print(session['user'])
            session['type']=2
            session['user']=selectcompany.id
            return redirect('/company')
        elif username == 'helpdesk@helpdesk.com' and passwd == '1234':
            session['type']=3
            session['user']=1
            return redirect('/helpdesk')
        else:
            error = "User with Given Credentials not found"
            return render_template('login.html',error=error)
    else:
        if session['type']!=0:
            type=session['type']
            id=session['user']
            if type==1:
                g.user = Applicant.query.filter_by(id=id).first()
                session['msg']='LOGGED IN SUCCESSFULLY'
                return redirect(url_for('student'))
            elif type==2:
                g.user = Company.query.filter_by(id=id).first()
                return redirect('/company')
            
        return render_template('login.html',error=None)

@app.route('/student', methods=['POST', 'GET'])
def student():
    if request.method == 'POST':
        job=request.form['job']
        location = request.form['location']
        position = request.form['position']
        companyname = request.form['company']
        query1 = Job.query
        if job != "":
            query1 = query1.filter_by(job_name=job)
        if location != "":
            selected = Company.query.filter_by(Address=location)
            sel_id=[]
            for i in selected:
                sel_id.append(i.id)
            query1 = query1.filter(Job.company_id.in_(sel_id))
        if position != "":
            query1 = query1.filter_by(job_role=position)
        if companyname != "":
            selected = Company.query.filter_by(Name=companyname).all()
            sel_id=[]
            for i in selected:
                sel_id.append(i.id)
            query1 = query1.filter(Job.company_id.in_(sel_id))
        sel_id1=db.session.execute("SELECT job_id from 'applied' WHERE applicant_id = :appid",{'appid':session['user']}).fetchall()
        # print(sel_id1)
        sel_id2=[]
        if not sel_id1:
            pass
        else:
            for i in sel_id1:
                sel_id2.append(i[0])
            query1 = query1.filter(Job.id.notin_(sel_id2))
        jobs=query1.all()
        session['msg']='FILTERED SUCCESSFULLY'
        return render_template('jobsearch.html',jobs=jobs,msg=session['msg'])
        
    else:
        sel_id1=db.session.execute("SELECT job_id from 'applied' WHERE applicant_id = :appid",{'appid':session['user']}).fetchall()
        sel_id2=[]
        # print(sel_id1)
        if not sel_id1:
            # print("in")
            jobs=Job.query.all()
        else:
            for i in sel_id1:
                sel_id2.append(i[0])
            jobs=Job.query.filter(Job.id.notin_(sel_id2)).all()
        # print(jobs)
        return render_template('jobsearch.html',jobs=jobs,msg=session['msg'])

@app.route('/helpdesk', methods=['POST', 'GET'])
def helpdesk():
    queries = Help.query.all()
    return render_template('viewqueries.html',queries=queries)



@app.route('/company', methods=['POST', 'GET'])
def company():
    jobs=Job.query.filter_by(company=Company.query.filter_by(id=session['user']).first()).all()
    return render_template('jobcreate.html',jobs=jobs)

@app.route('/createjob', methods=['GET','POST'])
def createjob():
    if request.method == "POST":
        company = Company.query.filter_by(id=session['user']).first()
        job_name = request.form['name']
        role = request.form['role']
        exp = int(request.form['exp'])
        date = datetime.strptime(request.form['date'],"%Y-%m-%d")
        skill = request.form['skill']
        sal = int(request.form['sal'])
        job = Job(job_name=job_name,job_role=role,last_date=date,skills_required=skill,salary=sal,company=company,experience=exp)
        try:
            db.session.add(job)
            db.session.commit()
        except Exception as e:
            return("error")
        return redirect('/company')
    else:
        return render_template('createnewjob.html')

@app.route('/upload', methods=['POST', 'GET'])
def upload():
    if request.method == 'POST':
        file = request.files['myfile']
        resume = Resume(filename=file.filename,data=file.read())
        try:
            db.session.add(resume)
            db.session.commit()
        except:
            return "error adding values to database"
        return redirect('/')
    else:
        return render_template('a.html')

@app.route('/studentsignup', methods=['POST', 'GET'])
def studentsignup():
    if request.method == 'POST':
        fname = request.form['fname']
        lname = request.form['lname']
        name = fname + lname
        passwd = request.form['password']
        email = request.form['email']
        contact = request.form['contact']
        address = request.form['address']
        clg = request.form['clg']
        spec = request.form['spec']
        degree = request.form['degree']
        cgpa = request.form['cgpa']
        file = request.files['myfile']
        resume = Resume(filename=file.filename,data=file.read())
        aspirant = Applicant(Name=name,Password=passwd,Email_id=email,Contact=contact,Address=address,Education=degree,Specialization=spec,College=clg,CGPA=cgpa,user=resume)
        try:
            db.session.add(resume)
            db.session.add(aspirant)
            db.session.commit()
        except:
            return "error adding values to database"
        error = "Signed Up Successfully"
        return render_template('login.html',error=error)

    else:
        return render_template('studentsignup.html')

@app.route('/update', methods=['POST', 'GET'])
def update():
    if request.method == 'POST':
        if session['type']==1:
            name = request.form['fname']
            passwd = request.form['password']
            email = request.form['email']
            contact = request.form['contact']
            address = request.form['address']
            clg = request.form['clg']
            spec = request.form['spec']
            degree = request.form['degree']
            cgpa = request.form['cgpa']
            aspirant = Applicant.query.filter_by(id=session['user']).first()
            aspirant.Name = name
            aspirant.Password = passwd
            aspirant.Email_id = email
            aspirant.Contact = contact
            aspirant.Address = address
            aspirant.College = clg
            aspirant.Specialization = spec
            aspirant.Education = degree
            aspirant.CGPA = cgpa
            try:
                db.session.commit()
            except:
                return "error adding values to database"
            session['msg']='UPDATED SUCCESSFULLY'
            return redirect(url_for('student'))
        elif session['type'] == 2:
            name = request.form['name']
            passwd = request.form['password']
            email = request.form['email']
            contact = request.form['contact']
            address = request.form['address']
            domain = request.form['domain']
            company = Company.query.filter_by(id=session['user']).first()
            company.Name = name
            company.Password = passwd
            company.Email_id = email
            company.Contact = contact
            company.Address = address
            company.DOmain = domain
            try:
                db.session.commit()
            except:
                return "error adding values to database"
            return redirect('/company')
        elif session['type']== 3:
            return redirect('/helpdesk')
        else:
            return redirect('/')
    else:
        if session['type']==1:
            return render_template('studentupdate.html')
        elif session['type']==2:
            return render_template('companyupdate.html')
        else:
            return redirect('/')

@app.route('/helpquery', methods=['POST', 'GET'])
def helpquery():
    if session['type']==2:
        user = Company.query.filter_by(id=session['user']).first()
    elif session['type']==1:
        user = Applicant.query.filter_by(id=session['user']).first()
    statement = request.form['review']
    help = Help(username=user.Name,issue=statement)
    try:
        db.session.add(help)
        db.session.commit()
    except:
        return "Error adding to the database"
    if session['type']==1:
        session['msg']="QUERY SENT"
        return redirect(url_for('student'))
    elif session['type']==2:
        return redirect('/company')
    else:
        return redirect('/login')

@app.route('/companysignup', methods=['POST', 'GET'])
def companysignup():
    if request.method == 'POST':
        name = request.form['name']
        passwd = request.form['password']
        email = request.form['email']
        contact = request.form['contact']
        address = request.form['address']
        domain = request.form['domain']
        company = Company(Name=name,Password=passwd,Email_id=email,Contact=contact,Address=address,Domain = domain)
        try:
            db.session.add(company)
            db.session.commit()
        except:
            return "error adding values to database"
        error = "Signed Up Successfully"
        return render_template('login.html',error=error)

    else:
        return render_template('companysignup.html')

@app.route('/apply', methods=['POST', 'GET'])
def apply():
    id=request.form['id']
    reason = request.form['reas']
    d={"jid":id,"aid":session['user'],"reason":reason}
    db.session.execute('INSERT INTO "applied" ("job_id", "applicant_id", "reason") VALUES ( :jid , :aid, :reason)',d)
    db.session.commit()
    session['msg']='APPLIED SUCCESSFULLY'
    return redirect(url_for('student'))

@app.route('/seeapplicants/<int:id>', methods=['POST', 'GET'])
def seeapplicants(id):
    sel_id=db.session.execute("SELECT applicant_id,reason from 'applied' WHERE job_id= :jobid",{'jobid':id}).fetchall()
    sel=[]
    reason=[]
    job=Job.query.filter_by(id=id).first()
    for sid in sel_id:
        sel.append(sid[0])
        reason.append(sid[1])
    students=Applicant.query.filter(Applicant.id.in_(sel)).all()
    temp=0
    reason1=[]
    for i in students:
        reason1.append({'r':reason[sel.index(i.id)],'j':i})
    return render_template('viewstudents.html',job=job,reason=reason1)

@app.route('/results/<int:choice>/<int:id>/<int:stid>', methods=['POST', 'GET'])
def results(choice,id,stid):
    job=Job.query.filter_by(id=id).first()
    stud=Applicant.query.filter_by(id=stid).first()
    msg = Message(
                'Recruitement System : Results',
                sender ='edhukkuindhamail@gmail.com',
                recipients = [stud.Email_id]
               )
    if(choice==0):
        msg.body="Hello "+stud.Name+",\nYou have been selected for the job "+job.job_name+" with Salary of "+str(job.salary)+" LPA in the company "+job.company.Name+".\nContact the Company using mail "+job.company.Email_id+" for more  details"
    else:
        msg.body="Hello "+stud.Name+",\nYou have been rejected for the job "+job.job_name+" in the company "+job.company.Name+".\nBetter Luck next time."
    mail.send(msg)
    db.session.execute("DELETE FROM 'applied' WHERE job_id= :id AND applicant_id= :stid",{'id':id,'stid':stid})
    db.session.commit()
    return redirect(url_for("seeapplicants",id=id))

@app.route('/delete/<int:id>', methods=['POST', 'GET'])
def delete(id):
    stid=session['user']
    print(id,stid)
    db.session.execute("DELETE FROM 'applied' WHERE job_id= :id AND applicant_id= :stid",{'id':id,'stid':stid})
    db.session.commit()
    return redirect('/status')

@app.route('/status', methods=['POST', 'GET'])
def status():
    sel_id1=db.session.execute("SELECT job_id from 'applied' WHERE applicant_id = :appid",{'appid':session['user']}).fetchall()
    sel_id2=[]
    for i in sel_id1:
        sel_id2.append(i[0])
    jobs=Job.query.filter(Job.id.in_(sel_id2)).all()
    return render_template('appliedstatus.html',jobs=jobs)

@app.route('/download/<int:id>', methods=['POST', 'GET'])
def download(id):
    data = Applicant.query.filter_by(id=id).first()
    return send_file(BytesIO(data.user.data),attachment_filename="{}-Resume.pdf".format(data.Name),as_attachment=True)

@app.route('/resolve/<id>', methods=['POST', 'GET'])
def resolve(id):
    task_to_delete = Help.query.get(id)

    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/helpdesk')
    except:
        return 'There was a problem deleting that task'

if __name__ == "__main__":
    app.run(debug=True)

# def index():
    # if request.method == 'POST':
    #     task_content = request.form['content']
    #     new_task = Todo(content=task_content)

    #     try:
    #         db.session.add(new_task)
    #         db.session.commit()
    #         return redirect('/')
    #     except:
    #         return 'There was an issue adding your task'

    # else:
    #     tasks = Todo.query.order_by(Todo.date_created).all()


# @app.route('/update/<int:id>', methods=['GET', 'POST'])
# def update(id):
#     task = Todo.query.get_or_404(id)

#     if request.method == 'POST':
#         task.content = request.form['content']

#         try:
#             db.session.commit()
#             return redirect('/')
#         except:
#             return 'There was an issue updating your task'

#     else:
#         return render_template('update.html', task=task)