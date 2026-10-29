from pathlib import Path

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev-key-change-in-production",
        SQLALCHEMY_DATABASE_URI=f"sqlite:///{Path(app.instance_path) / 'logistica.sqlite'}",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    if test_config:
        app.config.update(test_config)

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    db.init_app(app)

    from app.routes import bp

    app.register_blueprint(bp)

    with app.app_context():
        from app import models

        db.create_all()
        if not models.Pedido.query.first():
            models.seed_demo_data()

    return app
