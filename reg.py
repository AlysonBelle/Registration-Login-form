from flask import Flask, render_template, request, session, flash, url_for, redirect
from flask_wtf import Form
from wtforms import TextField, SubmitField, SelectField, validators, PasswordField
from flask_sqlalchemy import SQLAlchemy 
import os
from sqlalchemy import update
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


app 							= Flask(__name__)
app.config['SECRET_KEY']		= 'ASDFIJKL'
db 								= SQLAlchemy(app)
migrate 						= Migrate(app, db)


basedir 						= os.path.abspath(os.path.dirname(__file__))



class Config(object):
	SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
	SQLALCHEMY_TRACK_MODIFICATION = False 



app.config.from_object(Config)
db 								= SQLAlchemy(app)
migrate 						= Migrate(app, db)

login_user 						= None
summary 						= None

class RegForm(Form):
	first_name		= TextField('First Name', [validators.DataRequired('Please provide your first name')])
	last_name		= TextField('Last Name', [validators.DataRequired('Please provide your surname')])
	email			= TextField('Email', [validators.DataRequired('Please submit a valid email address'), validators.Email()])
	password 		= PasswordField('Password', [validators.DataRequired(), validators.EqualTo('confirm', message="Passwords Must Match")])
	confirm 		= PasswordField('Repeat Password')
	submit 			= SubmitField('Register')

class LogForm(Form):
	email 			= TextField('Email', [validators.DataRequired('Please enter your email address'), validators.Email()])
	password 		= PasswordField('Password', [validators.DataRequired('Please enter your password')])
	login			= SubmitField('Login')

class SubmitButton(Form):
	save 			= SubmitField('Save')




class User(db.Model):
	id 				= db.Column(db.Integer, primary_key=True)
	first_name 		= db.Column(db.String(64), index=True)
	last_name		= db.Column(db.String(64), index=True)
	email 			= db.Column(db.String(120), index=True, unique=True)
	password_hash 	= db.Column(db.String(120))
	first_time	 	= db.Column(db.Integer)

	profile_foreign_key 	= db.Column(db.Integer, db.ForeignKey('profile.id'))
	bot_key 				= db.Column(db.Integer, db.ForeignKey('bot.id'))

	profile 		= db.relationship('Profile', foreign_keys=[profile_foreign_key])
	bot 			= db.relationship('Bot', foreign_keys=[bot_key])

	def __str__(self):
		return 'first name : ' + self.first_name + ' last_name : ' + self.last_name + ' email : ' + self.email



class Profile(db.Model):
	id 				= db.Column(db.Integer, primary_key=True)
	email 			= db.Column(db.String(120))
	profile_pic		= db.Column(db.String(120), index=True)
	summary 		= db.Column(db.String(240))


class Bot(db.Model):
	id 				= db.Column(db.Integer, primary_key=True)
	email 			= db.Column(db.String(120))
	work 			= db.Column(db.String(2000))
	interests 		= db.Column(db.String(2000))






def check_if_valid_user(form):
	users = User.query.all()

	for user in users:
		if form.email.data == user.email and form.password.data == user.password_hash:
			return True
	return False



@app.route('/user_profile', methods=['GET', 'POST'])
def user_profile():
	if 'username' not in session:
		return redirect(url_for('login'))
	user_info = User.query.filter(User.email == session['username'])
	for user in user_info:
		if user.email == session['username']:
			login_user = user 
			summary = login_user.profile.query.all()
			break 
	return render_template('profile.html', 
		first_name=login_user.first_name,
		last_name=login_user.last_name,
		summary=summary[0].summary
	)



@app.route('/login', methods=['GET', 'POST'])
def login():
	form 			= LogForm()
	doesnt_exist 	= ''
	global login_user
	global summary

	if login_user != None:
		return render_template('profile.html',
					first_name=login_user.first_name,
					last_name=login_user.last_name,
					summary=summary[0].summary
			)
	if request.method == 'POST' and form.validate():
		if check_if_valid_user(form) == True:
			session['username'] = form.email.data
			return redirect(url_for('home'))
		else:
			doesnt_exist = 'Email or password is incorrect'
	return render_template('login.html', form=form, doesnt_exist=doesnt_exist)




def does_user_exist(email):
	all_users = User.query.all()

	for user in all_users:
		if (user.email == email):
			return False
	return True


@app.route('/logout', methods=['GET', 'POST'])
def logout():
	global login_user
	global summary

	login_user		= None
	summary	 		= None
	session.pop('username', None)
	return render_template('logout.html')


@app.route('/edit-profile', methods=['GET', 'POST'])
def edit_profile():
	SaveButton 		= SubmitButton()
	users 			= User.query.all()
	user_profile 	= None

	for user in users:
		if session['username'] == user.email:
			print('here')
			user_profile = user.profile.query.all()
			break 	

	if request.method == 'POST' and SaveButton.validate_on_submit():
		message = request.form['texta']
		print('Message printed is ', message)
		# add sql update
	print('summar is ', user_profile[0].summary)
	return render_template('edit_profile.html', 
			form=SaveButton,
			summary=user_profile[0].summary)



@app.route("/register", methods=['GET', 'POST'])
def register():
	form 	= RegForm()
	doesnt_exist = ''

	if form.validate_on_submit():
		print('IT WORKED!')
		if does_user_exist(form.email.data) == True:
			newUser = User(
				first_name=form.first_name.data,
				last_name=form.last_name.data,
				email=form.email.data,
				password_hash=form.password.data,
				first_time=0)
			db.session.add(newUser)
			db.session.commit()
			newUser.profile = Profile(summary='None', email=form.email.data)
			db.session.add(newUser.profile)
			db.session.commit()
			print('Commit successful')
			return render_template(url_for('login'))
	else:
		print('You did nothing!')
	return render_template('register.html', form=form)



@app.route('/')
def home():
	return render_template('home.html', session=session)


if __name__ == '__main__':
	app.run()











