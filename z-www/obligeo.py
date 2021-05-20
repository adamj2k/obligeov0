# - *- coding: utf- 8 - *-
import os
import pandas as pd
import random
import sys
sys.path.append('/home/adamjawor/.local/lib/python2.7/site-packages/')
import ezdxf
import geopandas as gpd
import shapely.geometry as geometry
from shapely.geometry import Point, Polygon
from flask import Flask, render_template, request, redirect, url_for, send_file, send_from_directory
from werkzeug.utils import secure_filename



UPLOAD_FOLDER = '/home/adamjawor/obligeov0/temp_uploads'
ALLOWED_EXTENSIONS = {'txt', 'dxf'}

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
        zrodlo = open(os.path.join(app.config['UPLOAD_FOLDER'], filename)).readlines() #konwersja pliku zrodlowego
        cel = open(os.path.join(app.config['UPLOAD_FOLDER'], filename+'_Am.txt'),'w')
        for s in zrodlo:
             values = s.split("\t")   #dzieli plik tekstowy wzgledem tab
             #print("Nr:"+values[0] + ", X:"+ values[1] + ", y:"+ values[2] + ", H:"+ values[3]) #wyswietla zawartosc pliku
             h = float(values[3])+float(roznica)       #przeliczenie wysokosci - wartosc roznicy moze byc zmieniona
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
        #raport=['lista plikow z bledami danych']   #utworzenie listy na raport bledow
        #data = pd.read_csv(f, sep='\t', header=None)  #utworzenie dataframe z pliku z pikietami
        """
            try:
                data[1]=data[1].astype(float)   #kontrola czy wsp to liczby zmiennoprzecinkowe float64
            except:                                 #jesli bład wyswietl komunikat i zapisz nazwe blednego pliku
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

#WSAD GEO_INFO
@app.route('/wsadgeoinfo')
def wsad_gi():
    return render_template('wsad_geoinfo.html')

@app.route('/wsad_geoinfo', methods =['GET', 'POST'])
def wsad_geoinfo():
    if request.method == 'POST':
        datapom=request.form['datapom']
        zgloszenie=request.form['zgloszenie']
        f = request.files['file']
        filename = secure_filename(f.filename)
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        data = pd.read_csv(os.path.join(app.config['UPLOAD_FOLDER'], filename), sep='\t', header=None)  #utworzenie dataframe z pliku z pikietami
        data[4]='GSPPRB'
        data[5]='O'
        data[6]=zgloszenie
        data[7]=datapom
        wynik=(data[[4,0,1,2,3,3,5,6,7]])   #tabela x, y ,h, rzg, kod, rodzja pom -pom. na osnowę, data pomiaru, kerg.n

       #dodanie dodatkowych danych do pliku wsadowego
        w_zakonczenie = '#Koniec'
        poczatek0='# Plik wsadowy GEO-INFO 7, wygenerowany przez program Generator wsadów'
        poczatek1='#_SEPARATOR=|'
        poczatek2='#Punkty inne=_code.n|_number|_X|_Y|_H|RZG|MPD.n|KRG.n|DTP'
        #zapis do plików txt
        wynik.to_csv (os.path.join(app.config['UPLOAD_FOLDER'], filename+'_wsad.wsd'),sep='|', index=False, header=False, float_format='%.2f') #eksport do txt/csv - z zachowaniem 2 miejsc po przecinku
        #dopisanie dodatkowych danych do pliku txt
        plik = open(os.path.join(app.config['UPLOAD_FOLDER'], filename+'_wsad.wsd'),"r+")
        linie=plik.readlines()
        plik.seek(0, 0)
        plik.write(poczatek0+'\n')
        plik.write(poczatek1+'\n')
        plik.write(poczatek2+'\n')
        for linia in linie:
            plik.write(linia)
        plik.seek(0, os.SEEK_END)
        plik.write(w_zakonczenie+'\n')
        plik.close()
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename+'_wsad.wsd', as_attachment=True)

#WSAD TURBOMAP
@app.route('/wsadturbomap')
def wsad_tb():
    return render_template('wsad_turbomap.html')
@app.route('/wsad_turbomap', methods =['GET', 'POST'])
def wsad_turbomap():
    if request.method == 'POST':
        datapom=request.form['datapom']
        zgloszenie=request.form['zgloszenie']
        f = request.files['file']
        filename = secure_filename(f.filename)
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        data = pd.read_csv(os.path.join(app.config['UPLOAD_FOLDER'], filename), sep='\t', header=None)  #utworzenie dataframe z pliku z pikietami
        data[4]='pomiarNaOsnowe'
        data[5]=zgloszenie
        data[6]=datapom
        wynik=(data[[0,1,2,3,4,6,5]])   #tabela nr, x, y ,h, zrodlo, , data pomiaru, operat
        wynik.to_csv (os.path.join(app.config['UPLOAD_FOLDER'], filename+'_wsad.txt'),sep='\t', index=False, header=False, float_format='%.2f') #eksport do txt/csv - z zachowaniem 2 miejsc po przecinku
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename+'_wsad.txt', as_attachment=True)

#WSAD EWMAPA
@app.route('/wsadewmapa')
def wsad_ewm():
    return render_template('wsad_ewmapa.html')

@app.route('/wsad_ewmapa', methods =['GET', 'POST'])
def wsad_ewmapa():
    if request.method == 'POST':
        pliki = request.files.getlist('file[]')
        calosc=pd.DataFrame()   #utworzenie pustej tabeli do której będą zapisywane kolejne pliki
        for file in pliki:
            nazwa = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], nazwa))
            #tutaj kod przetwarzania plików
            data = pd.read_csv(os.path.join(app.config['UPLOAD_FOLDER'], nazwa), sep=None, header=None)  #utworzenie dataframe z pliku z pikietami
            data[3]='4#'+nazwa
            data[4]='1.00'
            data[5]='359.60'
            data[6]='7'
            data[7]='"'+data[0].astype(str)+'"'
            wynik=(data[[1,2,4,5,6,7,3]])   #tabela x, y ,1.0, 359.6, 7, nr, rodzaj, operat
            calosc = calosc.append(wynik)                       #itercyjne dodawanie kolejnych plików do tabeli
        calosc.to_csv (os.path.join(app.config['UPLOAD_FOLDER'], 'ewmapa_wsad.txt'),sep='\t', index=False, header=False, float_format='%.2f') #eksport do txt/csv - z zachowaniem 2 miejsc po przecinku
        return send_from_directory(app.config['UPLOAD_FOLDER'], 'ewmapa_wsad.txt', as_attachment=True)


#WSP DO PLIKU DXF
@app.route('/pktdodxf')
def pktdodxf():
    return render_template('pktdodxf.html')

@app.route('/punkty_dxf', methods =['GET', 'POST'])
def punkty_dxf():
    if request.method == 'POST':
        pliki = request.files.getlist('file[]')
        przeglad=ezdxf.new(dxfversion='R2010')
        model=przeglad.modelspace()
        #import przeglądówek 2000 i 65 z obszarami
        przeg2000=gpd.read_file('/home/adamjawor/obligeov0/temp_uploads/przeg.shp')
        przeg65=gpd.read_file('/home/adamjawor/obligeov0/temp_uploads/przeg_65.shp')
        #poligony okrelające obszar opracowania - wprowadzone ręcznie
        oboprac=Polygon([(5572151.7553, 5707978.6366), (5577311.5050, 5710677.2032), (5578864.2224, 5707708.3554), (5573894.7270, 5704062.2555)])
        oboprac65=Polygon([(3663170.6256, 5610718.0956),(3666428.0216, 5609062.2334),(3661369.7888, 5604823.2264),(3658953.2246, 5607333.5134)])
        #kontrola danych
        raport=['Wynik przyporzadkowania czesci obiektu oraz ewentualne bledy']   #utworzenie listy na raport błedów

        for file in pliki:
            nazwa = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], nazwa))
            raport.append(nazwa)
            try:
                #tutaj kod przetwarzania plików
                dane = pd.read_csv(os.path.join(app.config['UPLOAD_FOLDER'], nazwa), sep=' ', header=None)
                color = random.randint(2,220) #losowy kolor dla operatu
                points = [Point(xyh) for xyh in zip(dane[2], dane[1], dane[3])]
                point_collection = geometry.MultiPoint(list(points))
            except Exception as komunikat:
                raport.append(komunikat)
                continue
        #kontrola współrzędnych - czy znajdują się w obszarze opracowania
            spr1=point_collection.within(oboprac)
            spr2=point_collection.within(oboprac65)
            if spr1 is False and spr2 is False:
                raport.append('sprawdź współrzędne jakas jest poza zakresem opracowania w pliku: ')

       #sprawdzenie w jakim obszarze są punkty z pliku ukl2000
            for index, row in przeg2000.iterrows():
                obszar=(row[6])
                zawiera=point_collection.within(obszar)
                przecina=point_collection.crosses(obszar)
            #sprawdzenie zawierania i przecinania punktów przez obszar
                if zawiera is True or przecina is True:
                    wynik=(row[5])
                    raport.append(' czesc='+wynik)
                    break
        #sprawdzenie w jakim obszarze są punkty z pliku ukl65
            for index, row in przeg65.iterrows():
                obszar65=(row[6])
                zawiera65=point_collection.within(obszar65)
                przecina65=point_collection.crosses(obszar65)
            #sprawdzenie zawierania i przecinania punktów przez obszar
                if zawiera65 is True or przecina65 is True:
                    wynik=(row[5])
                    raport.append(' czesc='+wynik)
                    break


            #wczytaj punkty do dxf
            for index in dane.index:
                wspolrzedne= (dane[2][index],dane[1][index])
                tekst = dane[0][index]
                #print (tekst+wspolrzedne)
                model.add_text(tekst, dxfattribs={'layer':nazwa, 'color':color, 'height':5}).set_pos((wspolrzedne), align='LEFT')
        #zapis pliku raportu
            raportpd=pd.DataFrame(raport)
            raportpd.to_csv (os.path.join(app.config['UPLOAD_FOLDER'], 'raport.txt'),sep='\t', index=False, header=False)
        #zapis pliku dxf
            przeglad.saveas(os.path.join(app.config['UPLOAD_FOLDER'],'wczytane_wsp.dxf'))
        #return send_from_directory(app.config['UPLOAD_FOLDER'], 'wczytane_wsp.dxf', as_attachment=True)
        pobieranie =(app.config['UPLOAD_FOLDER'], 'wczytane_wsp.dxf')
        return render_template('wynik_pktdodxf.html',raport=raport, pobieranie=pobieranie)
