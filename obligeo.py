import os
from flask import Flask, render_template, request, redirect, url_for, send_file, send_from_directory
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'temp_uploads'
ALLOWED_EXTENSIONS = {'txt'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/')
def index():
    return render_template('index.html')

#wczytanie danych do konwersji
@app.route('/konwersja')
def konwersja():
    return render_template('wczytanie.html')

@app.route('/konwersja_w', methods =['GET', 'POST'])
def konwersja_w():
    if request.method == 'POST':
        f = request.files['file']
        filename = secure_filename(f.filename)
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        zrodlo = open(os.path.join(app.config['UPLOAD_FOLDER'], filename)).readlines() #konwersja pliku źrodłowego
        cel = open(os.path.join(app.config['UPLOAD_FOLDER'], filename+'_Am.txt'),'w')
        for s in zrodlo:
             values = s.split("\t")   #dzieli plik tekstowy względem tab
             #print("Nr:"+values[0] + ", X:"+ values[1] + ", y:"+ values[2] + ", H:"+ values[3]) #wyświetla zawartość pliku
             h = float(values[3])+0.070        #przeliczenie wysokości - wartość różnicy może być zmieniona
             cel.write(s.replace(values[3],str(h)))
        cel.close()
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename+'_Am.txt', as_attachment=True)
        

@app.route('/pobranie/<filename>', methods= ['GET'])
def pobranie(filename):
    return render_template('pobieranie.html', value=filename)




if __name__ == '__main__':
   app.run(debug = True)
