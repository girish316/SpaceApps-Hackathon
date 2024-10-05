from flask import Flask, render_template
from map import create_map

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/map')
def show_map():
    create_map()
    return render_template('map.html')

if __name__ == '__main__':
    app.run(debug=True)
