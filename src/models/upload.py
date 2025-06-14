from src.models import db

class Upload(db.Model):
    __tablename__ = 'uploads'

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    link = db.Column(db.String(255), nullable=True)
    uploaded_at = db.Column(db.DateTime, server_default=db.func.now())

    def __repr__(self):
        return f'<Upload {self.filename}>'
