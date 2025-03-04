from flask import Flask, render_template, request
from tkinter import Tk, filedialog


app = Flask(__name__)

@app.route('/')
def index():
    # if current_user.is_authenticated:
    #     return redirect(url_for('dashboard'))
    
    return render_template('index.html')

print('Hi')




