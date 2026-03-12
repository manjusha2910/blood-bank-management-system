from flask import Flask, render_template, request, redirect, session
import mysql.connector

app = Flask(__name__)
app.secret_key = "supersecretkey"


# ---------- DATABASE CONNECTION ----------
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Kushwanth@7",
        database="blood_bank_db"
    )


# ---------- LOGIN ROUTE ----------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "admin123":
            session["user"] = username
            return redirect("/dashboard")
        else:
            return render_template("login.html", error="Invalid Username or Password ❌")

    return render_template("login.html")

# ---------- DASHBOARD ----------
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")

    message = request.args.get("message")
    return render_template("dashboard.html", message=message)

#-----------ADD----------------
@app.route("/add", methods=["GET", "POST"])
def add():
    if "user" not in session:
        return redirect("/")

    if request.method == "POST":
        name = request.form["name"]
        age = request.form["age"]
        blood_group = request.form["blood_group"]
        city = request.form["city"]

        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO donor (name, age, blood_group, city) VALUES (%s, %s, %s, %s)",
            (name, age, blood_group, city)
        )
        connection.commit()
        connection.close()

        return redirect("/dashboard?message=Donor Added Successfully")

    return render_template("add.html")
#--------Update-------------
@app.route("/update", methods=["GET", "POST"])
def update():
    if "user" not in session:
        return redirect("/")

    connection = get_connection()
    cursor = connection.cursor()

    if request.method == "POST":
        donor_id = request.form["donor_id"]
        name = request.form["name"]
        age = request.form["age"]
        blood_group = request.form["blood_group"]
        city = request.form["city"]

        cursor.execute("""
            UPDATE donor
            SET name=%s, age=%s, blood_group=%s, city=%s
            WHERE donor_id=%s
        """, (name, age, blood_group, city, donor_id))

        connection.commit()
        connection.close()

        return redirect("/dashboard?message=Donor Updated Successfully")

    # Fetch all donors to show in dropdown
    cursor.execute("SELECT donor_id, name FROM donor")
    donors = cursor.fetchall()
    connection.close()

    return render_template("update.html", donors=donors)

#----------------DELETE-----------------
@app.route("/delete", methods=["GET", "POST"])
def delete():
    if "user" not in session:
        return redirect("/")

    connection = get_connection()
    cursor = connection.cursor()

    if request.method == "POST":
        donor_id = request.form["donor_id"]

        try:
            # First delete related donation records
            cursor.execute("DELETE FROM donation WHERE donor_id = %s", (donor_id,))

            # Then delete donor
            cursor.execute("DELETE FROM donor WHERE donor_id = %s", (donor_id,))

            connection.commit()

        except Exception as e:
            connection.rollback()
            connection.close()
            return f"Error occurred: {e}"

        connection.close()
        return redirect("/dashboard?message=Donor Deleted Successfully")

    cursor.execute("SELECT donor_id, name FROM donor")
    donors = cursor.fetchall()
    connection.close()

    return render_template("delete.html", donors=donors)
# ---------- QUERY ROUTE (Protected) ----------
@app.route("/query/<int:query_id>")
def run_query(query_id):

    if "user" not in session:
        return redirect("/")

    connection = get_connection()
    cursor = connection.cursor()

    if query_id == 1:
        cursor.execute("SELECT * FROM donor")

    elif query_id == 2:
        cursor.execute("SELECT * FROM hospital")

    elif query_id == 3:
        cursor.execute("SELECT COUNT(*) AS Total_Donors FROM donor")

    elif query_id == 4:
        cursor.execute("SELECT MAX(age) AS Oldest_Donor FROM donor")

    elif query_id == 5:
        cursor.execute("SELECT SUM(units) AS Total_Units_Donated FROM donation")

    elif query_id == 6:
        cursor.execute("""
            SELECT d.name, b.name AS Blood_Bank, donation.units
            FROM donation
            JOIN donor d ON donation.donor_id = d.donor_id
            JOIN blood_bank b ON donation.blood_bank_id = b.reg_id
        """)

    elif query_id == 7:
        cursor.execute("SELECT blood_group, COUNT(*) FROM donor GROUP BY blood_group")

    elif query_id == 8:
        cursor.execute("SELECT name FROM donor WHERE age > (SELECT AVG(age) FROM donor)")

    elif query_id == 9:
        cursor.execute("SELECT MIN(age) FROM donor")

    elif query_id == 10:
        cursor.execute("SELECT AVG(age) FROM donor")

    elif query_id == 11:
        cursor.execute("SELECT * FROM donor WHERE city = 'Hyderabad'")

    elif query_id == 12:
        cursor.execute("SELECT * FROM donor WHERE age BETWEEN 20 AND 30")

    elif query_id == 13:
        cursor.execute("SELECT * FROM donor WHERE name LIKE 'R%'")

    elif query_id == 14:
        cursor.execute("SELECT DISTINCT blood_group FROM donor")

    elif query_id == 15:
        cursor.execute("""
            SELECT d.name, SUM(donation.units)
            FROM donation
            JOIN donor d ON donation.donor_id = d.donor_id
            GROUP BY d.name
        """)

    elif query_id == 16:
        cursor.execute("""
            SELECT d.name, SUM(donation.units)
            FROM donation
            JOIN donor d ON donation.donor_id = d.donor_id
            GROUP BY d.name
            HAVING SUM(donation.units) > 2
        """)

    elif query_id == 17:
        cursor.execute("""
            SELECT a.name, h.name
            FROM acceptor a
            JOIN hospital h ON a.hospital_id = h.hospital_id
        """)

    elif query_id == 18:
        cursor.execute("""
            SELECT b.name, SUM(donation.units)
            FROM donation
            JOIN blood_bank b ON donation.blood_bank_id = b.reg_id
            GROUP BY b.name
            ORDER BY SUM(donation.units) DESC
            LIMIT 1
        """)

    elif query_id == 19:
        cursor.execute("""
            SELECT d.name, donation.units
            FROM donor d
            LEFT JOIN donation ON d.donor_id = donation.donor_id
        """)

    elif query_id == 20:
        cursor.execute("SELECT * FROM donor ORDER BY age DESC")

    elif query_id == 21:
        cursor.execute("""
            SELECT name FROM donor
            WHERE EXISTS (SELECT * FROM donation WHERE donation.donor_id = donor.donor_id)
        """)

    elif query_id == 22:
        cursor.execute("""
            SELECT name FROM donor
            WHERE NOT EXISTS (SELECT * FROM donation WHERE donation.donor_id = donor.donor_id)
        """)

    elif query_id == 23:
        cursor.execute("SELECT name, age FROM donor WHERE age = (SELECT MAX(age) FROM donor)")

    elif query_id == 24:
        cursor.execute("""
            SELECT name,
            CASE
                WHEN age < 25 THEN 'Young'
                WHEN age BETWEEN 25 AND 30 THEN 'Adult'
                ELSE 'Senior'
            END
            FROM donor
        """)

    elif query_id == 25:
        cursor.execute("""
            SELECT * FROM donor
            WHERE donor_id IN (SELECT donor_id FROM donation WHERE units > 2)
        """)

    elif query_id == 26:
        cursor.execute("SELECT name FROM donor UNION SELECT name FROM acceptor")

    elif query_id == 27:
        cursor.execute("""
            SELECT d.name, donation.units
            FROM donor d
            JOIN donation ON d.donor_id = donation.donor_id
            WHERE donation.units > (SELECT AVG(units) FROM donation)
        """)

    elif query_id == 28:
        cursor.execute("SELECT * FROM donation ORDER BY donation_date DESC")

    elif query_id == 29:
        cursor.execute("SELECT COUNT(*) FROM donation")

    elif query_id == 30:
        cursor.execute("SELECT blood_group, COUNT(*) FROM donor GROUP BY blood_group")

    elif query_id == 31:
        cursor.execute("SELECT * FROM hospital ORDER BY name")

    elif query_id == 32:
        cursor.execute("SELECT * FROM blood_bank ORDER BY location")

    elif query_id == 33:
        cursor.execute("SELECT COUNT(*) FROM hospital")

    elif query_id == 34:
        cursor.execute("SELECT COUNT(*) FROM blood_bank")

    elif query_id == 35:
        cursor.execute("SELECT MAX(units) FROM donation")

    elif query_id == 36:
        cursor.execute("SELECT MIN(units) FROM donation")

    elif query_id == 37:
        cursor.execute("SELECT AVG(units) FROM donation")

    elif query_id == 38:
        cursor.execute("SELECT * FROM donor ORDER BY name")

    elif query_id == 39:
        cursor.execute("SELECT * FROM acceptor ORDER BY name")

    elif query_id == 40:
        cursor.execute("SELECT donation_id, units, donation_date FROM donation")

    elif query_id == 41:
        cursor.execute("SELECT * FROM donor WHERE age > 25")

    elif query_id == 42:
        cursor.execute("SELECT * FROM donor WHERE age < 30")

    elif query_id == 43:
        cursor.execute("SELECT * FROM donor WHERE blood_group = 'O+'")

    elif query_id == 44:
        cursor.execute("SELECT * FROM donor WHERE blood_group = 'A+'")

    elif query_id == 45:
        cursor.execute("SELECT * FROM acceptor WHERE blood_group = 'A+'")

    elif query_id == 46:
        cursor.execute("SELECT donor_id, COUNT(*) FROM donation GROUP BY donor_id")

    elif query_id == 47:
        cursor.execute("SELECT blood_bank_id, SUM(units) FROM donation GROUP BY blood_bank_id")

    elif query_id == 48:
        cursor.execute("SELECT hospital_id, COUNT(*) FROM acceptor GROUP BY hospital_id")

    elif query_id == 49:
        cursor.execute("SELECT * FROM donation WHERE units >= 2")

    elif query_id == 50:
        cursor.execute("SELECT * FROM donor WHERE city = 'Vijayawada'")

    else:
        connection.close()
        return "Invalid Query"

    data = cursor.fetchall()
    columns = [col[0] for col in cursor.description]
    connection.close()

    return render_template("index.html", data=data, columns=columns)

# ---------- LOGOUT ----------
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)