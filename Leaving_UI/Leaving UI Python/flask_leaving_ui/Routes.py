from flask import Flask, render_template, redirect, url_for, Response, session
from flask_leaving_ui import app


@app.route("/")
@app.route("/home")
def home_page():
    return render_template('qr_leaving.html')


@app.route('/qr_leaving_success')
def qr_success():
    return render_template('qr_leaving_success.html')


@app.route('/qr_leaving_failed')
def qr_failed():
    return render_template('qr_leaving_failed.html')
