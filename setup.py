from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy


# Here get db config parameter from config.py file and initialize db

def setup_db(app):
    app.config.from_object('config')
    db = SQLAlchemy(app)
    migrate = Migrate(app, db)
    return db
