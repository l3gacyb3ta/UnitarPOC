import os, uuid, pickle
from hashlib import sha1
from flask import Flask, flash, request, redirect, url_for, send_from_directory, render_template
from werkzeug.utils import secure_filename

# Constants!
UPLOAD_FOLDER = 'icons'
ALLOWED_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.tif', '.tiff', '.svg'}

# Maximum upload size
MEGABYTES = 5

# uuid generation shortcut
def uuid_gen():
  return uuid.uuid4().hex

# Determin if a file can be uploaded
def allowed_file(filename):
  # Use the safer os.path.splitext instead of string manipulation
  return os.path.splitext(filename)[1].lower() in ALLOWED_EXTENSIONS

def hash(data):
    return sha1(data).hexdigest()

# Configure flask
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MEGABYTES * 1024 * 1024
app.config['SECRET_KEY'] = uuid_gen()

users = {'test': ['9f67db172e2d4db99095bfc4cf23f527.jpg', 'hehe']}

# File hashing index:
files = {}

for (dirpath, dirnames, filenames) in os.walk('icons'):
    for filename in filenames:
        path = os.sep.join([dirpath, filename])
        files[hash(open(path, 'rb').read())] = filename

print(files.keys())

# Basic index
@app.route('/')
def index():
    return render_template("index.html")

# Fancy upload stuff!
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

            path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            
            hashed_file = hash(open(path, 'rb').read())
            # Make sure someone hasn't already uploaded the file the new user is uploading
            if hashed_file in files.keys():
                os.remove(path) # Delete the new file (This is the best I could find)
                users[uname] = users[uname] + [files[hashed_file]] if uname in users.keys() else [files[hashed_file]] # Adding to the user's list of icons
                return redirect("user/" + uname) 

            else:
                # If it's a new file, add the hash
                files[hashed_file] = filename

            users[uname] = users[uname] + [filename] if uname in users.keys() else [filename] # Adding to the user's list of icons

            # Give you your user page
            return redirect("user/" + uname) 
    
    return render_template("upload.html")

# Return an icon based on it's filename
@app.route('/icons/<filename>')
def uploaded_icon(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], secure_filename(filename))

# Set the favorite 
@app.route('/set/<uname>/<icon>')
def set_favorite(uname, icon):
    # If the user exists then do stuff
    if uname in users.keys():
        # If it's aleready set, then don't do anything
        if icon == users[uname][0]:
            return redirect("/")

        else:
            # Other wise, if check for the icon
            if icon in users[uname]:
                x = users[uname].remove(icon)
                y = users[uname][0]
                users[uname][0] = icon
                users[uname].append(y)
                return redirect("/")
            # If not, then display an error
            else:
                return "ERROR NOT USER ICON"
            
    else:
        return "ERROR NO USER"
    

# Chose the best icon
@app.route('/user/<uname>')
def user_icons(uname):
    return render_template("user.html", icons = users[uname], uname=uname)

# Get the number 1 (0) avatar from user
@app.route('/avatar/<uname>')
def get_best_avatar(uname):
    return send_from_directory(app.config['UPLOAD_FOLDER'], users[uname][0]) if uname in users.keys() else "ERROR USER NOT FOUND"

# Pickle save and load, acessed using /save and /load

@app.route('/save')
def save():
    pickle.dump(users, open( "save.p", "wb" ) )

@app.route('/load')
def load():
    users = pickle.load( open( "save.p", "rb" ) )

app.run(host='0.0.0.0', port=8080)