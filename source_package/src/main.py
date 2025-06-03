import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))  # DON'T CHANGE THIS !!!

from flask import Flask, render_template, session, g
from src.models import db
from src.routes import auth_bp, main_bp, admin_bp, context_bp
from datetime import datetime
from src.models.user import User

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_secret_key_change_in_production')
    
    # Use persistent database path for production environment
    db_path = os.path.join('/data', 'powerbi_portal.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Ensure the data directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    # Initialize database
    db.init_app(app)
    
    # Register blueprints
    app.register_blueprint(context_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp)
    
    # Add template global variables
    @app.context_processor
    def inject_now():
        return {'now': datetime.utcnow()}
    
    # Create database tables
    with app.app_context():
        db.create_all()
        # Create custom admin user
        admin = User.query.filter_by(username='zhihaiyan').first()
        if not admin:
            admin = User(username='zhihaiyan', email='zhihaiyan@example.com', is_admin=True)
            admin.set_password('abc')
            db.session.add(admin)
            db.session.commit()  # Explicitly commit the transaction
    
    # Error handling
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500
    
    return app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
