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
import logging
from bs4 import BeautifulSoup
api = allocine()
api.configure('100043982026','29d185d98c984a359e6e6f26a0474269')
logging.basicConfig(filename='trace.log', filemode='w', level=logging.DEBUG)
logging.info('Ceci est une beta. Certaines bandes annonces pourront etre en anglais voir ne pas correspondre au film')
print 'Ceci est une beta. Certaines bandes annonces pourront etre en anglais voir ne pas correspondre au film'
root = Tkinter.Tk()
directory = tkFileDialog.askdirectory(parent=root,initialdir="/",title='Choisir le repertoire a scanner')
if len(directory) > 0:
    print "Vous avez choisi : %s" % directory
    logging.info("Vous avez choisi : %s" % directory)
root.destroy()
rootDir = os.path.dirname(os.path.abspath(__file__))
try:
    _DEV_NULL = subprocess.DEVNULL
except AttributeError:
    _DEV_NULL = open(os.devnull, 'wb')
path = directory

def cleantitle(title):
    specialchars=[',','.',';','!','?','-',':','  ']
    title=unicodedata.normalize('NFKD',title).encode('ascii','ignore')
    for chars in specialchars:
        if chars=='  ':
            title=title.replace(chars,' ')
        else:
            title=title.replace(chars,'')        
    return title.lower()

def cleandic(dict,moviename,hd=True):
    titlenames=urldic.keys()
    listkeys=[]
    for titledict in titlenames:
        cleandict=cleantitle(titledict)
        if cleantitle(moviename[:-5].decode('unicode-escape')) in cleandict and 'vf' in cleandict:
            if hd:
                if 'hd' in cleandict:
                    listkeys.append(titledict)
            else:
                listkeys.append(titledict)
        urllist=[]
        for listkey in listkeys:
            urllist.append(dict[listkey])
    return urllist

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
    print 'En attente 10 secondes de lautorisation de google'
    time.sleep(10)
    print 'En train de rechercher sur google : ' +searchstring
    logging.info('En train de rechercher sur google : ' +searchstring)
    g = pygoogle(str(searchstring))
    try:
        urldic = g.search()
    except:
        try:
            print 'En attente 90 secondes de lautorisation de google'
            time.sleep(90)
            urldic = g.search()
        except:
            try:
                print 'En attente 240 secondes de lautorisation de google'
                time.sleep(240)
                urldic = g.search()
            except:
                urldic={}
    return urldic

def allocinesearch(moviename):
    series=['2','3','4','5','6','7','8']
    specialchars=[' :',',','.',';','!','?','-',':']
    print 'Tentative de recherche sur Allocine de ' +moviename[:-5]
    logging.info('Tentative de recherche sur Allocine de ' +moviename[:-5])
    try:
        search = api.search(moviename[:-5], "movie")
        for result in search['feed']['movie']:
            countseries=0
            ficheresult=api.movie(result['code'])
            ficheresulttitle=cleantitle(ficheresult['movie']['title'])
            ficheresulttitleori=cleantitle(ficheresult['movie']['originalTitle'])
            test=cleantitle(moviename[:-5].decode('unicode-escape'))
            for x in series:
                if x in ficheresulttitle or x in ficheresulttitleori:
                    if x not in moviename[:-5]:
                        countseries+=1                        
            if cleantitle(moviename[:-5].decode('unicode-escape')) in ficheresulttitle and countseries==0:
                goodresult=result
                break
        print "Resultat : Nombre [{0}] Code [{1}] Titre original [{2}]".format(search['feed']['totalResults'],
                                                                    goodresult['code'],
                                                                    goodresult['originalTitle'])
        print 'Recherche de la fiche du film avec le code : ' + str(goodresult['code'])
        logging.info('Recherche de la fiche du film avec le code : ' + str(goodresult['code']))
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
        logging.info("Potentiel code de bande annonce [{0}]".format(lienid))
        print "Recuperation de la liste des bandes annonces et identification de la meilleure qualite"
        trailerallo = api.trailer(lienid)
        long=len(trailerallo['media']['rendition'])
        bestba=trailerallo['media']['rendition'][long-1]
        linkallo=trailerallo['media']['rendition'][long-1]['href']
        heightbaallo=bestba['height']
        longadr=len(linkallo)
        extallo=linkallo[longadr-3:]
                
        return linkallo,extallo,heightbaallo
    except:
        return 'None','None',0

def quacontrol(url):
    quallist=[]
    p=subprocess.Popen([sys.executable, 'youtube_dl/__main__.py', '-F',url],cwd=rootDir, shell=True, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    while p.poll() is None:
        l = p.stdout.readline() # This blocks until it receives a newline.
        quallist.append(l)
    (out, err) = p.communicate()
    for qual in quallist:
        if 'best' in qual and ('720' in qual or '1080' in qual):
            return True
        else:
            continue
    return False
                               
def videodl(cleanlist,trailername,moviename,trailerpath):
    bocount=0
    for bo in cleanlist:
        if bocount==0:
            try:
                print 'En train de telecharger : ' + bo + ' pour ' +moviename
                logging.info('En train de telecharger : ' + bo + ' pour ' +moviename)
                tempdest=unicodedata.normalize('NFKD', os.path.join(rootDir,trailername)).encode('ascii','ignore')+u'.%(ext)s'
                dest=os.path.join(trailerpath,trailername)
                p=subprocess.Popen([sys.executable, 'youtube_dl/__main__.py', '-o',tempdest,'--newline', '--max-filesize', '105m', '--format','best',bo],cwd=rootDir, shell=True, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
                while p.poll() is None:
                    l = p.stdout.readline() # This blocks until it receives a newline.
                    if 'download' in l:
                        print l.replace('\n','')
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
                            logging.info('Une bande annonce telechargee pour ' + moviename)
                            return True
            except:
                continue
        else:
            continue
    return False
    
fichier = libraryscan(path)
if len(fichier)>0:
    print str(len(fichier)) + ' films sans bandes annonces ont ete trouves'
    logging.info(str(len(fichier)) + ' films sans bandes annonces ont ete trouves')
    for moviewithouttrailer in fichier:
        print unicodedata.normalize('NFKD', moviewithouttrailer[1]).encode('ascii','ignore')
else:
    print 'Aucun film sans bande annonce trouve. Appuyer sur ENTREE pour fermer la fenetre'
    logging.info('Aucun film sans bande annonce trouve. Appuyer sur ENTREE pour fermer la fenetre')
    raw_input()
    sys.exit()
countgoogle=0
countallo=0
compteur=0
notfound=[]
for movie in fichier:
    listBA=[]
    listlowq=[]
    print '####################Il reste ' + str(len(fichier)-compteur)+' films######################'
    logging.info('####################Il reste ' + str(len(fichier)-compteur)+' films######################')
    compteur+=1
    trailerpath=movie[0]
    moviename = unicodedata.normalize('NFKD', movie[1]).encode('ascii','ignore')
    trailername=movie[2]+'-trailer'
    searchstring=moviename + u' bande annonce vf HD'
    linkallo,extallo,heightbaallo=allocinesearch(moviename)
    if linkallo<>'None':
        print 'Meilleure resolution trouvee sur Allocine : '+str(heightbaallo)+'p'
        logging.info('Meilleure resolution trouvee sur Allocine : '+str(heightbaallo)+'p')
    if linkallo <>'None' and heightbaallo>=481:
        print 'Telechargement de la bande annonce suivante : ' + linkallo +' en '+str(heightbaallo)+'p en cours...'
        logging.info('Telechargement de la bande annonce suivante : ' + linkallo +' en '+str(heightbaallo)+'p en cours...')
        urllib.urlretrieve(linkallo, os.path.join(trailerpath,trailername)+'.'+extallo)
        countallo+=1
        print 'Une bande annonce telechargee pour ' + moviename +' sur Allocine'
        logging.info('Une bande annonce telechargee pour ' + moviename +' sur Allocine')
    else:
        if linkallo <>'None':
            listBA.append({'link':linkallo,'ext':extallo,'height':heightbaallo,'site':'allocine'})
            print 'Tentative de recherche dune meilleure qualite sur google'
            logging.info('Tentative de recherche dune meilleure qualite sur google')
        else:
            print 'Rien trouve sur Allocine Tentative de recherche sur google'
            logging.info('Rien trouve sur Allocine Tentative de recherche sur google')
        urldic=googlesearch(searchstring+' site:http://www.youtube.com')
        cleanlistctrl=cleandic(urldic,moviename)
        cleanlist=[]
        for tocontrolqual in cleanlistctrl:
            print 'Controle de la qualite reelle de ' +tocontrolqual+ ' en cours...'
            logging.info('Controle de la qualite reelle de ' +tocontrolqual+ ' en cours...')
            if quacontrol(tocontrolqual):
                print 'La qualite de ' +tocontrolqual+' semble HD je rajoute a la liste'
                logging.info('La qualite de ' +tocontrolqual+' semble HD je rajoute a la liste')
                cleanlist.append(tocontrolqual)
            else:
                print 'Pfffff encore un mytho la qualite de ' +tocontrolqual+' nest pas HD jignore'
                logging.info('Pfffff encore un mytho la qualite de ' +tocontrolqual+' nest pas HD jignore')
        low=cleandic(urldic,moviename,False)
        if low:
            listlowq.append(low)
        if cleanlist:
            print 'Si jen crois google jai trouve mieux que la bande annonce allocine . Lets go'
            logging.info('Si jen crois google jai trouve mieux que la bande annonce allocine . Lets go')
            videodl(cleanlist,trailername,moviename,trailerpath)
            countgoogle+=1     
        else:
            print 'Aucune bande annnonce trouvee pour ' + moviename + ' sur youtube en HD essai sur dailymotion'
            logging.info('Aucune bande annnonce trouvee pour ' + moviename + ' sur youtube en HD essai sur dailymotion')
            urldic=googlesearch(searchstring+' site:http://www.dailymotion.com')
            cleanlistctrl=cleandic(urldic,moviename)
            cleanlist=[]
            for tocontrolqual in cleanlistctrl:
                print 'Controle de la qualite reelle de ' +tocontrolqual+ ' en cours...'
                logging.info('Controle de la qualite reelle de ' +tocontrolqual+ ' en cours...')
                if quacontrol(tocontrolqual):
                    print 'La qualite de ' +tocontrolqual+' semble HD je rajoute a la liste'
                    logging.info('La qualite de ' +tocontrolqual+' semble HD je rajoute a la liste')
                    cleanlist.append(tocontrolqual)
                else:
                    print 'Pfffff encore un mytho la qualite de ' +tocontrolqual+' nest pas HD jignore'
                    logging.info('Pfffff encore un mytho la qualite de ' +tocontrolqual+' nest pas HD jignore')
            if low:
                listlowq.append(low)
            if cleanlist:
                print 'Si jen crois google jai trouve mieux que la bande annonce allocine . Lets go'
                logging.info('Si jen crois google jai trouve mieux que la bande annonce allocine . Lets go')
                videodl(cleanlist,trailername,moviename,trailerpath)
                countgoogle+=1     
            else:
                print 'Aucune bande annnonce trouvee pour ' + moviename + ' sur dailymotion en HD essai dune autre recherche'
                logging.info('Aucune bande annnonce trouvee pour ' + moviename + ' sur dailymotion en HD essai dune autre recherche')
                searchstring=moviename[:-5] + u' bande annonce vf HD'
                urldic=googlesearch(searchstring+' site:http://www.youtube.com')
                cleanlistctrl=cleandic(urldic,moviename)
                cleanlist=[]
                for tocontrolqual in cleanlistctrl:
                    print 'Controle de la qualite reelle de ' +tocontrolqual+ ' en cours...'
                    logging.info('Controle de la qualite reelle de ' +tocontrolqual+ ' en cours...')
                    if quacontrol(tocontrolqual):
                        print 'La qualite de ' +tocontrolqual+' semble HD je rajoute a la liste'
                        logging.info('La qualite de ' +tocontrolqual+' semble HD je rajoute a la liste')
                        cleanlist.append(tocontrolqual)
                    else:
                        print 'Pfffff encore un mytho la qualite de ' +tocontrolqual+' nest pas HD jignore'
                        logging.info('Pfffff encore un mytho la qualite de ' +tocontrolqual+' nest pas HD jignore')
                if low:            
                    listlowq.append(low)
                if cleanlist:
                    print 'Si jen crois google jai trouve mieux que la bande annonce allocine . Lets go'
                    logging.info('Si jen crois google jai trouve mieux que la bande annonce allocine . Lets go')
                    videodl(cleanlist,trailername,moviename,trailerpath)
                    countgoogle+=1     
                else:
                    print 'Aucune bande annnonce trouvee pour ' + moviename[:-5] + ' sur youtube en HD essai dune autre recherche sur dailymotion'
                    logging.info('Aucune bande annnonce trouvee pour ' + moviename[:-5] + ' sur youtube en HD essai dune autre recherche sur dailymotion')
                    searchstring=moviename[:-5] + u' bande annonce vf HD'
                    urldic=googlesearch(searchstring+' site:http://www.dailymotion.com')
                    cleanlistctrl=cleandic(urldic,moviename)
                    cleanlist=[]
                    for tocontrolqual in cleanlistctrl:
                        print 'Controle de la qualite reelle de ' +tocontrolqual+ ' en cours...'
                        logging.info('Controle de la qualite reelle de ' +tocontrolqual+ ' en cours...')
                        if quacontrol(tocontrolqual):
                            print 'La qualite de ' +tocontrolqual+' semble HD je rajoute a la liste'
                            logging.info('La qualite de ' +tocontrolqual+' semble HD je rajoute a la liste')
                            cleanlist.append(tocontrolqual)
                        else:
                            print 'Pfffff encore un mytho la qualite de ' +tocontrolqual+' nest pas HD jignore'
                            logging.info('Pfffff encore un mytho la qualite de ' +tocontrolqual+' nest pas HD jignore')
                    if low:
                        listlowq.append(low)
                    if cleanlist:
                        print 'Si jen crois google jai trouve mieux que la bande annonce allocine . Lets go'
                        logging.info('Si jen crois google jai trouve mieux que la bande annonce allocine . Lets go')
                        videodl(cleanlist,trailername,moviename,trailerpath)
                        countgoogle+=1     
                    else:
                        if listBA:
                            print 'Rien trouve de mieux sur google pour : '+moviename+' je telecharge donc la bande annonce non HD Allocine'
                            logging.info('Rien trouve de mieux sur google pour : '+moviename+' je telecharge donc la bande annonce non HD Allocine')
                            linkallo=listBA[0]['link']
                            heightbaallo=listBA[0]['height']
                            print 'Telechargement de la bande annonce suivante : ' + linkallo +' en '+str(heightbaallo)+'p en cours...'
                            logging.info('Telechargement de la bande annonce suivante : ' + linkallo +' en '+str(heightbaallo)+'p en cours...')
                            urllib.urlretrieve(linkallo, os.path.join(trailerpath,trailername)+'.'+extallo)
                            countallo+=1
                            print 'Une bande annonce telechargee pour ' + moviename +' sur Allocine'
                            logging.info('Une bande annonce telechargee pour ' + moviename +' sur Allocine')
                        else:
                            if listlowq:
                                print 'Rien trouve sur Allocine pour : ' +moviename+' je recupere donc une bande annonce non HD trouve sur google'
                                logging.info('Rien trouve sur Allocine pour : ' +moviename+' je recupere donc une bande annonce non HD trouve sur google')
                                videodl(listlowq,trailername,moviename,trailerpath)
                                countgoogle+=1
                            else:
                                print 'Snifff encore un film pourri pas de bande annonce trouve pour ' + moviename
                                logging.info('Snifff encore un film pourri pas de bande annonce trouve pour ' + moviename)
                                notfound.append(moviename)
for nf in notfound:
    print 'Aucune bande annnonce trouvee pour ' + nf
    logging.info('Aucune bande annnonce trouvee pour ' + nf)
print str(countallo) + ' bandes annonces telechargees sur Allocine'
logging.info(str(countallo) + ' bandes annonces telechargees sur Allocine')
print str(countgoogle) + ' bandes annonces telechargees sur Google'
logging.info(str(countgoogle) + ' bandes annonces telechargees sur Google')
print str(countallo+countgoogle)+ ' bandes annonces telechargees au total'
logging.info(str(countallo+countgoogle)+ ' bandes annonces telechargees au total')
print 'Veuillez appuyer sur ENTREE pour fermer la fenetre'
raw_input()
    
