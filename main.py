from flask import Flask, render_template, request
import sqlite3
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/travel')
def hello_world():
    latitude = []
    longitude = []
    ename = []
    country = request.args.get('country')
    if (country != 'Spain' and country != 'spain' and country != "Switzerland" and country != "switzerland" and country != "hungary" and country != "Hungary"):
        return render_template("index.html", message = "sorry, your input country is invalid.")

    conn = sqlite3.connect("travelTest.db")
    cur = conn.cursor()
    datalist = []
    sql = "select * from travel where country ='"+country+"'"
    data = cur.execute(sql)
    for item in data:
        datalist.append(item)
        name = str(item[4]).replace("(", "")
        name = name.replace(")", "")
        ename.append(name)
        longitude.append(item[10])
        latitude.append(item[11])
    cur.close()
    conn.close()
    name = country + '.jpg'
    return render_template("travel.html", image_name=name, places=datalist, ename=ename, latitude=latitude, longitude=longitude)


if __name__ == "__main__":
    app.run(debug=True)