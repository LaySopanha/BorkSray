from flask import Blueprint, render_template, request
from .utils import process_excel, ask_gpt

main = Blueprint('main', __name__)

@main.route('/', methods=['GET', 'POST'])
def index():
    answer = None
    if request.method == 'POST':
        file = request.files['file']
        query = request.form['query']
        data_summary = process_excel(file)
        answer = ask_gpt(query, data_summary)
    return render_template('index.html', answer=answer)
