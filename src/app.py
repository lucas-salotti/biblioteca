import os

import click
from datetime import datetime, timedelta
from flask import Flask, current_app
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy as sa
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)
migrate = Migrate()

class User(db.Model):
    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True)
    name: Mapped[str] = mapped_column(sa.String, nullable=False)
    email: Mapped[str] = mapped_column(sa.String, nullable=False, unique=True)

class Book(db.Model):
    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True) 
    title: Mapped[str] = mapped_column(sa.String, nullable=False)
    author: Mapped[str] = mapped_column(sa.String, nullable=False)

class Loan(db.Model):
    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(sa.ForeignKey("user.id"))
    book_id: Mapped[int] = mapped_column(sa.ForeignKey("book.id"))
    loan_date: Mapped[datetime] = mapped_column(sa.DateTime, server_default=sa.func.now())
    return_date: Mapped[datetime] = mapped_column(sa.DateTime)
    is_returned: Mapped[bool] = mapped_column(sa.Boolean, default=False, nullable=False)

@click.command("init-db")
def init_db_command():
    global db
    with current_app.app_context():
        db.create_all()
    click.echo("Inicializado.")

def create_app(test_config=None):
    app = Flask(__name__,instance_relative_config=True)
    app.config.from_mapping(
        SQLALCHEMY_DATABASE_URI = "sqlite:///db_biblioteca.sqlite"
    )

    if test_config is None: 
        app.config.from_pyfile("config.py", silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    app.cli.add_command(init_db_command)

    db.init_app(app)
    migrate.init_app(app, db)

    # from src.controllers import user

    # app.register_blueprint(user.app)
    return app
