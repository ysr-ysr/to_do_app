from flask import Flask, render_template, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
 
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(500), nullable=False)
    completed = db.Column(db.Integer, default=0)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Task {self.id}>'

@app.route("/", methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        task_content = request.form['content']
        new_task = Todo(content=task_content)
        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect('/')
        except:
            return "There was an issue adding your task"
    else:
        tasks_pending = Todo.query.filter_by(completed=0).order_by(Todo.date_created).all()
        tasks_done = Todo.query.filter_by(completed=1).order_by(Todo.date_created).all()
        return render_template("index.html", tasks_pending=tasks_pending, tasks_done=tasks_done)

@app.route("/delete/<int:id>")
def delete(id):
    task_to_delete = Todo.query.get_or_404(id)
    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return "There was a problem deleting that task"

@app.route("/update/<int:id>", methods=['GET', 'POST'])
def update(id):
    task = Todo.query.get_or_404(id)
    if request.method == 'POST':
        task.content = request.form['content']

        try:
            db.session.commit()
            return redirect('/')
        except:
            return "There was an issue updating your task"
    else:
        return render_template('update.html', task=task)


@app.route("/toggle/<int:id>", methods=['POST'])
def toggle(id):
    task = Todo.query.get_or_404(id)
    task.completed = 0 if task.completed else 1
    try:
        db.session.commit()
    except:
        return "Error while updating task status"
    return redirect('/')







# AI PART --------

import google.generativeai as genai
from flask import jsonify

genai.configure(api_key="AIzaSyCOtZhJhc1eZDv9HalauUcFh3JhV4wvIjQ")
model = genai.GenerativeModel(model_name="models/gemini-1.5-flash")


conversation_history = ["Tu es un coach personnel intelligent qui aide à organiser les tâches."
    "Soyers concis et précis dans vos réponses."
    "Tu peux répondre aux questions sur les tâches, les organiser et donner des conseils sur la gestion du temps."
    "Tu peux aussi aider à prioriser les tâches en fonction de leur importance et de leur urgence."
    "Tu peux aussi suggérer des méthodes pour améliorer la productivité."
    "soyez gentil et encourageant dans vos réponses."
    "tu peut utiliser des emojis mais juste un peut."
]

def ask_agent(question):
    conversation_history.append("Utilisateur: " + question)
    prompt = "\n".join(conversation_history) + "\nCoach:"
    response = model.generate_content(prompt)
    answer = response.text.strip()
    conversation_history.append("Coach: " + answer)
    return answer

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    question = data.get("message", "")
    if not question:
        return jsonify({"response": "Je n'ai pas compris."})
    response = ask_agent(question)
    return jsonify({"response": response})


if __name__ == "__main__":
    app.run(debug=True)
