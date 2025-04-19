from flask import Flask, render_template, request, session, redirect, url_for
import random
from questions import questions
from model import get_recommendations  # Ensure this function is defined in model.py

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a strong, random key

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/quiz', methods=['GET', 'POST'])
def quiz():  # renamed from `home` to `quiz`
    if request.method == 'POST':
        responses = [request.form[f'response{i}'] for i in range(5)]
        session['responses'] = responses
        return redirect(url_for('results'))

    if 'selected_questions' not in session:
        session['selected_questions'] = random.sample(questions, 5)

    return render_template('index.html', questions=session['selected_questions'])

@app.route('/results')
def results():
    responses = session.get('responses', [])
    if not responses:
        return redirect(url_for('quiz'))

    recommendations = get_recommendations(responses)
    return render_template('result.html', recommendations=recommendations)

if __name__ == '__main__':
    app.run(debug=True)
