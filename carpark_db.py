import flask
import pyodbc

class CarParkDB():
    def __init__(self):
        conn_string_sch = (
            'Driver={SQL Server};'
            'Server=svr-cmp-01;'
            'Database=25svynarchT230;'
            'Trusted_Connection=yes;'
        )

        conn_string_home = (
            "Driver={SQL Server};"
            "Server=localhost\\SQLEXPRESS;"
            "Database=Climate_Flask;"
            "Trusted_Connection=yes;"
            "TrustServerCertificate=yes;"
        )

        try:
            pyodbc.connect(conn_string_sch, timeout=3)
            self.conn_string = conn_string_sch
        except:
            self.conn_string = conn_string_home


    def _get_connection(self):
        return pyodbc.connect(self.conn_string)
    
    def convert_date_to_ISO(self, date):
        ISO = date[-4:] + '-' + date[3:5] + '-' + date[:2]
        return ISO

    def query_database(self, filter_data):
        print("-------------------------------------------------------")
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
            car_query += f" NumberPlate = '{filter_data['reg']}' AND"
        if filter_data['make'] != '':
            car_query += f" Make = '{filter_data['make']}' AND"
        if filter_data['model'] != '':
            car_query += f" Model = '{filter_data['model']}' AND"
        
        if len(car_query) > 1:
            car_query = 'SELECT NumberPlate, Colour, PhotoPath FROM Car WHERE' + car_query
            car_query = car_query[:-4]
        else:
            car_query = 'SELECT NumberPlate, Colour, PhotoPath FROM Car'

#----------------------------------------------------------------------execute the sql statement------------------------
        with self._get_connection() as conn:
            sql = f"SELECT u.FirstName,u.LastName,u.Age,c.NumberPlate,c.Colour,p.HasPermit,u.UserType,p.ValidFrom,p.ValidUntil,u.PhotoPath,c.PhotoPath FROM ({user_query}) u JOIN ({permit_query}) p ON u.SYNumber = p.SYNumber JOIN ({car_query}) c ON p.NumberPlate = c.NumberPlate;"
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
                        'Id': i
            })

        return data
