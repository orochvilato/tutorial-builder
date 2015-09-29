import webbrowser
from flask import Flask, render_template
from threading import Timer
app = Flask(__name__)

@app.route('/hello')
@app.route('/hello/<name>')
def hello_world(name=None):
    return render_template('main.html',name=name)

def openbrowser():
    webbrowser.open('http://localhost:5000/hello',new=1)

def main():
    import logging
    logging.basicConfig(filename='example.log',level=logging.DEBUG)
    logging.info('start')
    app.debug = True
    app.run()
    logging.info('end')
        
if __name__ == '__main__':
    #Timer(1,openbrowser,()).start()
    main()
    
