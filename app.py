# from flask import Flask, render_template, request
from tkinter import *


window = Tk()

window.title("Task Management System")
window.geometry('350x200')
lbl = Label(window, text = "Hello", font=("Arial Bold", 50))
lbl.grid(column=0, row=0)

btn = Button()

window.mainloop()

# app = Flask(__name__)

# @app.route('/')
# def index():
#     # if current_user.is_authenticated:
#     #     return redirect(url_for('dashboard'))
    
#     return render_template('index.html')

# print('Hi')

