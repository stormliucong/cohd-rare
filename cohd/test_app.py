from flask import Flask,render_template
from werkzeug.utils import redirect
app = Flask(__name__,template_folder='site')

@app.route("/")
def hello():
  return render_template("index.html")

if __name__ == "__main__":
  app.run(host='localhost',debug=True)