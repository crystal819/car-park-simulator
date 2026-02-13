import pyodbc

class ConnString():
    def connstr(self):
        conn_string_sch = (
            'Driver={SQL Server};'
            'Server=svr-cmp-01;'
            'Database=25svynarchT230;'
            'Trusted_Connection=yes;'
        )

        conn_string_home = (
            "Driver={SQL Server};"
            "Server=localhost\\SQLEXPRESS;"
            "Database=collyers_car_park;"
            "Trusted_Connection=yes;"
            "TrustServerCertificate=yes;"
        )

        try:
            pyodbc.connect(conn_string_sch, timeout=3)
            self.conn_string = conn_string_sch
        except:
            self.conn_string = conn_string_home
        
        return self.conn_string
    
    def _get_connection(self):
        return pyodbc.connect(self.conn_string)
    
    def build_database(self):
        with open('masterSQL.txt', 'r') as f:
            sql = f.read()
        with self._get_connection() as conn:
            conn.cursor().execute(sql)


if __name__ == '__main__':
    x = ConnString()
    x.connstr()
    x.build_database()

        