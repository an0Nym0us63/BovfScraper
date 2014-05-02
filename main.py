from pygoogle import pygoogle
import subprocess
import time
import sys
import os.path
import unicodedata
import Tkinter
import shutil
import tkFileDialog
import glob
import pprint
from allocine import allocine
import urllib
import urllib2
from bs4 import BeautifulSoup
api = allocine()
api.configure('100043982026','29d185d98c984a359e6e6f26a0474269')
print 'Ceci est une beta. Certaines bandes annonces pourront etre en anglais voir ne pas correspondre au film'
root = Tkinter.Tk()
directory = tkFileDialog.askdirectory(parent=root,initialdir="/",title='Choisir le repertoire a scanner')
if len(directory) > 0:
    print "Vous avez choisi : %s" % directory
root.destroy()
rootDir = os.path.dirname(os.path.abspath(__file__))
try:
    _DEV_NULL = subprocess.DEVNULL
except AttributeError:
    _DEV_NULL = open(os.devnull, 'wb')
path = directory
    
def libraryscan(path):
    print 'Veuillez patienter pendant la recherche des films sans bandes-annonces dans ' + path
    fichier=[] 
    print 'Calcul en cours....'
    numberfiles=0
    pathori=path
    for path, dires, fics in os.walk(path):
        for f in fics:
            numberfiles+=1
    currentnumber=0
    for root, dirs, files in os.walk(pathori):
        for i in files:
            currentnumber+=1
            trailercount=0
            if ('.mkv' in i or '.avi' in i or '.mp4' in i) and '-trailer' not in i:
                for x in os.listdir(root):
                    if '-trailer' in x:
                        trailercount+=1
                if trailercount==0:
                    fileroot=root
                    filename=i
                    filename=filename[:filename.rfind(")")].replace(' 3DBD','').replace('(','')
                    fichier.append([fileroot,filename,i[:-4]])
                    print str(currentnumber)+' fichiers scannes sur un total de '+str(numberfiles)   
    print str(numberfiles)+' fichiers scannes sur un total de '+str(numberfiles)
    return fichier

def googlesearch(searchstring):
    print 'En attente 5 secondes de lautorisation de google'
    time.sleep(5)
    print 'En train de rechercher sur google : ' +searchstring
    g = pygoogle(str(searchstring))
    try:
        urllist = g.get_urls()
    except:
        try:
            print 'En attente 20 secondes de lautorisation de google'
            time.sleep(20)
            urllist = g.get_urls()
        except:
            try:
                print 'En attente 60 secondes de lautorisation de google'
                time.sleep(60)
                urllist = g.get_urls()
            except:
                urllist=[]
    return urllist

def allocinesearch(moviename):
    series=['2','3','4','5','6','7','8']
    specialchars=[',','.',';','!','?','-',':']
    print 'Tentative de recherche sur Allocine de ' +moviename[:-5]
    try:
        search = api.search(moviename[:-5], "movie")
        for result in search['feed']['movie']:
            countseries=0
            ficheresult=api.movie(result['code'])
            ficheresulttitle=unicodedata.normalize('NFKD', ficheresult['movie']['title']).encode('ascii','ignore')
            ficheresulttitleori=unicodedata.normalize('NFKD', ficheresult['movie']['originalTitle']).encode('ascii','ignore')
            for x in series:
                if x in ficheresulttitle.lower() or x in ficheresulttitleori.lower():
                    if x not in moviename[:-5].lower():
                        countseries+=1
            for chars in specialchars:
                moviename=moviename.replace(chars,'')
                ficheresulttitle=ficheresulttitle.replace(chars,'')
            if moviename[:-5].lower() in ficheresulttitle.lower() and countseries==0:
                goodresult=result
                break
        print "Resultat : Nombre [{0}] Code [{1}] Titre original [{2}]".format(search['feed']['totalResults'],
                                                                    goodresult['code'],
                                                                    goodresult['originalTitle'])
        print 'Recherche de la fiche du film avec le code : ' + str(goodresult['code'])
        movieallo = ficheresult
        for x in movieallo['movie']['link']:
            if x.has_key('name') and 'Bandes annonces' in x['name']:
                pagetrailer=x['href']
            else:
                continue
        soup = BeautifulSoup( urllib2.urlopen(pagetrailer), "html.parser" )
        rows = soup.findAll("a")
        for lien in rows:
            if 'Bande-annonce' in str(lien) and 'VF' in str(lien):
                lienid=lien['href'][:lien['href'].find('&')].replace('/video/player_gen_cmedia=','')
        print "Potentiel code de bande annonce [{0}]".format(lienid)
        print "Recuperation de la liste des bandes annonces et identification de la meilleure qualite"
        trailerallo = api.trailer(lienid)
        long=len(trailerallo['media']['rendition'])
        linkallo=trailerallo['media']['rendition'][long-1]['href']
        longadr=len(linkallo)
        extallo=linkallo[longadr-3:]
                
        return linkallo,extallo
    except:
        return 'None','None'
def clean(urllist):
    cleanlist=[]
    for x in urllist:
        if 'youtube' in x or 'dailymotion' in x:
            cleanlist.append(x)
    return cleanlist

def videodl(cleanlist,trailername,moviename,trailerpath):
    bocount=0
    for bo in cleanlist:
        if bocount==0:
            try:
                print 'En train de telecharger : ' + cleanlist[0] + ' pour ' +moviename
                tempdest=unicodedata.normalize('NFKD', os.path.join(rootDir,trailername)).encode('ascii','ignore')+u'.%(ext)s'
                dest=os.path.join(trailerpath,trailername)
                p=subprocess.Popen([sys.executable, 'youtube_dl/__main__.py', '-o',tempdest,'--newline', '--max-filesize', '105m', bo],cwd=rootDir, shell=True, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
                while p.poll() is None:
                    l = p.stdout.readline() # This blocks until it receives a newline.
                    print l +' ' + moviename + ' trailer'
                # When the subprocess terminates there might be unconsumed output 
                # that still needs to be processed.
                (out, err) = p.communicate()
                print out
                print err
                if err:
                    continue
                else:
                    listetemp=glob.glob(os.path.join(rootDir,'*'))
                    for listfile in listetemp:
                        if unicodedata.normalize('NFKD', trailername).encode('ascii','ignore') in listfile:
                            ext=listfile[-4:]
                            destination=dest+ext
                            shutil.move(listfile, destination)
                            bocount=1
                            print 'Une bande annonce telechargee pour ' + moviename
                            return True
            except:
                continue
        else:
            continue
    return False
    
fichier = libraryscan(path)
if len(fichier)>0:
    print str(len(fichier)) + ' films sans bandes annonces ont ete trouves'
    for moviewithouttrailer in fichier:
        print unicodedata.normalize('NFKD', moviewithouttrailer[1]).encode('ascii','ignore')
else:
    print 'Aucun film sans bande annonce trouve. Appuyer sur ENTREE pour fermer la fenetre'
    raw_input()
    sys.exit()
countgoogle=0
countallo=0
compteur=0
notfound=[]
for movie in fichier:
    print '####################Il reste ' + str(len(fichier)-compteur)+' films######################'
    compteur+=1
    trailerpath=movie[0]
    moviename = unicodedata.normalize('NFKD', movie[1]).encode('ascii','ignore')
    trailername=movie[2]+'-trailer'
    searchstring=moviename + u' bande annonce vf HD'
    linkallo,extallo=allocinesearch(moviename)
    if linkallo <>'None':
        print 'Telechargement de la bande annonce suivante : ' + linkallo + ' en cours...'
        urllib.urlretrieve(linkallo, os.path.join(trailerpath,trailername)+'.'+extallo)
        countallo+=1
        print 'Une bande annonce telechargee pour ' + moviename
    else:
        urllist=googlesearch(searchstring)
        cleanlist=clean(urllist)
        if cleanlist:
            videodl(cleanlist,trailername,moviename,trailerpath)
            countgoogle+=1     
        else:
            print 'Aucune bande annnonce trouvee pour ' + moviename + ' essai dune autre recherche'
            searchstring=moviename[:-5] + u' bande annonce vf HD'
            urllist=googlesearch(searchstring)
            cleanlist=clean(urllist)
            if cleanlist:
                videodl(cleanlist,trailername,moviename,trailerpath)
                countgoogle+=1      
            else:     
                notfound.append(moviename)
for nf in notfound:
    print 'Aucune bande annnonce trouvee pour ' + nf
print str(countallo) + ' bandes annonces telechargees sur Allocine'
print str(countgoogle) + ' bandes annonces telechargees sur google'
print str(countallo+countgoogle)+ ' bandes annonces telechargees au total'
print 'Veuillez appuyee sur ENTREE pour fermer la fenetre'
raw_input()
    
