from flask import Flask, render_template, request
import numpy as np
import pandas as pd
import torch
import flask_bm
app = Flask(__name__)

@app.route('/')
def student():
   return render_template('index.html')

@app.route('/submit',methods = ['POST', 'GET'])
def result():
   if request.method == 'POST':
      result = request.form
      tts=float(result['tts'])
      epochs=int(result['epochs'])
      nh=int(result['nh'])
      op=flask_bm.rec(tts,epochs,nh)
      return render_template("submit.html",result = op)

if __name__ == '__main__':
   app.run(port=8900)