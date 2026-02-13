from flask import Flask, render_template, request, jsonify, redirect
from carpark_db import CarParkDB


app = Flask(__name__)
db = CarParkDB()



@app.route('/', methods=['GET', 'POST'])
def index(data=None):


    return render_template('index.html',
                           car_photo='img/car_photo1.jpg',
                           user_photo='img/person_photo2.jpg',
                           search_fields=['FirstName', 'LastName', 'Age', 'Registration', 'Make', 'Model', 'CarColour', 'Permit', 'UserType', 'ValidFrom', 'ValidUntil'],
                           page_url = 'index'
                           )



@app.route("/filter-data", methods=["POST"])
def recieve_filter_data():
    
    filter_data = request.get_json()
    rows = db.query_database(filter_data)

    return jsonify(rows)



@app.route('/add_records', methods=['GET','POST'])
def add_records():
    
    return render_template('add_records.html', page_url = 'add_records')
    


@app.route('/validate-data', methods=['POST'])
def validate_data():

    unvalidated_data = request.get_json()

    #performs data validation on the data inputted
    non_valid_data = db.validate_data(unvalidated_data)  

    print('data has been validated') 
    
    if non_valid_data['isSuccessful'] == True:
        non_valid_data = db.add_data_to_db(unvalidated_data, non_valid_data)

    return jsonify(non_valid_data)


if __name__ == '__main__':
    app.run(debug=True)
