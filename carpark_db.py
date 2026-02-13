import flask
import pyodbc
from datetime import datetime, date
from database_setup import ConnString

class CarParkDB():
    def __init__(self):
        x = ConnString()
        self.conn_string = x.connstr()

    def _get_connection(self):
        return pyodbc.connect(self.conn_string)
    
    def convert_date_to_ISO(self, date): #converts dates from dd/mm/yyyy -> yyyy-mm-dd || human read-able to date standard
        ISOstr = date[-4:] + '-' + date[3:5] + '-' + date[:2]
        return ISOstr


    def query_database(self, filter_data):
#------------------------permit---------------------------
        permit_query = ''
        if filter_data['from'] != 'Valid From':
            permit_query += f" ValidFrom >= '{self.convert_date_to_ISO(filter_data['from'])}' AND"
        if filter_data['until'] != 'Valid Until':
            permit_query += f" ValidUntil <= '{self.convert_date_to_ISO(filter_data['until'])}' AND"
        if filter_data['permit'] == 'active':
            permit_query += " HasPermit = '1' AND"
        elif filter_data['permit'] == 'inactive':
            permit_query += " HasPermit = '0' AND"

        if len(permit_query) > 1:
            permit_query = 'SELECT SYNumber, NumberPlate, HasPermit, ValidFrom, ValidUntil FROM Permit WHERE' + permit_query
            permit_query = permit_query[:-3]
        else:
            permit_query = 'SELECT SYNumber, NumberPlate, HasPermit, ValidFrom, ValidUntil FROM Permit'

#--------------------------users----------------------
        if filter_data['name'] != '':
            words = filter_data['name'].split(' ')
            if len(words) >= 2:
                firstname = words[0]
                lastname = ''
                for i in range(len(words)-1):
                    lastname += words[i+1] + ' '
                lastname = lastname[:-1]
                user_query = f"SELECT SYNumber, FirstName, LastName, Age, UserType, PhotoPath FROM Users WHERE FirstName = '{firstname}' AND LastName = '{lastname}' AND ("
            else:
                user_query = f"SELECT SYNumber, FirstName, LastName, Age, UserType, PhotoPath FROM Users WHERE FirstName = '{filter_data['name']}' AND ("
            if filter_data['staff'] == 'on':
                user_query += " UserType = 'staff' OR"
            if filter_data['student'] == 'on':
                user_query += " UserType = 'student' OR"
            if filter_data['visitor'] == 'on':
                user_query += " UserType = 'visitor' OR"
            
            if user_query[-1:] == '(':
                user_query = user_query[:-6]
            else:
                user_query = user_query[:-3] + ')'


        else:
            user_query = ''
            if filter_data['staff'] == 'on':
                user_query += " UserType = 'staff' OR"
            if filter_data['student'] == 'on':
                user_query += " UserType = 'student' OR"
            if filter_data['visitor'] == 'on':
                user_query += " UserType = 'visitor' OR"
            if len(user_query) > 1:
                user_query = 'SELECT SYNumber, FirstName, LastName, Age, UserType, PhotoPath FROM Users WHERE' + user_query
                user_query = user_query[:-3]
            else:
                user_query = 'SELECT SYNumber, FirstName, LastName, Age, UserType, PhotoPath FROM Users'

#------------------------car-----------------------------
        car_query = ''
        if filter_data['reg'] != '':
            if len(filter_data['reg']) == 8: #format check
                filter_data['reg'] = filter_data['reg'][:4]+filter_data['reg'][5:] #removes the additional space if included
            car_query += f" NumberPlate = '{filter_data['reg']}' AND"
        if filter_data['make'] != '':
            car_query += f" Make = '{filter_data['make']}' AND"
        if filter_data['model'] != '':
            car_query += f" Model = '{filter_data['model']}' AND"
        
        if len(car_query) > 1:
            car_query = 'SELECT NumberPlate, Colour, PhotoPath, Make, Model FROM Car WHERE' + car_query
            car_query = car_query[:-4]
        else:
            car_query = 'SELECT NumberPlate, Colour, PhotoPath, Make, Model FROM Car'

#--------------------------determines ordering----------------------
        if filter_data['order'] is None:
            order_query = '' #skips as this is when the search button is pressed so there is no ordering
        else:
            if filter_data['order'][1] == 'none':
                order_query = '' #empty since there is no ordering
            elif filter_data['order'][1] == 'asc':
                if filter_data['order'][0] in ['FirstName', 'LastName', 'Age', 'UserType', 'ValidFrom', 'ValidUntil', 'Make', 'Model']:
                    order_query = f' ORDER BY {filter_data['order'][0]} ASC'
                elif filter_data['order'][0] == 'CarColour':
                    order_query = f' ORDER BY Colour ASC'
                elif filter_data['order'][0] == 'Registration':
                    order_query = f' ORDER BY NumberPlate ASC'
                elif filter_data['order'][0] == 'Permit':
                    order_query = f' ORDER BY HasPermit ASC'
                
            elif filter_data['order'][1] == 'desc':
                if filter_data['order'][0] in ['FirstName', 'LastName', 'Age', 'UserType', 'ValidFrom', 'ValidUntil', 'Make', 'Model']:
                    order_query = f' ORDER BY {filter_data['order'][0]} DESC'
                elif filter_data['order'][0] == 'CarColour':
                    order_query = f' ORDER BY Colour DESC'
                elif filter_data['order'][0] == 'Registration':
                    order_query = f' ORDER BY NumberPlate DESC'
                elif filter_data['order'][0] == 'Permit':
                    order_query = f' ORDER BY HasPermit DESC'
            
            if len(order_query) == 0:
                pass
            elif filter_data['order'][0] in ['FirstName', 'LastName', 'Age', 'UserType']:
                order_query = order_query[:10]+'u.'+order_query[10:]
            elif filter_data['order'][0] in ['Registration', 'Make', 'Model', 'CarColour']:
                order_query = order_query[:10]+'c.'+order_query[10:]
            elif filter_data['order'][0] in ['Permit', 'ValidFrom', 'ValidUntil']:
                order_query = order_query[:10]+'p.'+order_query[10:]
 
#----------------------------------------------------------------------execute the sql statement------------------------
        with self._get_connection() as conn:
            sql = f"SELECT u.FirstName,u.LastName,u.Age,c.NumberPlate,c.Colour,p.HasPermit,u.UserType,p.ValidFrom,p.ValidUntil,u.PhotoPath,c.PhotoPath,c.Make,c.Model FROM ({user_query}) u JOIN ({permit_query}) p ON u.SYNumber = p.SYNumber JOIN ({car_query}) c ON p.NumberPlate = c.NumberPlate{order_query}"
            print(sql)
            rows = conn.cursor().execute(sql).fetchall()

        data = []
        for i in range(len(rows)):
            data.append({
                        'first_name': rows[i][0],
                        'last_name': rows[i][1],
                        'age': rows[i][2],
                        'number_plate': rows[i][3],
                        'colour': rows[i][4],
                        'permit': rows[i][5],
                        'usertype': rows[i][6],
                        'valid_from': rows[i][7],
                        'valid_until': rows[i][8],
                        'user_photo': rows[i][9],
                        'car_photo': rows[i][10],
                        'Id': i,
                        'make': rows[i][11],
                        'model': rows[i][12]
            })

        return data
    

    #performs data validation -> returns a dict with a list of errors associated with each input field (if no errors then its left empty and isSuccessful = True)
    def validate_data(self, unvalidated_data):

        if unvalidated_data['Data'] == 'User':
            non_valid_data = {  'isSuccessful': True, #sets the successfull bool to true
                                'SYNumber': [], #empty arrays for storing errors for that input if present
                                'FirstName': [],
                                'LastName': [],
                                'Age': [],
                                'UserType': []
            }

            #---------------------for validating SYNumber------------------------length + type check
            if len(unvalidated_data['SYNumber']) == 0:
                non_valid_data['SYNumber'].append('SYNumber is omitted')
            elif type(unvalidated_data['SYNumber']) != int: #type check
                try:
                    unvalidated_data['SYNumber'] = int(unvalidated_data['SYNumber'])
                except:
                    non_valid_data['isSuccessful'] = False
                    non_valid_data['SYNumber'].append('SYNumber is not a number')

            if len(str(unvalidated_data['SYNumber'])) != 6: #length check
                        non_valid_data['isSuccessful'] = False
                        non_valid_data['SYNumber'].append('SYNumber is not 6 digits')

            #--------------------for validating FirstName-------------------------length + type check
            temp = unvalidated_data['FirstName'].replace(" ", "")     
            if len(unvalidated_data['FirstName']) > 20: #length check
                non_valid_data['isSuccessful'] = False
                non_valid_data['FirstName'].append('First name is too long')
            elif len(unvalidated_data['FirstName']) < 1: 
                non_valid_data['isSuccessful'] = False
                non_valid_data['FirstName'].append('First name is omitted')
            elif not temp.isalnum(): #type check
                non_valid_data['isSuccessful'] = False
                non_valid_data['FirstName'].append('First name cannot contain special characters')
            
            #--------------------for validating LastName-------------------------length + type + existence check
            temp = unvalidated_data['LastName'].replace(" ", "")
            if len(unvalidated_data['LastName']) != 0: #existence check
                if len(unvalidated_data['LastName']) < 1 or len(unvalidated_data['LastName']) > 20: #length check
                    if not len(unvalidated_data['LastName']) == 0: #ensures it wasnt just left empty
                        non_valid_data['isSuccessful'] = False
                        non_valid_data['LastName'].append('Last name is too long')
                if not temp.isalnum(): #type check
                    non_valid_data['isSuccessful'] = False
                    non_valid_data['LastName'].append('Last name cannot contain special characters')
                    
            #--------------------for validating \Age-------------------------range + type check
            if len(str(unvalidated_data['Age'])) > 100: #length check
                non_valid_data['isSuccessful'] = False
                non_valid_data['Age'].append('Age is too long')
            elif len(str(unvalidated_data['Age'])) < 1:
                non_valid_data['isSuccessful'] = False
                non_valid_data['Age'].append('Age is omitted')
            else:
                if type(unvalidated_data['Age']) != int: #type check
                    try:
                        unvalidated_data['Age'] = int(unvalidated_data['Age'])
                    except:
                        non_valid_data['isSuccessful'] = False
                        non_valid_data['Age'].append('Age is not a number')

            #--------------------for validating UserType-------------------format check
            if unvalidated_data['UserType'] not in ['Student', 'Staff', 'Visitor']:
                non_valid_data['isSuccessful'] = False
                non_valid_data['UserType'].append('Not a valid user type')



        elif unvalidated_data['Data'] == 'Car':
            non_valid_data = {  'isSuccessful': True, #sets the successfull bool to true
                                'NumberPlate': [], #empty arrays for storing errors for that input if present
                                'Make': [],
                                'Model': [],
                                'Colour': []
            }

            #--------------for validating NumberPlate------------------- length + format + type check
            try: #type check
                int(unvalidated_data['NumberPlate'])
                non_valid_data['isSuccessful'] = False
                non_valid_data['NumberPlate'].append('NumberPlate is an int')
            except:
                try: 
                    float(unvalidated_data['NumberPlate']) 
                    non_valid_data['isSuccessful'] = False
                    non_valid_data['NumberPlate'].append('NumberPlate is a float')
                except:
                    pass

            if len(unvalidated_data['NumberPlate']) == 8: #format check
                unvalidated_data['NumberPlate'] = unvalidated_data['NumberPlate'][:4]+unvalidated_data['NumberPlate'][5:] #removes the additional space if included

            if len(unvalidated_data['NumberPlate']) > 8: #length check
                non_valid_data['isSuccessful'] = False
                non_valid_data['NumberPlate'].append('NumberPlate length is too long')
            elif len(unvalidated_data['NumberPlate']) < 1: #length check
                non_valid_data['isSuccessful'] = False
                non_valid_data['NumberPlate'].append('NumberPlate length is omitted')

            #-----------------for validating Make------------------------- length + type check
            temp = unvalidated_data['Make'].replace(" ", "")
                
            if len(unvalidated_data['Make']) > 20: #length check
                non_valid_data['isSuccessful'] = False
                non_valid_data['Make'].append('Car make is too long')
            elif len(unvalidated_data['Make']) < 1: 
                non_valid_data['isSuccessful'] = False
                non_valid_data['Make'].append('Car make is omitted')
            elif not temp.isalnum(): #type check
                non_valid_data['isSuccessful'] = False
                non_valid_data['Make'].append('Car make cannot contain special characters')

            #-----------------for validating Model------------------------- length + type check
            temp = unvalidated_data['Model'].replace(" ", "")
                
            if len(unvalidated_data['Model']) > 20: #length check
                non_valid_data['isSuccessful'] = False
                non_valid_data['Model'].append('Car model is too long')
            elif len(unvalidated_data['Model']) < 1: 
                non_valid_data['isSuccessful'] = False
                non_valid_data['Model'].append('Car model is omitted')
            elif not temp.isalpha(): #type check
                non_valid_data['isSuccessful'] = False
                non_valid_data['Model'].append('Car model cannot contain special characters')

            #-----------------for validating Colour------------------------- length + type check
            temp = unvalidated_data['Colour'].replace(" ", "")
                
            if len(unvalidated_data['Colour']) > 20: #length check
                non_valid_data['isSuccessful'] = False
                non_valid_data['Colour'].append('Car colour is too long')
            elif len(unvalidated_data['Colour']) < 1: 
                non_valid_data['isSuccessful'] = False
                non_valid_data['Colour'].append('Car colour is omitted')
            elif not temp.isalpha(): #type check
                non_valid_data['isSuccessful'] = False
                non_valid_data['Colour'].append('Car colour cannot contain numbers and/or special characters')



        elif unvalidated_data['Data'] == 'Permit':
            non_valid_data = {  'isSuccessful': True, #sets the successfull bool to true
                                'SYNumber': [], #empty arrays for storing errors for that input if present
                                'NumberPlate': [],
                                'HasPermit': [],
                                'ValidFrom': [],
                                'ValidUntil': []
            }

            #---------------for validating SYNumber-------------- length + type check
            if len(unvalidated_data['SYNumber']) == 0:
                non_valid_data['SYNumber'].append('SYNumber is omitted')
            elif type(unvalidated_data['SYNumber']) != int: #type check
                try:
                    unvalidated_data['SYNumber'] = int(unvalidated_data['SYNumber'])
                except:
                    non_valid_data['isSuccessful'] = False
                    non_valid_data['SYNumber'].append('SYNumber is not a number')

            if len(str(unvalidated_data['SYNumber'])) != 6: #length check
                        non_valid_data['isSuccessful'] = False
                        non_valid_data['SYNumber'].append('SYNumber is not 6 digits')

            #--------------for validating NumberPlate------------------- length + format + type check
            try: #type check
                int(unvalidated_data['NumberPlate'])
                non_valid_data['isSuccessful'] = False
                non_valid_data['NumberPlate'].append('NumberPlate is an int')
            except:
                try: 
                    float(unvalidated_data['NumberPlate']) 
                    non_valid_data['isSuccessful'] = False
                    non_valid_data['NumberPlate'].append('NumberPlate is a float')
                except:
                    pass

            if len(unvalidated_data['NumberPlate']) == 8: #format check
                unvalidated_data['NumberPlate'] = unvalidated_data['NumberPlate'][:4]+unvalidated_data['NumberPlate'][5:] #removes the additional space if included


            if len(unvalidated_data['NumberPlate']) > 8: #length check
                non_valid_data['isSuccessful'] = False
                non_valid_data['NumberPlate'].append('NumberPlate length is too long')
            elif len(unvalidated_data['NumberPlate']) < 1: #length check
                non_valid_data['isSuccessful'] = False
                non_valid_data['NumberPlate'].append('NumberPlate length is omitted')

            #--------------for validating HasPermit---------------------type check (only options are yes and no)
            if unvalidated_data['HasPermit'] not in ['Yes', 'No']:
                non_valid_data['isSuccessful'] = False
                non_valid_data['HasPermit'].append('Has Permit option selected is not an option')

            if unvalidated_data['HasPermit'] == 'Yes':
                #---------------for validating ValidFrom and ValidUntil----------------------range + existence check
                if unvalidated_data['ValidFrom'] != '': #existence check for ValidFrom
                    if unvalidated_data['ValidUntil'] != '': #existence check for ValidUntil
                        valid_from_date = datetime.strptime(self.convert_date_to_ISO(unvalidated_data['ValidFrom']), "%Y-%m-%d")
                        valid_until_date = datetime.strptime(self.convert_date_to_ISO(unvalidated_data['ValidUntil']), "%Y-%m-%d")
                        today_date = datetime.strptime(str(date.today()), "%Y-%m-%d")
                        if valid_from_date > today_date: #range check
                            non_valid_data['isSuccessful'] = False
                            non_valid_data['ValidFrom'].append('ValidFrom is set to a future date')
                        if valid_from_date > valid_until_date:
                            non_valid_data['isSuccessful'] = False
                            non_valid_data['ValidUntil'].append('Inconsistent with the valid from date')
                    else:
                        non_valid_data['isSuccessful'] = False
                        non_valid_data['ValidUntil'].append('Valid From supplied but no expiry date')
                else:
                    if unvalidated_data['ValidUntil'] != '': #existence check for ValidUntil
                        non_valid_data['isSuccessful'] = False
                        non_valid_data['ValidUntil'].append('Valid Until supplied but no Valid From')



        return non_valid_data 


    #adds new records to the database (assumes the data is already validated)
    def add_data_to_db(self, data, non_valid_data):
        print(data)
        if data['Data'] == 'User':
            with self._get_connection() as conn:
                sql_identity = f"SELECT * FROM Users WHERE SYNumber = {int(data['SYNumber'])} "
                #runs an sql command to check if the primary key has already been taken
                results = conn.cursor().execute(sql_identity).fetchall()

            if len(results) != 0:
                non_valid_data['isSuccessful'] = False
                non_valid_data['SYNumber'].append("This SYNumber has already been registered with a user")
            else:
                if len(data['LastName']) == 0:
                    last_name = 'Null'
                    sql = f"INSERT INTO Users (SYNumber, FirstName, LastName, Age, UserType) VALUES ({int(data['SYNumber'])}, '{data['FirstName']}', {last_name}, {int(data['Age'])}, '{data['UserType']}')"
                else:
                    last_name = data['LastName']
                    sql = f"INSERT INTO Users (SYNumber, FirstName, LastName, Age, UserType) VALUES ({int(data['SYNumber'])}, '{data['FirstName']}', '{last_name}', {int(data['Age'])}, '{data['UserType']}')"
                with self._get_connection() as conn:
                    print(sql)
                    conn.cursor().execute(sql)

        elif data['Data'] == 'Car':
            with self._get_connection() as conn:
                sql_identity = f"SELECT * FROM Car WHERE NumberPlate = '{data['NumberPlate']}'"
                #runs an sql command to check if the primary key has already been taken
                results = conn.cursor().execute(sql_identity).fetchall()

            if len(results) != 0:
                non_valid_data['isSuccessful'] = False
                non_valid_data['NumberPlate'].append("This car's number plate has already been registered")
            else:
                sql = f"INSERT INTO Car (NumberPlate, Make, Model, Colour) VALUES ('{data['NumberPlate']}', '{data['Make']}', '{data['Model']}', '{data['Colour']}')"
                with self._get_connection() as conn:
                    print(sql)
                    conn.cursor().execute(sql)


        elif data['Data'] == 'Permit':
            with self._get_connection() as conn:
                sql_identity = f"SELECT * FROM Permit WHERE SYNumber = {int(data['SYNumber'])} and NumberPlate = '{data['NumberPlate']}'"
                #runs an sql command to check if the primary key has already been taken
                results = conn.cursor().execute(sql_identity).fetchall()

            if len(results) != 0:
                non_valid_data['isSuccessful'] = False
                non_valid_data['SYNumber'].append("This user and car already have a registered permit")
            else:
                if data['HasPermit'] == 'Yes':
                    permit_val = 1
                else:
                    permit_val = 0

                if len(data['ValidFrom']) == 0:
                    valid_from = None
                else:
                    valid_from = self.convert_date_to_ISO(data['ValidFrom'])

                if len(data['ValidUntil']) == 0:
                    valid_until = None
                else:
                    valid_until = self.convert_date_to_ISO(data['ValidUntil'])
                sql = f"INSERT INTO Permit (SYNumber, NumberPlate, hasPermit, ValidFrom, ValidUntil) VALUES ({int(data['SYNumber'])}, '{data['NumberPlate']}', {permit_val}, '{valid_from}', '{valid_until}')"
                with self._get_connection() as conn:
                    print(sql)
                    conn.cursor().execute(sql)
        return non_valid_data
