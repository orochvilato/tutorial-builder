import webbrowser
from flask import Flask
from threading import Timer
app = Flask(__name__)

@app.route('/hello')
@app.route('/hello/<name>')
def hello_world(name=None):
    return render_template('main.html',name=name)

def openbrowser():
    webbrowser.open('http://localhost:5000/hello',new=1)
    
if __name__ == '__main__':
    Timer(1,openbrowser,()).start()
    app.run()
    
    
