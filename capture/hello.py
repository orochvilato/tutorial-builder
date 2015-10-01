import webbrowser
from flask import Flask, render_template
from threading import Timer
import json

app = Flask(__name__)
from record.record import Snapshot
S = Snapshot()
@app.route('/hello')
@app.route('/hello/<name>')
def hello_world(name=None):
    return render_template('main.html',name=name)

@app.route('/action/<name>')
def action(name):
    if name=='start':
        S.start()
    elif name=='stop':
        S.stop()
    elif name=='save':
        S.saveTimeline()
    return json.dumps('done')
    
@app.route('/test')
def test():
    return json.dumps(['a','b'])
        
def openbrowser():
    webbrowser.open('http://localhost:5000/hello',new=1)

def main():
    import logging
    logging.basicConfig(filename='example.log',level=logging.INFO)
    logging.info('start')
    app.debug = True
    app.run()
    logging.info('end')
        
if __name__ == '__main__':
    #Timer(1,openbrowser,()).start()
    
    main()
    
