import os
import pandas as pd
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
        roznica=request.form['roznica']
        f = request.files['file']
        filename = secure_filename(f.filename)
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        zrodlo = open(os.path.join(app.config['UPLOAD_FOLDER'], filename)).readlines() #konwersja pliku źrodłowego
        cel = open(os.path.join(app.config['UPLOAD_FOLDER'], filename+'_Am.txt'),'w')
        for s in zrodlo:
             values = s.split("\t")   #dzieli plik tekstowy względem tab
             #print("Nr:"+values[0] + ", X:"+ values[1] + ", y:"+ values[2] + ", H:"+ values[3]) #wyświetla zawartość pliku
             h = float(values[3])+float(roznica)       #przeliczenie wysokości - wartość różnicy może być zmieniona
             cel.write(s.replace(values[3],str(h)))
        cel.close()
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename+'_Am.txt', as_attachment=True)
    
#wczytanie danych do zmiany nr x y h        
@app.route('/zmiana')
def zmiana():
    return render_template('zmiana.html')

@app.route('/zmiananrxyh', methods =['GET', 'POST'])
def zmiananrxyh():
    if request.method == 'POST':
        f = request.files['file']
        filename = secure_filename(f.filename)
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        #raport=['lista plików z błędami danych']   #utworzenie listy na raport błedów
        #data = pd.read_csv(f, sep='\t', header=None)  #utworzenie dataframe z pliku z pikietami
        """
            try:
                data[1]=data[1].astype(float)   #kontrola czy wsp to liczby zmiennoprzecinkowe float64   
            except:                                 #jeśli błąd wyświetl komunikat i zapisz nazwę blędnego pliku
                #print('BŁĄD DANYCH W PLIKU - WSP X '+n)
                blad=n+' blad wsp X'
                raport.append(blad)
            try:
                data[2]=data[2].astype(float)
            except:                                 #jeśli błąd wyświetl komunikat i zapisz nazwę blędnego pliku
                #print('BŁĄD DANYCH W PLIKU - WSP Y '+n)
                blad2=n+' błąd wsp y'
                raport.append(blad2)
            try:
                data[3]=data[3].astype(float)
            except:                                 #jeśli błąd wyświetl komunikat i zapisz nazwę blędnego pliku
                #print('BŁĄD DANYCH W PLIKU - WSP H '+n)
                blad3=n+' bład wsp h'
                raport.append(blad3)
        #zapis raportu z kontroli danych
            raportpd=pd.DataFrame(raport)
            raportpd.to_csv ('raport.txt',sep='\t', index=False, header=False)
        """
        #przetworzenie plików
        #print('przetarzany plik: '+n)  #plik z pikietami nr x y kerg
        data2 = pd.read_csv(os.path.join(app.config['UPLOAD_FOLDER'], filename), sep='\t', header=None)  #utworzenie dataframe z pliku z pikietami
        data2[4]=';'                                     #dodanie nowej kolumny
        data2[5]=data2[0].astype(str)+data2[4].astype(str)+data2[3].round(decimals=2).astype(str)   #nowa kolumna złączenie nr;H
        wynik=(data2[[5,1,2]])
        #print (wynik)
        wynik.to_csv (os.path.join(app.config['UPLOAD_FOLDER'], filename+'_nrhxy.txt'),sep='\t', index=False, header=False, float_format='%.2f') #eksport do txt/csv - z zachowaniem 2 miejsc po przecinku
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename+'_nrhxy.txt', as_attachment=True)



if __name__ == '__main__':
   app.run(debug = True)
