from flask import Flask, render_template
from map import create_map
import folium

app = Flask(__name__)

@app.route('/')
def home():
    return "Welcome to the Calgary Community Insights!"

@app.route('/map')
def show_map():
    create_map()
    return render_template('map.html')

if __name__ == '__main__':
    app.run(debug=True)
