from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def index():
    # if current_user.is_authenticated:
    #     return redirect(url_for('dashboard'))
    
    return render_template('index.html')

print("hello")




