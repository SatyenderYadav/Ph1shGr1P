from flask import Flask, render_template, redirect,session,  request, Response, url_for,  flash
import re,os,random,string
from datetime import timedelta,datetime
from werkzeug.utils import secure_filename
import dotenv 

dotenv_file = os.path.join("./.env")
if os.path.isfile(dotenv_file):
    dotenv.load_dotenv(dotenv_file)


UPLOAD_FOLDER = '/home/l3v1ath4n/Documents/eml/files'
ALLOWED_EXTENSIONS = {'eml'}
SECRET_KEY = os.environ['SECRET_KEY']


app=Flask(__name__,static_url_path="/frontend/static/", static_folder="../frontend/static", template_folder='../frontend/templates')
app.permanent_session_lifetime = timedelta(seconds=2)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER