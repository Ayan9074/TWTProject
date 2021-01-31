from flask import Flask, redirect, url_for, render_template, request
from flask_sqlalchemy import SQLAlchemy
import wikipedia
import matplotlib
import matplotlib.pyplot as plt
import json
from werkzeug.utils import secure_filename
import os
import speech_recognition as sr 
r = sr.Recognizer()
uploadfolder = 'TWTPROJECTFINAL/uploadfolder'
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'
app.config['SQLALCHEMY_TRAKC_MODIFICATIONS'] = False
app.config['uploadfolder'] = uploadfolder

db = SQLAlchemy(app)
class users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column("name", db.String(100))
    darkmode = db.Column("darkmode", db.String(100))
    userdatas = db.relationship('userdata', backref='mainuser')


class userdata(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    wikisearch = db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

def init_db():
  db.create_all()


@app.route('/', methods=["POST", "GET"])
def hello_world():
    if request.method == "POST":
        try:
            user = request.form["name"]
            darkmode = request.form["voice"]
            found_user = users.query.filter_by(name=user).first()
            if found_user:
                print('found')
                return redirect(url_for("homepage", usr=user, voice=darkmode))
            else:
                usr = users(name = user, darkmode=darkmode)
                db.session.add(usr)
                db.session.commit()
            return redirect(url_for("homepage", usr=user, darkmode=darkmode))
        except:
            user = request.form["name"]
            found_user = users.query.filter_by(name=user).first()
            if found_user:
                print('found')
                return redirect(url_for("homepage", usr=user, darkmode='no'))
            else:
                usr = users(name = user, darkmode='no')
                db.session.add(usr)
                db.session.commit()
            return redirect(url_for("homepage", usr=user, darkmode='no'))
    else:
        return render_template("testindex.html")

@app.route("/homepage+name<usr>+darkmode=<darkmode>")
def homepage(usr, darkmode):
    return render_template("mainpage.html")

@app.route("/wikisearch+name=<usr>+darkmode=<darkmode>", methods=["POST", "GET"])
def wikisearch(usr, darkmode):
    if request.method == 'POST':
        found_user = users.query.filter_by(name=usr).first()
        data = request.form['wiki']
        new_wikisearch = userdata(wikisearch = data, mainuser = found_user)
        db.session.add(new_wikisearch)
        db.session.commit()
        print(found_user.userdatas[0].wikisearch)
        wordlist = {}
        for i in range(0, len(found_user.userdatas)):
            try:
                wordlist[found_user.userdatas[i].wikisearch] = wikipedia.summary(wikipedia.suggest(found_user.userdatas[i].wikisearch))
            except:
                try:
                    wordlist[found_user.userdatas[i].wikisearch] = wikipedia.summary(found_user.userdatas[i].wikisearch)
                except:
                    wordlist[found_user.userdatas[i].wikisearch] = "WIKIPEDIA ERROR"
                
        return render_template("wikisearch.html", len=wordlist.items(), Pokemons = wordlist)
    else:
        wordlist = {}
        found_user = users.query.filter_by(name=usr).first()
        for i in range(0, len(found_user.userdatas)):
            try:
                wordlist[found_user.userdatas[i].wikisearch] = wikipedia.summary(wikipedia.suggest(found_user.userdatas[i].wikisearch))
            except:
                wordlist[found_user.userdatas[i].wikisearch] = wikipedia.summary(found_user.userdatas[i].wikisearch)
                
        return render_template("wikisearch.html", len=wordlist.items(), Pokemons = wordlist)

@app.route("/graphcreator", methods=["POST", "GET"])
def graphcreator():
    if request.method == "POST":
        return render_template("graphcreator.html")
    else:
        return render_template("graphcreator.html")

@app.route("/graphmaker+<listii>", methods=["POST", "GET"])
def graphmaker(listii):
    if request.method == "POST":
        return listii
    else:
        vals = json.loads(listii)
        title = vals["title"]
        yaxis = vals["yaxis"]
        xaxis = vals["xaxis"]
        lname = vals["lname"]
        xvals = vals["xvals"]
        xvals = [int(i) for i in xvals]
        yvals = vals["yvals"]
        xvals = [int(i) for i in yvals]
        fig = plt.figure()
        ax = plt.subplot(111)
        ax.plot(xvals, yvals, label=lname)
        plt.title(title)
        plt.xlabel(xaxis)
        plt.ylabel(yaxis)
        ax.legend()
        fig.savefig('TWTProjectcopy/static/plot.png')
        return render_template("graphmaker.html", listii=listii)

@app.route("/textospeach", methods=["POST", "GET"])
def textospeach():
    if request.method == "POST":
        file = request.files['file']
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['uploadfolder'], filename))
            with sr.AudioFile(app.config['uploadfolder'], filename) as source:
                # listen for the data (load audio to memory)
                audio_data = r.record(source)
                # recognize (convert from speech to text)
                text = r.recognize_google(audio_data)
                print(text)

        return render_template("speechtotext.html")
    else:
        return render_template("speechtotext.html")

if  __name__ == "__main__":
    init_db()
    app.run(debug=True)
    