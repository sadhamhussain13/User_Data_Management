# from flask import Flask, render_template, flash, request, redirect, url_for
# from flask_mysqldb import MySQL



# # # OR (recommended: use os.urandom for randomness)
# # import os
# # app.secret_key = os.urandom(24)

# app = Flask(__name__)
# # Set a secret key (must be unique & secret)
# app.secret_key = "Hello@123"  # Simple key for demonstration

# # MySQL configurations
# app.config['MYSQL_HOST'] = 'localhost'
# app.config['MYSQL_USER'] = 'root'
# app.config['MYSQL_PASSWORD'] = ''
# app.config['MYSQL_DB'] = 'crud'
# app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
# mysql = MySQL(app)

# @app.route('/')
# def home():
#     con=mysql.connection.cursor()
#     sql="SELECT * FROM users"
#     con.execute(sql)
#     data=con.fetchall()
#     return render_template('home.html', users=data)

# # Add User
# @app.route('/addUser', methods=['GET','POST'])
# def addUser():
    
#     if request.method == 'POST':
#         name = request.form['name']
#         age = request.form['age']
#         contact = request.form['contact']
#         city = request.form['city']
#         con = mysql.connection.cursor()
#         sql = "INSERT INTO users(Name,Age,Contact,City) VALUES(%s,%s,%s,%s)"
#         con.execute(sql,(name,age,contact,city))
#         mysql.connection.commit()
#         flash("User Added Successfully")
#         return redirect(url_for('home'))
#     return render_template('addUser.html')


# # Edit User
# @app.route('/editUser/<string:id>', methods=['GET','POST'])
# def editUser(id):
#     con = mysql.connection.cursor()
#     if request.method == 'POST':
#         name = request.form['name']
#         age = request.form['age']
#         contact = request.form['contact']
#         city = request.form['city']
#         sql = "UPDATE users SET Name=%s, Age=%s, Contact=%s, City=%s WHERE ID=%s"
#         con.execute(sql,(name, age, contact, city, id))
#         mysql.connection.commit()
#         flash("User Updated Successfully")
#         return redirect(url_for('home'))
#     sql = "SELECT * FROM users WHERE ID=%s"
#     con.execute(sql,(id,))
#     data = con.fetchone()
#     return render_template('editUser.html', user=data)

# # Delete User
# @app.route('/deleteUser/<string:id>', methods=['GET','POST'])
# def deleteUser(id):
#     con = mysql.connection.cursor()
#     sql = "DELETE FROM users WHERE ID=%s"
#     con.execute(sql,(id,))
#     mysql.connection.commit()
#     flash("User Deleted Successfully")
#     return redirect(url_for('home'))

# if __name__ == "__main__":
#     app.run(debug=True)





from flask import Flask, render_template, flash, request, redirect, url_for
import psycopg
from psycopg.rows import dict_row
import os
from dotenv import load_dotenv
from validations import validate_user_form

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL")


def get_db_connection():
   try:
    return psycopg.connect(DATABASE_URL, row_factory=dict_row)
   except Exception as e:
       print("Database connection error:", e)
       return None       

# Home Route
@app.route('/')
def home():
   try: 
    con = get_db_connection()
    cur = con.cursor()
    cur.execute("SELECT * FROM users")
    data = cur.fetchall()
    return render_template('home.html', users=data)
   except Exception as e:
        flash("An error occurred while fetching users.")
        return render_template('home.html', users=None) 
   finally:
        if con:
            cur.close()
            con.close()
       

# Add User
@app.route('/addUser', methods=['GET', 'POST'])
def addUser(): 
    form_data = {'name':'', 'age':'', 'contact':'', 'city':''}
    alert_message = ""

    if request.method == 'POST':
        form_data['name'] = request.form['name']
        form_data['age'] = request.form['age']
        form_data['contact'] = request.form['contact']
        form_data['city'] = request.form['city']

     
        isValid, errors = validate_user_form(
            form_data['name'], form_data['age'], form_data['contact'], form_data['city']
        )

        if isValid:
           try:  
            con = get_db_connection()
            cur = con.cursor()
            sql = "INSERT INTO users(Name,Age,Contact,City) VALUES(%s,%s,%s,%s)"
            cur.execute(sql, (form_data['name'], form_data['age'], form_data['contact'], form_data['city']))
            con.commit()
            return redirect(url_for('home'))
           except Exception as e:
               if 'duplicate key value violates unique constraint' in str(e):
                     alert_message = "Contact number already exists!"
               else:
                     alert_message = "An error occurred while adding the user."
           finally:
                if con:
                    cur.close()
                    con.close()                
        else:
            alert_message = "\\n".join([f"{field.capitalize()}: {msg}" for field, msg in errors.items()])

    return render_template('addUser.html', form=form_data, alert_message=alert_message)

# Edit User
@app.route('/editUser/<string:id>', methods=['GET', 'POST'])
def editUser(id):
    con = get_db_connection()
    cur = con.cursor()
    alert_message = ""
    form_data = {'ID': id, 'Name':'', 'Age':'', 'Contact':'', 'City':''}

    if request.method == 'POST':
        form_data['Name'] = request.form['name']
        form_data['Age'] = request.form['age']
        form_data['Contact'] = request.form['contact']
        form_data['City'] = request.form['city']

        isValid, errors = validate_user_form(
            form_data['Name'], form_data['Age'], form_data['Contact'], form_data['City']
        )

        if isValid:
           try:
            sql = "UPDATE users SET Name=%s, Age=%s, Contact=%s, City=%s WHERE ID=%s"
            cur.execute(sql, (form_data['Name'], form_data['Age'], form_data['Contact'], form_data['City'], id))
            con.commit()
            cur.close()
            con.close()
            return redirect(url_for('home'))
           except Exception as e:
                if 'duplicate key value violates unique constraint' in str(e):
                        alert_message = "Contact number already exists!"
                else:
                        alert_message = "An error occurred while updating the user."
           finally:
                if con:
                    cur.close()
                    con.close()                           
        else:
            alert_message = "\\n".join([f"{field.capitalize()}: {msg}" for field, msg in errors.items()])
    else:
        sql = "SELECT * FROM users WHERE ID=%s"
        cur.execute(sql, (id,))
        user = cur.fetchone()
        if user:
           form_data['Name'] = user['name']
           form_data['Age'] = user['age']
           form_data['Contact'] = user['contact']
           form_data['City'] = user['city']

    cur.close()
    con.close()
    return render_template('editUser.html', form=form_data, alert_message=alert_message)



# Delete User
@app.route('/deleteUser/<string:id>', methods=['GET','POST'])
def deleteUser(id):
   try: 
    con = get_db_connection()
    cur = con.cursor()

    sql = "DELETE FROM users WHERE ID=%s"
    cur.execute(sql, (id,))
    con.commit()
    flash("User Deleted Successfully")
    return redirect(url_for('home'))
   except Exception as e:
       flash("An error occurred while deleting the user.")
       return redirect(url_for('home'))
   finally:
        if con:
            cur.close()
            con.close()

if __name__ == "__main__":
    app.run(debug=True)