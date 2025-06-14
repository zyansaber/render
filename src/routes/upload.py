from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from werkzeug.utils import secure_filename
import os
from src.models import db
from src.models.upload import Upload
from functools import wraps
from flask import session

upload_bp = Blueprint('upload', __name__, url_prefix='/uploads')

# Login required decorator

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_id'):
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


@upload_bp.route('/', methods=['GET', 'POST'])
@login_required
def uploads():
    if request.method == 'POST':
        file = request.files.get('image')
        link = request.form.get('link')

        if file and file.filename:
            filename = secure_filename(file.filename)
            save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(save_path)
            upload = Upload(filename=filename, link=link)
            db.session.add(upload)
            db.session.commit()
            flash('Image uploaded successfully!', 'success')
            return redirect(url_for('upload.uploads'))
        else:
            flash('Please select a file to upload.', 'danger')

    uploads = Upload.query.order_by(Upload.uploaded_at.desc()).all()
    return render_template('uploads/list.html', uploads=uploads)
