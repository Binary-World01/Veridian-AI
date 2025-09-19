import os
import time
import requests
import io
import random
from flask import (Flask, render_template, request, redirect, url_for,
                   flash, session, send_from_directory, jsonify)
from flask_login import (LoginManager, login_user, logout_user,
                         login_required, current_user)
from flask_socketio import SocketIO
from dotenv import load_dotenv
from PIL import Image

load_dotenv()
app = Flask(__name__)
socketio = SocketIO(app)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['USER_DATA_FOLDER'] = os.path.abspath('user_data')
app.config['PUBLIC_IMAGES_FOLDER'] = os.path.abspath('public_images')

from models import db, User, Generation
db.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

PROHIBITED_KEYWORDS = ['blood', 'gore', 'nsfw', 'explicit', 'violence']

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def save_image(image_bytes, folder, filename):
    os.makedirs(folder, exist_ok=True)
    filepath = os.path.join(folder, filename)
    try:
        image = Image.open(io.BytesIO(image_bytes))
        image.save(filepath)
        return filepath
    except Exception as e:
        print(f"Error saving image: {e}")
        return None

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form.get('email')).first()
        if user:
            flash('Email address already exists.')
            return redirect(url_for('register'))
        new_user = User(email=request.form.get('email'), username=request.form.get('username'))
        new_user.set_password(request.form.get('password'))
        db.session.add(new_user)
        db.session.commit()
        flash('Account created successfully! Please log in.')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form.get('email')).first()
        if user and user.check_password(request.form.get('password')):
            login_user(user)
            return redirect(url_for('homepage'))
        flash('Invalid email or password.')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('homepage'))

@app.route('/')
def homepage():
    initial_images = Generation.query.filter_by(status='public', is_deleted_by_user=False).order_by(Generation.timestamp.desc()).limit(20).all()
    return render_template('homepage.html', images=initial_images)

@app.route('/gallery')
def public_gallery():
    public_images = Generation.query.filter_by(status='public', is_deleted_by_user=False).order_by(Generation.timestamp.desc()).all()
    return render_template('public_gallery.html', images=public_images)

@app.route('/dashboard')
@login_required
def dashboard():
    user_creations = Generation.query.filter_by(author=current_user, is_deleted_by_user=False).order_by(Generation.timestamp.desc()).all()
    return render_template('dashboard.html', creations=user_creations)

@app.route('/settings', methods=['GET'])
@login_required
def settings():
    return render_template('settings.html')

@app.route('/image/<int:image_id>')
@login_required
def get_user_image(image_id):
    image_record = Generation.query.get_or_404(image_id)
    if current_user.id == image_record.user_id or current_user.is_admin:
        filename = os.path.basename(image_record.image_path)
        return send_from_directory(app.config['USER_DATA_FOLDER'], filename)
    return "Access Forbidden", 403

@app.route('/generate', methods=['POST'])
@login_required
def generate():
    prompt = request.form.get('prompt')
    ratio = request.form.get('ratio', '1:1')
    visibility = request.form.get('visibility', 'private')

    if current_user.parental_control_enabled:
        if any(word in prompt.lower() for word in PROHIBITED_KEYWORDS):
            flash('Your prompt contains restricted words due to parental controls.')
            return redirect(url_for('homepage'))

    ai_api_endpoint = os.getenv('AI_API_ENDPOINT')
    if not ai_api_endpoint:
        flash("AI Engine endpoint is not configured. Please start the Colab notebook and set the URL in the .env file.")
        return redirect(url_for('homepage'))
        
    try:
        payload = {'prompt': prompt, 'ratio': ratio}
        response = requests.post(ai_api_endpoint, json=payload, headers={'Content-Type': 'application/json'}, timeout=300)

        if response.status_code == 200:
            filename = f"{current_user.id}_{int(time.time())}.png"
            filepath = save_image(response.content, app.config['USER_DATA_FOLDER'], filename)
            
            new_gen = Generation(prompt=prompt, style_type=ratio, image_path=filepath, author=current_user)
            
            if visibility == 'public':
                public_filename = f"pub_{filename}"
                public_filepath_abs = os.path.join(app.config['PUBLIC_IMAGES_FOLDER'], public_filename)
                public_filepath_rel = os.path.join('public_images', public_filename)
                
                with open(filepath, 'rb') as f_orig:
                    with open(public_filepath_abs, 'wb') as f_pub:
                        f_pub.write(f_orig.read())

                new_gen.status = 'public'
                new_gen.public_image_path = public_filepath_rel
                
                socketio.emit('new_image', {
                    'path': new_gen.public_image_path,
                    'prompt': new_gen.prompt,
                    'author': current_user.username
                })

            db.session.add(new_gen)
            db.session.commit()
            flash("Image generated successfully!")
        else:
            flash(f"Error from AI Engine (Status {response.status_code}): {response.text}")
    except requests.exceptions.RequestException as e:
        flash(f"Could not connect to the AI Engine. Error: {e}")
    
    return redirect(url_for('dashboard'))

@app.route('/change-password', methods=['POST'])
@login_required
def change_password():
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')

    if not current_user.check_password(current_password):
        flash('Your current password was incorrect.')
        return redirect(url_for('settings'))

    if new_password != confirm_password:
        flash('New passwords do not match.')
        return redirect(url_for('settings'))
    
    current_user.set_password(new_password)
    db.session.commit()
    flash('Your password has been updated successfully.')
    return redirect(url_for('settings'))

@app.route('/toggle-parental-controls', methods=['POST'])
@login_required
def toggle_parental_controls():
    user = User.query.get(current_user.id)
    user.parental_control_enabled = 'parental_control' in request.form
    db.session.commit()
    flash('Parental control settings updated.')
    return redirect(url_for('settings'))

@app.route('/become-admin', methods=['POST'])
@login_required
def become_admin():
    submitted_code = request.form.get('security_code')
    correct_code = os.getenv('ADMIN_SECURITY_CODE')

    if submitted_code and submitted_code == correct_code:
        user = User.query.get(current_user.id)
        user.is_admin = True
        db.session.commit()
        flash("Success! You have been granted administrator privileges.")
    else:
        flash("The security code you entered was incorrect.")
    
    return redirect(url_for('settings'))

@app.route('/delete-image/<int:image_id>', methods=['POST'])
@login_required
def delete_image(image_id):
    image = Generation.query.get_or_404(image_id)
    if image.author != current_user:
        return "Access Forbidden", 403
    image.is_deleted_by_user = True
    db.session.commit()
    flash('Image moved to trash.')
    return redirect(url_for('dashboard'))

@app.route('/request-download/<int:image_id>', methods=['POST'])
@login_required
def request_download(image_id):
    image = Generation.query.get_or_404(image_id)
    if image.author != current_user:
        return "Access Forbidden", 403
    image.download_status = 'pending'
    db.session.commit()
    flash('Download request sent to administrator.')
    return redirect(url_for('dashboard'))

@app.route('/download-image/<int:image_id>')
@login_required
def download_image(image_id):
    image = Generation.query.get_or_404(image_id)
    if image.author == current_user and image.download_status == 'approved':
        filename = os.path.basename(image.image_path)
        return send_from_directory(app.config['USER_DATA_FOLDER'], filename, as_attachment=True)
    flash('You do not have permission to download this file.')
    return redirect(url_for('dashboard'))

@app.route('/admin/users')
@login_required
def admin_users():
    if not current_user.is_admin:
        return "Access Forbidden", 403
    all_users = User.query.all()
    return render_template('admin/users.html', users=all_users)

@app.route('/admin/user/<int:user_id>')
@login_required
def admin_user_detail(user_id):
    if not current_user.is_admin:
        return "Access Forbidden", 403
    user = User.query.get_or_404(user_id)
    creations = Generation.query.filter_by(author=user).order_by(Generation.timestamp.desc()).all()
    return render_template('admin/user_detail.html', user=user, creations=creations)

@app.route('/admin/requests')
@login_required
def admin_requests():
    if not current_user.is_admin:
        return "Access Forbidden", 403
    pending_requests = Generation.query.filter_by(download_status='pending').all()
    return render_template('admin/requests.html', requests=pending_requests)

@app.route('/admin/approve-download/<int:image_id>', methods=['POST'])
@login_required
def approve_download(image_id):
    if not current_user.is_admin:
        return "Access Forbidden", 403
    image = Generation.query.get_or_404(image_id)
    image.download_status = 'approved'
    db.session.commit()
    return redirect(url_for('admin_requests'))

@app.route('/admin/delete-image/<int:image_id>', methods=['POST'])
@login_required
def admin_delete_image(image_id):
    if not current_user.is_admin:
        return "Access Forbidden", 403
    image = Generation.query.get_or_404(image_id)
    try:
        if os.path.exists(image.image_path):
            os.remove(image.image_path)
        if image.public_image_path and os.path.exists(os.path.join('static', image.public_image_path)):
            os.remove(os.path.join('static', image.public_image_path))
    except Exception as e:
        flash(f"Error deleting files: {e}")
    db.session.delete(image)
    db.session.commit()
    flash('Image has been permanently deleted.')
    return redirect(url_for('admin_user_detail', user_id=image.user_id))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)