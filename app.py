from flask import Flask, render_template, request, redirect, flash, session, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import json
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key' 

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    score = db.Column(db.Integer, nullable=False, default=0)


@app.route('/')
def index():
    if 'user_id' in session:
        user_id = session['user_id']
        user = User.query.get(user_id)
        if user:
            return render_template('index.html', username=user.username, score=user.score)
    return redirect(url_for('login'))

@app.route('/saveGameData', methods=['POST'])
def save_game_data():
    game_data = request.json
    with open('game_data.json', 'a') as f:
        json.dump(game_data, f)
        f.write('\n')
    return jsonify({'status': 'success', 'message': 'Game data saved successfully'}), 200

@app.route('/setScore', methods=['POST'])
def save_score():
    if 'user_id' in session:
        user_id = session['user_id']
        user = User.query.get(user_id)
        if user:
            score = request.form.get('score')
            if score:
                user.score = score
                db.session.commit()
    return redirect(url_for('index'))

@app.route('/getScore', methods=['GET'])
def get_score():
    if 'user_id' in session:
        user_id = session['user_id']
        user = User.query.get(user_id)
        if user:
            score = user.score
            return jsonify({'score': score})
    return jsonify({'error': 'Score not found'})

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            return redirect('/')
        else:
            flash('Invalid username or password', 'error')
            return redirect('/login') 
    else:
        return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists. Please choose a different username.', 'error')
            return redirect('/register')

        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password)

        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful. You can now log in.', 'success')
        return redirect('/')
    else:
        return render_template('newuser.html')

@app.route('/users')
def users():
    users = User.query.all()
    return render_template('user.html', users=users)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
