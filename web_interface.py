#!/usr/bin/python

from flask import Flask
from flask import request
html = ""
interface = Flask(__name__)
@interface.route("/")
def index():

    return interface.send_static_file('Evolution.html')
@interface.route('/names.json')
def ColNames():
	return interface.send_static_file('CensusColNames.json')
if __name__ == "__main__":

	interface.run(debug=True)
