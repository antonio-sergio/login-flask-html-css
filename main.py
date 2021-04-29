import os
from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = '05c31152d33d28330bfd6cdfb5ee36e2'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
db = SQLAlchemy(app)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    price = db.Column(db.String(10))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class User(db.Model):
 id = db.Column(db.Integer, primary_key=True)
 name = db.Column(db.String(1000))
 email = db.Column(db.String(100), unique=True)
 password = db.Column(db.String(100))

@app.route('/')
def index():
  if 'user_id' not in session:
    return redirect('/login')
  user_id = session['user_id']
  products = Product.query.filter_by(user_id=user_id).all()
  return render_template('index.html', products=products)

@app.route('/login')
def login():
 return render_template('login.html')

@app.route('/signin', methods=['POST'])
def signin():
  email = request.form.get('email')
  password = request.form.get('password')

  user = User.query.filter_by(email=email).first()
  if not user or not check_password_hash(user.password, password):
    return redirect('/login')
  session['user_id'] = user.id
  return redirect('/')

@app.route('/signup', methods=['POST'])
def signup():
  name = request.form.get('name')
  email = request.form.get('email')
  password = request.form.get('password')
  user = User.query.filter_by(email=email).first()
  if user:
    return redirect('/register')

  new_user = User(
    email=email, name=name,
    password=generate_password_hash(password, method='sha256')
    )
  db.session.add(new_user)
  db.session.commit()
  return redirect('/login')

@app.route('/register')
def register():
 return render_template('register.html')

@app.route('/logout')
def logout():
 if 'user_id' in session:
   session.pop('user_id', None)
 return redirect('/')


@app.route('/create', methods=['POST'])
def create():
  if 'user_id' not in session:
      return redirect('/login')
  user_id = session['user_id']

  title = request.form.get('title')
  price = request.form.get('price')
  new_product = Product(title=title, price=price,user_id=user_id)
  db.session.add(new_product)
  db.session.commit()
  return redirect('/')


@app.route('/delete/<int:id>')
def delete(id):
    if 'user_id' not in session:
      return redirect('/login')

    product = Product.query.filter_by(id=id).first()
    db.session.delete(product)
    db.session.commit()
    return redirect('/')


@app.route('/update/<int:id>', methods=['POST'])
def update(id):
    if 'user_id' not in session:
      return redirect('/login')

    title = request.form.get('title')
    product = Product.query.filter_by(id=id).first()
    product.title = title
    db.session.commit()
    return redirect('/')





if __name__ == ("__main__"):
    db.create_all()
    port = int(os.environ.get('PORT', 5000))
    app.run(host="0.0.0.0", port = port)
