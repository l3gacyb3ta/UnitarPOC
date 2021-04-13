import os, uuid
from flask import Flask, flash, request, redirect, url_for, send_from_directory, render_template
from werkzeug.utils import secure_filename

def uuid_gen():
  return uuid.uuid4().hex

UPLOAD_FOLDER = 'icons'
ALLOWED_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.tif', '.tiff', '.svg'}

MEGABYTES = 5

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MEGABYTES * 1024 * 1024
app.config['SECRET_KEY'] = uuid_gen()

users = {'test': ['9f67db172e2d4db99095bfc4cf23f527.jpg', 'hehe']}

def allowed_file(filename):
  #Use the safer os.path.splitext instead of string manipulation
  return os.path.splitext(filename)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No icon in upload, maybe the file is corrupted?')
            return redirect(request.url)

        uname = request.form['uname']
        
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename

        if file.filename == '':
            flash('No selected icon, maybe you forgot to select a file?')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = uuid_gen() + os.path.splitext(file.filename)[1]
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            users[uname] = users[uname] + [filename] if uname in users.keys() else [filename]

            return redirect(url_for('uploaded_icon',
                                    filename=filename))
    
    return render_template("upload.html")


@app.route('/icons/<filename>')
def uploaded_icon(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], secure_filename(filename))

@app.route('/set/<uname>/<icon>')
def set_favorite(uname, icon):
    if uname in users.keys():
        if icon == users[uname][0]:
            return redirect("/")
        else:
            if icon in users[uname]:
                x = users[uname].pop(icon)
                y = users[uname][0]
                users[uname][0] = icon
                users[uname].append(y)
                return redirect("/")
    else:
        return "ERROR NO ICONS"
    

@app.route('/user/<uname>')
def user_icons(uname):
    return render_template("user.html", icons = users[uname])

@app.route('/avatar/<uname>')
def get_best_avatar(uname):
    return send_from_directory(app.config['UPLOAD_FOLDER'], users[uname][0]) if uname in users.keys() else "ERROR USER NOT FOUND"

app.run(host='0.0.0.0', port=8080)