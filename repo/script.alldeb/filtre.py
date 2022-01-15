import re
import xbmcgui
import xbmcvfs

lien_pref = xbmcvfs.translatePath("special://userdata/addon_data/script.alldeb/")
if xbmcvfs.exists(lien_pref+"/filtre.txt"):
	with xbmcvfs.File(lien_pref+"/filtre.txt", "r") as fichier:
		dico_fichier = fichier.read()
		dico_fichier = re.sub('>,<','>\n<',dico_fichier, 0, re.MULTILINE)
dialog = xbmcgui.Dialog()
ok = dialog.textviewer('Addon import Alldeb',dico_fichier)