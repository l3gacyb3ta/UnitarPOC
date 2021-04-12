import os, uuid
from flask import Flask, flash, request, redirect, url_for, send_from_directory, render_template
#from flask_assets import Bundle, Environment
from werkzeug.utils import secure_filename

#Constants
UPLOAD_FOLDER = 'icons'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'tif', 'tiff', 'svg'}
MEGABYTES = 5

#Utilities
def uuid_gen():
  #Generate a uuid
  return uuid.uuid4().hex

def allowed_file(filename):
  #Use the safer os.path.splitext instead of string manipulation
  return os.path.splitext(filename)[1].lower() in ALLOWED_EXTENSIONS

#Flask setup
app = Flask(__name__)
'''
assets = Environment(app)
css = Bundle("src/main.css", output="dist/main.css", filters="postcss")

#css build
assets.register("css", css)
css.build()
'''
#Flask config
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MEGABYTES * 1024 * 1024
app.config['SECRET_KEY'] = uuid_gen()


#Home page (For now)
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
                                    
    return render_template("upload.html")


#Icon server
@app.route('/icons/<filename>')
def uploaded_icon(filename):
  #Protects from getting files outside of icons.
  return send_from_directory(app.config['UPLOAD_FOLDER'], secure_filename(filename))

if __name__ == "__main__":
  app.run(host='0.0.0.0', port=8080)