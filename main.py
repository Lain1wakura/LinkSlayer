from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hash.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Hash(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    intext = db.Column(db.String(30), nullable=False)
    finalhash = db.Column(db.String(30), nullable=False)

    def __repr__(self):
        return '<Hash %r>' % self.id


@app.route("/")
@app.route("/", methods=['POST', 'GET'])
def home():
    if request.method == 'POST':
        intext = request.form['intext']

        def getHash(striing, hashlenght=30):
            def receivingExistCodes(x):
                x += 256
                while not (((x <= 57) & (x >= 48)) | ((x <= 90) & (x >= 65)) | ((x <= 122) & (x >= 97))):
                    if x < 48:
                        x += 24
                    else:
                        x -= 47
                return x

            def getControlSum(striing):
                strlen = 0
                salt = 0

                if len(striing) % 2 != 0:
                    striing += 's'

                while (strlen < len(striing)):
                    salt += ord(striing[strlen])
                    strlen += 1

                return salt

            hash = ""
            minLen = 2
            realminLen = 0
            originalSalt = getControlSum(striing)
            originalLenghtStr = len(striing)
            while minLen <= hashlenght:
                minLen *= 2
                realminLen = minLen

            while minLen < originalLenghtStr:
                minLen *= 2

            if (minLen - originalLenghtStr) < minLen:
                minLen *= 2

            addCount = minLen - originalLenghtStr
            for i in range(addCount):
                striing += chr(receivingExistCodes(ord(striing[i]) + ord(striing[i + 1])))

            maxSalt = getControlSum(striing)
            maxLenghtStr = len(striing)

            while (len(striing) != realminLen):
                center = int(len(striing) / 2)
                for i in range(center):
                    hash += chr(receivingExistCodes(ord(striing[center - i]) + ord(striing[center + i])))
                striing = hash
                hash = ""

            rem = realminLen - hashlenght
            countcomprees = realminLen / rem

            for i in range(len(hash) < (hashlenght - 4)):
                if i % countcomprees == 0:
                    hash += chr(receivingExistCodes(ord(striing[i]) + ord(striing[i + 1])))
                else:
                    hash += striing[i]

            hash += chr(receivingExistCodes(originalSalt))
            hash += chr(receivingExistCodes(originalLenghtStr))
            hash += chr(receivingExistCodes(maxSalt))
            hash += chr(receivingExistCodes(maxLenghtStr))
            return hash

        finalhash = getHash(intext)

        hash = Hash(intext=intext, finalhash=finalhash)
        try:
            db.session.add(hash)
            db.session.commit()
            return redirect("/posts")
        except:
            return "Something went wrong :("

    else:
        return render_template("index.html")


@app.route("/posts")
def posts():
    hashs = Hash.query.all()
    return render_template("posts.html", hashs=hashs)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/<string:hashs>", methods=['POST', 'GET'])
def redir(hashs):
    hashs1 = Hash.query.filter_by(finalhash=hashs).first()
    s = 'https://' + hashs1.intext
    return redirect(s)


if __name__ == "__main__":
    app.run(debug=True)
