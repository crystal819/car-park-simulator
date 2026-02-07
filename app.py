from flask import Flask, render_template, request, jsonify, redirect
from carpark_db import CarParkDB


app = Flask(__name__)
db = CarParkDB()



@app.route('/', methods=['GET', 'POST'])
def index(data=None):


    return render_template('index.html',
                           car_photo='img/car_photo1.jpg',
                           user_photo='img/person_photo2.jpg',
                           search_fields=['First Name', 'Last name', 'Age', 'Registration', 'Car colour', 'Permit', 'User Type', 'Valid From', 'Valid Until'],
                           page_url = 'index'
                           )



@app.route("/filter-data", methods=["POST"])
def recieve_filter_data():
    
    filter_data = request.get_json()
    rows = db.query_database(filter_data)

    return jsonify(rows)


@app.route('/add_records')
def add_records():
    
    return render_template('add_records.html', page_url = 'add_records')
    




if __name__ == '__main__':
    app.run(debug=True)