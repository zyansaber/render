import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))  # DON'T CHANGE THIS !!!

from flask import Flask, render_template, session, g
from src.models import db
from src.routes import auth_bp, main_bp, admin_bp, context_bp
from datetime import datetime
from src.models.user import User
from src.models.page import Page


def create_app():
    app = Flask(__name__)

    # Secret key
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_secret_key_change_in_production')

    # Handle PostgreSQL URL correction (postgres -> postgresql)
    raw_db_url = os.environ.get("DATABASE_URL", "sqlite:///fallback.db")
    if raw_db_url.startswith("postgres://"):
        raw_db_url = raw_db_url.replace("postgres://", "postgresql://", 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = raw_db_url

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize database
    db.init_app(app)

    # Register blueprints
    app.register_blueprint(context_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp)

    # Template globals
    @app.context_processor
    def inject_now():
        return {'now': datetime.utcnow()}

    @app.context_processor
    def utility_functions():
        def get_user_navigation():
            pages = Page.query.filter_by(is_active=True).order_by(Page.display_order).all()
            return [{'id': p.id, 'name': p.title} for p in pages]
        return dict(get_user_navigation=get_user_navigation)

    return app


app = create_app()

# Optional: Only for local one-time table creation
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        admin = User.query.filter_by(username='zhihaiyan').first()
        if not admin:
            admin = User(username='zhihaiyan', email='zhihaiyan@example.com', is_admin=True)
            admin.set_password('abc')
            db.session.add(admin)
            db.session.commit()

    app.run(host='0.0.0.0', port=5000, debug=True)
