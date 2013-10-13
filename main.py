from pygoogle import pygoogle
import subprocess
import time
import sys
import os.path
import unicodedata
import Tkinter
import tkFileDialog
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
    print 'Veuillez patienter pendant la recherche des films sans bandes-annonces'
    fichier=[] 
    for root, dirs, files in os.walk(path): 
        for i in files: 
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
    return fichier
    
fichier = libraryscan(path)
if len(fichier)>0:
    print str(len(fichier)) + ' films sans bandes annonces ont ete trouves'
    for moviewithouttrailer in fichier:
        print moviewithouttrailer[1]
else:
    print 'Aucun film sans bande annonce trouve. Appuyer sur ENTREE pour fermer la fenetre'
    raw_input()
count=0
for movie in fichier:
    trailerpath=movie[0]
    moviename=movie[1]
    trailername=movie[2]+'-trailer'
    searchstring=moviename +' bande annonce vf HD'
    time.sleep(5)
    print 'En train de rechercher sur google : ' +searchstring
    g = pygoogle(str(searchstring))
    diclist = g.search()
    urllist = g.get_urls()
    cleanlist=[]
    for x in urllist:
        if 'youtube' in x or 'dailymotion' in x:
            cleanlist.append(x)
    if cleanlist:
        print 'En train de telecharger : ' + cleanlist[0] + ' pour ' +moviename
        dest=os.path.join(trailerpath,trailername)
        destination=dest+u'.%(ext)s'
        subprocess.check_call([sys.executable, 'youtube_dl/__main__.py', '-o',destination, cleanlist[0]], cwd=rootDir, shell=False, stdout=_DEV_NULL,stderr=subprocess.STDOUT)
        print 'Une bande annonce telechargee pour ' + moviename
        count+=1
    else:
        print 'Aucune bande annnonce trouvee pour ' + moviename
print str(count) + ' bandes annonces telechargees. Veuillez appuyee sur ENTREE pour fermer la fenetre'
raw.input()
    
