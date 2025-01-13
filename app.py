from flask import dashboards, Flask

app = Flask(__name__)

app.route("/autorisation", methods=['GET', 'POST'])
def autorisation():

app.route("/inventory")
def inventory():
  
app.route("/inventory/<orderer>")
def order():

