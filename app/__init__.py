from flask import Flask
from .extensions import mongo
from app.webhook.routes import webhook


# Creating our flask app
def create_app():

    app = Flask(__name__)
    # registering all the blueprints
    app.register_blueprint(webhook)
    #configuring db
    app.config["MONGO_URI"] = "mongodb://localhost:27017/myDatabase"
    mongo.init_app(app) 
    return app
