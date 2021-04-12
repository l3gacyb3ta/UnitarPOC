import os, uuid
from flask import Flask, flash, request, redirect, url_for, send_from_directory, render_template
from werkzeug.utils import secure_filename

def uuid_gen():
  return uuid.uuid4().hex

UPLOAD_FOLDER = 'icons'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'tif', 'tiff', 'svg'}

MEGABYTES = 5

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MEGABYTES * 1024 * 1024
app.config['SECRET_KEY'] = uuid_gen()

def allowed_file(filename):
  #Use the safer os.path.splitext instead of string manipulation
  return os.path.splitext(filename)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No icon in upload, maybe the file is corrupted?')
            return redirect(request.url)

        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename

        if file.filename == '':
            flash('No selected icon, maybe you forgot to select a file?')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = uuid_gen + os.path.splitext(file.filename)[1]
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('uploaded_icon',
                                    filename=filename))
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''

@app.route('/icons/<filename>')
def uploaded_icon(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               secure_filename(filename))

app.run(host='0.0.0.0', port=8080)