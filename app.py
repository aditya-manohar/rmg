from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os

app = Flask(__name__)
if 'DATABASE_URL' in os.environ:
    # Use the Heroku-provided Postgres URL
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
else:
    # Use local SQLite database in 'instance' folder for development
    db_path = os.path.join(os.getcwd(), 'instance', 'data.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 
db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    traits = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f'<Submission {self.name}>'
    
class Leaderboard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    rank = db.Column(db.Integer, nullable=False)
    qualities = db.Column(db.String(500), nullable=True)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    if request.method == 'POST':
        name = request.form['name']
        traits = request.form['traits']
        
        new_submission = Submission(name=name, traits=traits)
        db.session.add(new_submission)
        db.session.commit()

        return redirect(url_for('leaderboard')) 

@app.route('/update_leaderboard', methods=['GET', 'POST'])
def update_leaderboard():
    if request.method == 'POST':
        entry_id = request.form.get('id')
        name = request.form['name']
        rank = request.form['rank']  
        qualities = request.form['qualities']

        if entry_id: 
            entry = Leaderboard.query.get(entry_id)
            entry.name = name
            entry.rank = rank  
            entry.qualities = qualities
            db.session.commit()
        else:  # Add new entry
            new_entry = Leaderboard(name=name, rank=rank, qualities=qualities)
            db.session.add(new_entry)
            db.session.commit()

        return redirect(url_for('leaderboard'))

    leaderboard_entries = Leaderboard.query.all()
    return render_template('update_leaderboard.html', leaderboard=leaderboard_entries)



@app.route('/delete_leaderboard/<int:id>', methods=['GET'])
def delete_leaderboard(id):
    entry = Leaderboard.query.get(id)
    db.session.delete(entry)
    db.session.commit()
    return redirect(url_for('leaderboard'))


@app.route('/leaderboard')
def leaderboard():
    leaderboard_data = Leaderboard.query.order_by(Leaderboard.rank).all()
    return render_template('leaderboard.html', leaderboard=leaderboard_data)

@app.route('/submissions')
def submissions():
    submissions = Submission.query.all()  
    return render_template('submissions.html', submissions=submissions)

@app.route('/delete_submission/<int:id>', methods=['GET'])
def delete_submission(id):
    # Find the submission by ID
    submission = Submission.query.get(id)
    
    if submission:
        # Delete the submission from the database
        db.session.delete(submission)
        db.session.commit()
    
    # Redirect to the submissions page
    return redirect(url_for('submissions'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
