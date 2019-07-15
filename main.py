#!/usr/bin/env python
from flask import Flask, flash, redirect, render_template, request, url_for, send_from_directory
import flask


app = flask.Flask(__name__)

@app.route('/about2')
def show_about():
    return render_template('about2.html')

@app.route('/demo1')
def demo():
    return render_template('demo1.html')

@app.route('/')
def main_page():
    return render_template('main.html')

if __name__=='__main__':
    app.run(debug=True)