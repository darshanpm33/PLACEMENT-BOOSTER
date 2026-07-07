from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
import random
import json
from datetime import datetime, date

app = Flask(__name__)
app.config['SECRET_KEY'] = 'placement_booster_ultra_secret_2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///placement_booster.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ─── Database Models ──────────────────────────────────────────────────────────

class User(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    username    = db.Column(db.String(50), unique=True, nullable=False)
    email       = db.Column(db.String(120), unique=True, nullable=False)
    password    = db.Column(db.String(200), nullable=False)
    points      = db.Column(db.Integer, default=0)
    streak      = db.Column(db.Integer, default=0)
    last_active = db.Column(db.Date, default=date.today)
    joined_on   = db.Column(db.DateTime, default=datetime.utcnow)

class TestRecord(db.Model):
    id      = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    score   = db.Column(db.Integer, nullable=False)
    total   = db.Column(db.Integer, nullable=False)
    results_json = db.Column(db.Text) # Stores detailed list of {question, user_ans, correct_ans, is_correct, explanation}
    date    = db.Column(db.DateTime, default=datetime.utcnow)
    user    = db.relationship('User', backref=db.backref('records', lazy=True))

class AptitudeQuestion(db.Model):
    id             = db.Column(db.Integer, primary_key=True)
    question       = db.Column(db.String(500), nullable=False)
    option_a       = db.Column(db.String(200), nullable=False)
    option_b       = db.Column(db.String(200), nullable=False)
    option_c       = db.Column(db.String(200), nullable=False)
    option_d       = db.Column(db.String(200), nullable=False)
    correct_option = db.Column(db.String(1), nullable=False)
    explanation    = db.Column(db.String(500))
    category       = db.Column(db.String(50), default='General')

class CodingQuestion(db.Model):
    id            = db.Column(db.Integer, primary_key=True)
    title         = db.Column(db.String(100), nullable=False)
    description   = db.Column(db.Text, nullable=False)
    sample_answer = db.Column(db.Text, nullable=False)
    difficulty    = db.Column(db.String(20), default='Easy')
    language      = db.Column(db.String(30), default='Python')

class HRQuestion(db.Model):
    id               = db.Column(db.Integer, primary_key=True)
    question         = db.Column(db.String(500), nullable=False)
    suggested_answer = db.Column(db.Text, nullable=False)
    category         = db.Column(db.String(50), default='General')

class AptitudeConcept(db.Model):
    id        = db.Column(db.Integer, primary_key=True)
    category  = db.Column(db.String(100), nullable=False)
    topic     = db.Column(db.String(100), nullable=False)
    theory    = db.Column(db.Text, nullable=False)
    formulas  = db.Column(db.Text) # JSON string array
    examples  = db.Column(db.Text)

class CompletedCoding(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('coding_question.id'), nullable=False)
    date        = db.Column(db.DateTime, default=datetime.utcnow)

class DailyTip(db.Model):
    id      = db.Column(db.Integer, primary_key=True)
    tip     = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50))

# ─── Database Seeder ──────────────────────────────────────────────────────────

def init_db():
    with app.app_context():
        db.create_all()

        seed_file = 'data/seed.json'
        
        if os.path.exists(seed_file):
            with open(seed_file, 'r') as f:
                seed_data = json.load(f)
                
            if not AptitudeConcept.query.first():
                concepts = []
                for c in seed_data.get('concepts', []):
                    concepts.append(AptitudeConcept(
                        category=c['category'],
                        topic=c['topic'],
                        theory=c['theory'],
                        formulas=json.dumps(c.get('formulas', [])),
                        examples=c['examples']
                    ))
                db.session.add_all(concepts)

            if not AptitudeQuestion.query.first():
                questions = []
                for q in seed_data.get('aptitude', []):
                    questions.append(AptitudeQuestion(
                        question=q['q'], option_a=q['a'], option_b=q['b'], option_c=q['c'], option_d=q['d'],
                        correct_option=q['c_opt'], explanation=q['exp'], category=q['cat']
                    ))
                db.session.add_all(questions)

            if not CodingQuestion.query.first():
                coding_qs = []
                for cq in seed_data.get('coding', []):
                    coding_qs.append(CodingQuestion(
                        title=cq['t'], description=cq['d'], sample_answer=cq['s'], 
                        difficulty=cq['diff'], language=cq['l']
                    ))
                db.session.add_all(coding_qs)

            if not HRQuestion.query.first():
                hr_qs = []
                for hq in seed_data.get('hr', []):
                    hr_qs.append(HRQuestion(
                        question=hq['q'], suggested_answer=hq['s'], category=hq['c']
                    ))
                db.session.add_all(hr_qs)
        
        if not DailyTip.query.first():
            tips = [
                DailyTip(tip="Practice at least 3 aptitude questions daily to build speed and accuracy.", category="Aptitude"),
                DailyTip(tip="Use the STAR method (Situation, Task, Action, Result) for all behavioral HR questions.", category="HR"),
                DailyTip(tip="Understand time complexity before attempting any coding challenge.", category="Coding"),
                DailyTip(tip="Research the company thoroughly before any interview — know their products & culture.", category="Interview"),
                DailyTip(tip="Keep your resume to 1 page if you have less than 2 years of experience.", category="Resume"),
                DailyTip(tip="Mock interviews are the best way to eliminate nervousness. Practice daily!", category="Interview"),
                DailyTip(tip="Always explain your thought process aloud during technical interviews.", category="Coding"),
                DailyTip(tip="Use flashcards to memorize key formulas for quantitative aptitude.", category="Aptitude"),
                DailyTip(tip="Dress professionally, even for virtual interviews — it boosts your confidence.", category="Interview"),
                DailyTip(tip="Have 3–5 solid project examples ready to discuss in depth.", category="Interview"),
            ]
            db.session.add_all(tips)

        db.session.commit()


# ─── Helper: Update Streak ────────────────────────────────────────────────────

def update_streak(user):
    today = date.today()
    if user.last_active == today:
        return  # Already updated today
    if user.last_active and (today - user.last_active).days == 1:
        user.streak += 1
    else:
        user.streak = 1  # Reset streak
    user.last_active = today
    db.session.commit()


# ─── Routes ───────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email    = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm  = request.form.get('confirm_password', '')

        # Server-side validation
        if len(username) < 3:
            flash('Username must be at least 3 characters.', 'danger')
            return redirect(url_for('register'))
        if '@' not in email or '.' not in email:
            flash('Please enter a valid email address.', 'danger')
            return redirect(url_for('register'))
        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'danger')
            return redirect(url_for('register'))
        if password != confirm:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('register'))

        if User.query.filter_by(username=username).first():
            flash('Username already exists! Please choose a different one.', 'danger')
            return redirect(url_for('register'))
        if User.query.filter_by(email=email).first():
            flash('An account with this email already exists!', 'danger')
            return redirect(url_for('register'))

        hashed = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, email=email, password=hashed)
        db.session.add(new_user)
        db.session.commit()

        flash('🎉 Registration successful! Welcome aboard. Please login.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id']  = user.id
            session['username'] = user.username
            update_streak(user)
            flash(f'🚀 Welcome back, {user.username}! Your streak is {user.streak} 🔥', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('❌ Invalid username or password. Please try again.', 'danger')

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out safely. See you soon! 👋', 'info')
    return redirect(url_for('index'))


@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user     = db.session.get(User, session['user_id'])
    tip      = DailyTip.query.order_by(db.func.random()).first()
    records  = TestRecord.query.filter_by(user_id=user.id).order_by(TestRecord.date.desc()).limit(5).all()
    avg_score = 0
    valid_records = [r for r in records if r.total > 0]
    if valid_records:
        avg_score = round(sum((r.score / r.total * 100) for r in valid_records) / len(valid_records), 1)
    return render_template('dashboard.html', user=user, tip=tip, records=records, avg_score=avg_score)


@app.route('/aptitude')
def aptitude():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    category = request.args.get('category', 'all')
    search = request.args.get('search', '').strip()
    
    query = AptitudeQuestion.query
    if category != 'all':
        query = query.filter_by(category=category)
    if search:
        query = query.filter(AptitudeQuestion.question.contains(search) | AptitudeQuestion.explanation.contains(search))
        
    questions = query.all()
    categories = db.session.query(AptitudeQuestion.category).distinct().all()
    categories = [c[0] for c in categories]
    return render_template('aptitude.html', questions=questions, categories=categories, selected=category, search=search)

@app.route('/concepts')
def concepts():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    all_concepts = AptitudeConcept.query.all()
    
    # Process formulas to list
    import json
    for c in all_concepts:
        try:
            c.formulas_list = json.loads(c.formulas) if c.formulas else []
        except json.JSONDecodeError:
            c.formulas_list = []
            
    return render_template('concepts.html', concepts=all_concepts)


@app.route('/coding')
def coding():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    diff = request.args.get('difficulty', 'all')
    search = request.args.get('search', '').strip()
    
    query = CodingQuestion.query
    if diff != 'all':
        query = query.filter_by(difficulty=diff)
    if search:
        query = query.filter(CodingQuestion.title.contains(search) | CodingQuestion.description.contains(search))
        
    questions = query.all()
        
    completed_ids = [c.question_id for c in CompletedCoding.query.filter_by(user_id=session['user_id']).all()]
    
    return render_template('coding.html', questions=questions, selected_diff=diff, completed_ids=completed_ids, search=search)


@app.route('/complete_coding/<int:q_id>', methods=['POST'])
def complete_coding(q_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Login required'}), 401
    
    # Check if already completed
    existing = CompletedCoding.query.filter_by(user_id=session['user_id'], question_id=q_id).first()
    if not existing:
        new_completion = CompletedCoding(user_id=session['user_id'], question_id=q_id)
        db.session.add(new_completion)
        
        # Award some bonus points
        user = db.session.get(User, session['user_id'])
        user.points += 25
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Challenge marked as completed! +25 Points'})
    
    return jsonify({'success': False, 'message': 'Already completed'})


@app.route('/hr')
def hr():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    category = request.args.get('category', 'all')
    search = request.args.get('search', '').strip()
    
    query = HRQuestion.query
    if category != 'all':
        query = query.filter_by(category=category)
    if search:
        query = query.filter(HRQuestion.question.contains(search) | HRQuestion.suggested_answer.contains(search))
        
    questions = query.all()
    categories = db.session.query(HRQuestion.category).distinct().all()
    categories = [c[0] for c in categories]
    return render_template('hr.html', questions=questions, categories=categories, selected=category, search=search)


@app.route('/mock_test', methods=['GET', 'POST'])
def mock_test():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        score       = 0
        ans_results = []
        questions   = AptitudeQuestion.query.all()
        total       = len(questions)

        for q in questions:
            user_ans   = request.form.get(f'q{q.id}')
            is_correct = (user_ans == q.correct_option)
            if is_correct:
                score += 1
            ans_results.append({
                'question'   : q.question,
                'user_ans'   : user_ans if user_ans else 'Not answered',
                'correct_ans': q.correct_option,
                'is_correct' : is_correct,
                'explanation': q.explanation
            })

        user = db.session.get(User, session['user_id'])
        user.points += score * 10
        record = TestRecord(user_id=user.id, score=score, total=total, results_json=json.dumps(ans_results))
        db.session.add(record)
        db.session.commit()

        percentage = round((score / total) * 100, 1) if total > 0 else 0
        return render_template('mock_result.html', score=score, total=total,
                               results=ans_results, percentage=percentage)

    questions = AptitudeQuestion.query.all()
    random.shuffle(questions)
    return render_template('mock_test.html', questions=questions)


@app.route('/leaderboard')
def leaderboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    top_users = User.query.order_by(User.points.desc()).limit(10).all()
    current_user = db.session.get(User, session['user_id'])
    
    # Calculate global rank
    users_sorted = User.query.order_by(User.points.desc()).all()
    try:
        rank = [u.id for u in users_sorted].index(current_user.id) + 1
    except ValueError:
        rank = "N/A"
        
    return render_template('leaderboard.html', top_users=top_users, current_user=current_user, rank=rank)


@app.route('/test_details/<int:record_id>')
def test_details(record_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    record = db.session.get(TestRecord, record_id)
    if not record or record.user_id != session['user_id']:
        flash('🚫 Unauthorized access or record not found.', 'danger')
        return redirect(url_for('profile'))
    
    # Parse results from JSON string
    results = []
    if record.results_json:
        results = json.loads(record.results_json)
    
    return render_template('test_details.html', record=record, results=results)


@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user    = db.session.get(User, session['user_id'])
    records = TestRecord.query.filter_by(user_id=user.id).order_by(TestRecord.date.desc()).all()
    best    = max((r.score for r in records), default=0)
    total_tests = len(records)
    
    # Calculate global rank
    users_sorted = User.query.order_by(User.points.desc()).all()
    try:
        rank = [u.id for u in users_sorted].index(user.id) + 1
    except ValueError:
        rank = "N/A"
        
    return render_template('profile.html', user=user, records=records, best=best, total_tests=total_tests, rank=rank)


# ─── AJAX Endpoints ───────────────────────────────────────────────────────────

@app.route('/check_username', methods=['POST'])
def check_username():
    data = request.get_json(silent=True) or {}
    username = data.get('username', '').strip()
    user = User.query.filter_by(username=username).first()
    return jsonify({'exists': user is not None})


@app.route('/check_email', methods=['POST'])
def check_email():
    data = request.get_json(silent=True) or {}
    email = data.get('email', '').strip()
    user = User.query.filter_by(email=email).first()
    return jsonify({'exists': user is not None})


@app.route('/chatbot', methods=['POST'])
def chatbot_response():
    data = request.get_json(silent=True) or {}
    user_msg = data.get('message', '').lower()

    if any(w in user_msg for w in ['hi', 'hello', 'hey']):
        reply = "Hey there! 👋 I'm your Placement Booster AI. Ask me about Aptitude, Coding, HR tips, or Mock Tests!"
    elif 'streak' in user_msg:
        reply = "🔥 Keep your daily streak alive! Login every day to maintain your streak and earn bonus points."
    elif 'aptitude' in user_msg:
        reply = "🧠 Aptitude section has 10+ curated MCQs covering Speed & Distance, Percentages, Ratios, Series, and more!"
    elif 'coding' in user_msg or 'code' in user_msg:
        reply = "💻 The Coding section has problems from Easy to Medium. See solutions right in the browser!"
    elif 'hr' in user_msg or 'interview' in user_msg:
        reply = "🎤 HR section covers Introduction, Behavioral, Company Fit, and Career Goal questions with sample answers."
    elif 'mock' in user_msg or 'test' in user_msg:
        reply = "⏱️ Mock Tests have randomized questions with a live timer. You earn 10 points per correct answer!"
    elif 'point' in user_msg or 'score' in user_msg:
        reply = "🏆 You earn 10 points per correct answer in Mock Tests. Points rank you on the Leaderboard!"
    elif 'leaderboard' in user_msg or 'rank' in user_msg:
        reply = "🥇 Check the Leaderboard to see where you stand among all users. Top 3 get special badges!"
    elif 'tip' in user_msg:
        tip = DailyTip.query.order_by(db.func.random()).first()
        reply = f"💡 Tip: {tip.tip}" if tip else "Keep practicing every day!"
    else:
        reply = "🤖 I can help with Aptitude, Coding, HR prep, Mock Tests, Points & Leaderboard. What would you like to know?"

    return jsonify({'response': reply})


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
