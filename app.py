
from tkinter import Tk, filedialog


window = Tk()

window.title("Task Management System")
window.geometry('350x200')



app = Flask(__name__)

@app.route('/')
def index():
    # if current_user.is_authenticated:
    #     return redirect(url_for('dashboard'))
    
    return render_template('index.html')

print('Hi')


