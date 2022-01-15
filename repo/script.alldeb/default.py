#import des librairies
import xbmc
import xbmcaddon
import xbmcgui
import xbmcvfs
import requests
import json
import re
import time

#déclaration des variables
serveur = "https://api.alldebrid.com/v4/user/links?agent="
agent = "kodi"
selfAddon = xbmcaddon.Addon('script.alldeb')
APIkey= ''
APIkey = selfAddon.getSettingString('API')
lien_pref = xbmcvfs.translatePath("special://userdata/addon_data/script.alldeb/")
Dir_base = selfAddon.getSettingString('Dossier')
Dir_Film = Dir_base + 'Films/'
Dir_Serie = Dir_base + 'Series/'
Dir_Inconnu = Dir_base + 'Inconnus/'


#Créer le dictionnaire de filtre dico_base. Si le fichier filtre existe, récuperer les données sinon utiliser des filtres préconsus
dico_base = {}
if xbmcvfs.exists(lien_pref+"/filtre.txt"):
	with xbmcvfs.File(lien_pref+"/filtre.txt", "r") as fichier:
		dico_fichier = fichier.read()
	dico_cle_fichier = dico_fichier.split('>,<')
	for cle_fichier in dico_cle_fichier:
		str_dico_fichier = cle_fichier.split('>:<')
		key = re.sub('^<|>$','',str_dico_fichier[0], 0, re.MULTILINE)
		value = re.sub('^<|>$','',str_dico_fichier[1], 0, re.MULTILINE)
		dico_base[key] = value
else:
	titre_a_remplacer = ["PD","Grey's","Greys anatomy","Grey's anatomy Anatomy","At Midnight","Toaru Kagaku no Accelerator","Kanata no Astra","Survivor AU","BSG","Bordertown (US)","Catch 22","Cosmos A Space Time Odyssey","CSI","DBZ","EPL","Fairy Tail Final Season","Enen no Shouboutai","Forever (US)","GOT","HDM","HOC","HIMYM","Instinct (US)","Law and Order SVU","MASH","MBFAGW","Naruto Shippuuden","NCIS LosAngeles","NCIS NO","OUaT","Outsiders (2016)","Proof (US)","Tangled: The Series","Resurrection (US)","Scream The TV Series","Sex and Drugs and Rock and Roll","SOS","Smithsonian","Star Trek: TOS","Star Trek: DS9","Star Trek: ENT","Star Trek: TNG","Star Trek: VOY","Stargate","Super Girl","TBBT","The Bridge (US)","The Code (AU)","The Inexplicable Universe with Neil deGrasse Tyson","Craig Ferguson","Luksusfaelden","The Nightly Show","TWD","TAAHM","UFC Fight Night","Warrior","WSOP"]
	titre_remplacement = ["Police Department","Grey's anatomy","Grey's anatomy","Grey's anatomy","@midnight","A Certain Scientific Accelerator","Astra Lost in Space","Australian Survivor","Battlestar Galactica (2003)","Bordertown (2016)","Catch-22","Cosmos: A Spacetime Odyssey","CSI: Crime Scene Investigation","Dragon Ball Z","English Premier League","Fairy Tail","Fire Force","Forever (2014)","Game of Thrones","His Dark Materials","House of Cards","How I Met Your Mother","Instinct (2018)","Law & Order: Special Victims Unit","M*A*S*H","My Big Fat American Gypsy Wedding","Naruto Shippuden","NCIS: Los Angeles","NCIS: New Orleans","Once Upon a Time (2011)","Outsiders","Proof (2015)","Rapunzel's Tangled Adventure","Resurrection","Scream","Sex&Drugs&Rock&Roll","Shahs of Sunset","Smithsonian Channel Documentaries","Star Trek","Star Trek: Deep Space Nine","Star Trek: Enterprise","Star Trek: The Next Generation","Star Trek: Voyager","Stargate SG-1","Supergirl","The Big Bang Theory","The Bridge (2013)","The Code (2014)","The Inexplicable Universe","The Late Late Show with Craig Ferguson","The Luxury Trap","The Nightly Show with Larry Wilmore","The Walking Dead","Two and a Half Men","UFC Primetime","Warrior (2019)","World Series of Poker"]
	zip_iterator = zip(titre_a_remplacer, titre_remplacement)
	dico_base = dict(zip_iterator)

#Récuperer les filtres entrés dans le setting de l'addon
dico = selfAddon.getSettingString('dico')
if not dico == '':
	dico_cle = dico.split('>,<')
	for key in dico_cle:	
		str_dico = key.split('>:<')
		key = re.sub('^<|>$','',str_dico[0], 0, re.MULTILINE)
		value = re.sub('^<|>$','',str_dico[1], 0, re.MULTILINE)
		dico_base[key] = value
	selfAddon.setSetting('dico', '')

#Remplissage du fichier filtre avec les nouveaux filtres
test = ''
for key, value in dico_base.items():
	test= test + '<'+key+'>:<'+value+'>,'
with xbmcvfs.File(lien_pref+"/filtre.txt", "w") as fichier:
	fichier.write(re.sub(',$','',test, 0, re.MULTILINE))


#on ne va chercher les liens que si on a un compte premium
if (APIkey != ''):

	#Suppression des repertoires
	if (xbmcvfs.exists(Dir_Film)) :
		xbmcvfs.rmdir(Dir_Film,1)
		
	if (xbmcvfs.exists(Dir_Serie)) :
		xbmcvfs.rmdir(Dir_Serie,1)

	if (xbmcvfs.exists(Dir_Inconnu)) :
		xbmcvfs.rmdir(Dir_Inconnu,1)

	#Création des repertoires sauf inconnus qui sera créé au besoin
	xbmcvfs.mkdirs(Dir_Film)
	xbmcvfs.mkdirs(Dir_Serie)

	#Recuperation des liens all debrid
	loaded_json = json.loads((requests.get(serveur+agent+"&apikey="+APIkey)).text)

	for i in loaded_json['data']['links']:
		#debridage du lien
		response_lien_deb = json.loads((requests.get("https://api.alldebrid.com/v4/link/unlock?agent=testavantprojet&apikey=wfYZOu5JO22C4dYO0Y9p&link="+i['link'])).text)
		
		#cherche la saison et l'episode
		output = re.search('(^.*)((S|Saison|Season)(\s?\d{1,3}))((E|Ep|Episode)(\s?\d{1,3}))', i['filename'], flags=re.IGNORECASE)
		if output is not None:
			#si on est la c'est une série
			type_media = "Serie"
			saison = output.group(4)
			episode = output.group(7)
			titre = output.group(1)
			for key, value in dico_base.items():
				# on nettoie à l'aide des filtres
				titre = titre.replace(key, value)
			titre = re.sub('(-{2,})|(\.{1,}[^ ]??)',' ',titre).strip()
			# on cree les repertoire dans series/nom_serie/saison/nom serie saison episode
			if not(xbmcvfs.exists(Dir_Serie+"/"+titre)):
				xbmcvfs.mkdirs(Dir_Serie+"/"+titre)
				xbmcvfs.mkdirs(Dir_Serie+"/"+titre+"/S"+saison)	
				with xbmcvfs.File(Dir_Serie+titre+"/S"+saison+"/"+titre+"S"+saison+"E"+episode+".strm", "w") as fichier:
					fichier.write(response_lien_deb['data']['link'])
			elif not (xbmcvfs.exists(Dir_Serie+"/"+titre+"/"+saison)):
				xbmcvfs.mkdirs(Dir_Serie+"/"+titre+"/S"+saison)	
				with xbmcvfs.File(Dir_Serie+titre+"/S"+saison+"/"+titre+"S"+saison+"E"+episode+".strm", "w") as fichier:
							fichier.write(response_lien_deb['data']['link'])
			else:
				with xbmcvfs.File(Dir_Serie+titre+"/S"+saison+"/"+titre+"S"+saison+"E"+episode+".strm", "w") as fichier:
					fichier.write(response_lien_deb['data']['link'])
			xbmc.executebuiltin("Notification(Série ,Création de "+titre+" S"+saison+"E"+episode+")")
			while not( xbmcvfs.exists(Dir_Serie+titre+"/S"+saison+"/"+titre+"S"+saison+"E"+episode+".strm")):
				time.sleep(1)
		else:
			#c'etait pas une serie, on cherche une année
			output = re.search('^.*[^\w]\d{4}[^\w]', i['filename'], flags=re.IGNORECASE)
			if output is not None:
				#si y a une année, on considere que c'est un film
				type_media = "Film"
				annee = output.group(0)[-5:-1]
				titre = output.group(0)[0:-5]
				for key, value in dico_titre.items():
					#nettoyage du titre avec les filtres
					titre = titre.replace(key, value)
				titre = re.sub('(-{2,})|(\.{1,}[^ ]??)',' ',titre).strip()
				xbmc.executebuiltin("Notification(Film, Création de "+titre+")")
				with xbmcvfs.File(Dir_Film+titre+" ("+annee+").strm", "w") as fichier:
					fichier.write(response_lien_deb['data']['link'])
				while not( xbmcvfs.exists(Dir_Film+titre+" ("+annee+").strm")):
					time.sleep(1)
			else:
				#Dans ce ca on ne sait pas ce que c'est on le mets dans inconnus
				type_media = "inconnu"
				titre = i['filename']
				if not(xbmcvfs.exists(Dir_Inconnu)):
					xbmcvfs.mkdirs(Dir_Inconnu)
				xbmc.executebuiltin("Notification(Inconnu ,Création de "+titre+")")
				with xbmcvfs.File(Dir_Inconnu+titre+".strm", "w") as fichier:
					fichier.write(response_lien_deb['data']['link'])
				while not( xbmcvfs.exists(Dir_Inconnu+titre+".strm")):
					time.sleep(1)
	xbmc.executebuiltin("Notification(Médiathèque ,Mise à jour de la médiathèque)")
	xbmc.executebuiltin("UpdateLibrary(video)")
	xbmc.executebuiltin("CleanLibrary(video)")
	xbmc.executebuiltin("Notification(Terminé ,Fin de l'import)")				
else : 
	dialog = xbmcgui.Dialog()
	ok = dialog.ok('Addon import Alldeb','Vous n\'avez pas renseigné d\'API dans la configuration de l\'addon.')
