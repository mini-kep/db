from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
# EP: for production we must change the line below to use 'config.ProductionConfig'
#     most likely the file will be put in .gitignore, so that different versions live at local and prod environments
app.config.from_object('config.DevelopmentConfig')
db = SQLAlchemy(app)
