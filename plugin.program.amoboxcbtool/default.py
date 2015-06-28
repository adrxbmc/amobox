import xbmc, xbmcaddon, xbmcgui, xbmcplugin,os,sys
import shutil
import urllib2,urllib
import re
import extract
import time
import CheckPath
import zipfile
import ntpath
import plugin.program.amoboxwizard

ARTPATH      =  '' + os.sep
FANART       =  ''
ADDON        =  xbmcaddon.Addon(id='plugin.program.amoboxcbtool')
AddonID      =  'plugin.program.amoboxcbtool'
AddonTitle   =  "[COLOR=blue][B]AMO[/B][/COLOR][COLOR=green]box[/COLOR] Custom Builds Tool"
zip          =  ADDON.getSetting('zip')
localcopy    =  ADDON.getSetting('localcopy')
keyid        =  ADDON.getSetting('keyid')
privatebuilds=  ADDON.getSetting('private')
privateuser  =  ADDON.getSetting('privateuser')
reseller     =  ADDON.getSetting('reseller')
resellername =  ADDON.getSetting('resellername')
resellerid   =  ADDON.getSetting('resellerid')
mastercopy   =  ADDON.getSetting('mastercopy')
dialog       =  xbmcgui.Dialog()
dp           =  xbmcgui.DialogProgress()
HOME         =  xbmc.translatePath('special://home/')
USERDATA     =  xbmc.translatePath(os.path.join('special://home/userdata',''))
MEDIA        =  xbmc.translatePath(os.path.join('special://home/media',''))
AUTOEXEC     =  xbmc.translatePath(os.path.join(USERDATA,'autoexec.py'))
AUTOEXECBAK  =  xbmc.translatePath(os.path.join(USERDATA,'autoexec_bak.py'))
ADDON_DATA   =  xbmc.translatePath(os.path.join(USERDATA,'addon_data'))
PLAYLISTS    =  xbmc.translatePath(os.path.join(USERDATA,'playlists'))
DATABASE     =  xbmc.translatePath(os.path.join(USERDATA,'Database'))
ADDONS       =  xbmc.translatePath(os.path.join('special://home','addons',''))
CBADDONPATH  =  xbmc.translatePath(os.path.join(ADDONS,AddonID,'default.py'))
GUISETTINGS  =  os.path.join(USERDATA,'guisettings.xml')
GUI          =  xbmc.translatePath(os.path.join(USERDATA,'guisettings.xml'))
GUIFIX       =  xbmc.translatePath(os.path.join(USERDATA,'guifix.xml'))
INSTALL      =  xbmc.translatePath(os.path.join(USERDATA,'install.xml'))
FAVS         =  xbmc.translatePath(os.path.join(USERDATA,'favourites.xml'))
SOURCE       =  xbmc.translatePath(os.path.join(USERDATA,'sources.xml'))
ADVANCED     =  xbmc.translatePath(os.path.join(USERDATA,'advancedsettings.xml'))
PROFILES     =  xbmc.translatePath(os.path.join(USERDATA,'profiles.xml'))
RSS          =  xbmc.translatePath(os.path.join(USERDATA,'RssFeeds.xml'))
KEYMAPS      =  xbmc.translatePath(os.path.join(USERDATA,'keymaps','keyboard.xml'))
USB          =  xbmc.translatePath(os.path.join(zip))
CBPATH       =  xbmc.translatePath(os.path.join(USB,'AMObox Custom Builds',''))
cookiepath   =  xbmc.translatePath(os.path.join(ADDON_DATA,AddonID,'cookiejar'))
startuppath  =  xbmc.translatePath(os.path.join(ADDON_DATA,AddonID,'startup.xml'))
tempfile     =  xbmc.translatePath(os.path.join(ADDON_DATA,AddonID,'temp.xml'))
idfile       =  xbmc.translatePath(os.path.join(ADDON_DATA,AddonID,'id.xml'))
idfiletemp   =  xbmc.translatePath(os.path.join(ADDON_DATA,AddonID,'idtemp.xml'))
notifyart    =  xbmc.translatePath(os.path.join(ADDONS,AddonID,'resources/'))
skin         =  xbmc.getSkinDir()
EXCLUDES     =  ['plugin.program.amoboxcbtool','plugin.video.adrxbmccustombuildswizard']
username     =  ADDON.getSetting('username')
password     =  ADDON.getSetting('password')
login        =  ADDON.getSetting('login')
userdatafolder = xbmc.translatePath(os.path.join(ADDON_DATA,AddonID))
GUINEW       =  xbmc.translatePath(os.path.join(userdatafolder,'guinew.xml'))
guitemp      =  xbmc.translatePath(os.path.join(userdatafolder,'guitemp',''))
tempdbpath   =  xbmc.translatePath(os.path.join(USB,'Database'))
urlbase      =  'None'
#-----------------------------------------------------------------------------------------------------------------    
#Simple shortcut to create a notification
def Notify(title,message,times,icon):
    icon = notifyart+icon
    xbmc.executebuiltin("XBMC.Notification("+title+","+message+","+times+","+icon+")")
#-----------------------------------------------------------------------------------------------------------------    
#Popup class - thanks to whoever codes the help popup in TVAddons Maintenance for this section. Unfortunately there doesn't appear to be any author details in that code so unable to credit by name.
class SPLASH(xbmcgui.WindowXMLDialog):
    def __init__(self,*args,**kwargs): self.shut=kwargs['close_time']; xbmc.executebuiltin("Skin.Reset(AnimeWindowXMLDialogClose)"); xbmc.executebuiltin("Skin.SetBool(AnimeWindowXMLDialogClose)")
    def onFocus(self,controlID): pass
    def onClick(self,controlID): 
        if controlID==12: xbmc.Player().stop(); self._close_dialog()
    def onAction(self,action):
        if action in [5,6,7,9,10,92,117] or action.getButtonCode() in [275,257,261]: xbmc.Player().stop(); self._close_dialog()
    def _close_dialog(self):
        xbmc.executebuiltin("Skin.Reset(AnimeWindowXMLDialogClose)"); time.sleep( .4 ); self.close()
#-----------------------------------------------------------------------------------------------------------------    
#Set popup xml based on platform
def pop():
    popup=SPLASH('totalxbmc.xml',ADDON.getAddonInfo('path'),'DefaultSkin',close_time=34)
    popup.doModal()
    del popup
#-----------------------------------------------------------------------------------------------------------------    
#Initial online check for new video
def VideoCheck():
    import yt
    unlocked = 'no'
    if not os.path.exists(userdatafolder):
        os.makedirs(userdatafolder)
    if not os.path.exists(startuppath):
        localfile = open(startuppath, mode='w+')
        localfile.write('date="01011001"\nversion="0.0"')
        localfile.close()
    if not os.path.exists(idfile):
        localfile = open(idfile, mode='w+')
        localfile.write('id="None"\nname="None"')
        localfile.close()
    BaseURL='http://pastebin.com/raw.php?i=KUg08p8m'
    link = OPEN_URL(BaseURL).replace('\n','').replace('\r','')
    datecheckmatch = re.compile('date="(.+?)"').findall(link)
    videomatch = re.compile('video="https://www.youtube.com/watch\?v=(.+?)"').findall(link)
    datecheck  = datecheckmatch[0] if (len(datecheckmatch) > 0) else ''
    videocheck  = videomatch[0] if (len(videomatch) > 0) else ''

    localfile = open(startuppath, mode='r')
    content = file.read(localfile)
    file.close(localfile)
    localdatecheckmatch = re.compile('date="(.+?)"').findall(content)
    localdatecheck  = localdatecheckmatch[0] if (len(localdatecheckmatch) > 0) else ''
    localversionmatch = re.compile('version="(.+?)"').findall(content)
    localversioncheck  = localversionmatch[0] if (len(localversionmatch) > 0) else ''
    localfile2 = open(idfile, mode='r')
    content2 = file.read(localfile2)
    file.close(localfile2)
    localidmatch = re.compile('id="(.+?)"').findall(content2)
    localidcheck  = localidmatch[0] if (len(localidmatch) > 0) else 'None'
    localbuildmatch = re.compile('name="(.+?)"').findall(content2)
    localbuildcheck  = localbuildmatch[0] if (len(localbuildmatch) > 0) else ''
    if  int(localdatecheck) < int(datecheck):
        replacefile = content.replace(localdatecheck,datecheck)
        writefile = open(startuppath, mode='w')
        writefile.write(str(replacefile))
        writefile.close()
        yt.PlayVideo(videocheck, forcePlayer=True)
        xbmc.sleep(500)
        while xbmc.Player().isPlaying():
            xbmc.sleep(500)
    
    else:
        pop()
    CATEGORIES(localbuildcheck,localversioncheck,localidcheck,unlocked)
#-----------------------------------------------------------------------------------------------------------------    
#Function to create a text box
def TextBoxes(heading,announce):
  class TextBox():
    WINDOW=10147
    CONTROL_LABEL=1
    CONTROL_TEXTBOX=5
    def __init__(self,*args,**kwargs):
      xbmc.executebuiltin("ActivateWindow(%d)" % (self.WINDOW, )) # activate the text viewer window
      self.win=xbmcgui.Window(self.WINDOW) # get window
      xbmc.sleep(500) # give window time to initialize
      self.setControls()
    def setControls(self):
      self.win.getControl(self.CONTROL_LABEL).setLabel(heading) # set heading
      try: f=open(announce); text=f.read()
      except: text=announce
      self.win.getControl(self.CONTROL_TEXTBOX).setText(str(text))
      return
  TextBox()
#---------------------------------------------------------------------------------------------------
#Create a community (universal) backup - this renames paths to special:// and removes unwanted folders
def COMMUNITY_BACKUP():
    guisuccess=1
    CHECK_DOWNLOAD_PATH()
    fullbackuppath = xbmc.translatePath(os.path.join(USB,'AMObox Custom Builds','My Builds',''))
    myfullbackup = xbmc.translatePath(os.path.join(USB,'AMObox Custom Builds','My Builds','my_full_backup.zip'))
    myfullbackupGUI = xbmc.translatePath(os.path.join(USB,'AMObox Custom Builds','My Builds','my_full_backup_GUI_Settings.zip'))
    if not os.path.exists(fullbackuppath):
        os.makedirs(fullbackuppath)
    vq = _get_keyboard( heading="Enter a name for this backup" )
    if ( not vq ): return False, 0
    title = urllib.quote_plus(vq)
    backup_zip = xbmc.translatePath(os.path.join(fullbackuppath,title+'.zip'))
    exclude_dirs_full =  ['plugin.program.amoboxcbtool']
    exclude_files_full = ["xbmc.log","xbmc.old.log","kodi.log","kodi.old.log",'.DS_Store','.setup_complete','XBMCHelper.conf']
    exclude_dirs =  ['plugin.program.amoboxcbtool', 'cache', 'system', 'Thumbnails', "peripheral_data",'library','keymaps']
    exclude_files = ["xbmc.log","xbmc.old.log","kodi.log","kodi.old.log","Textures13.db",'.DS_Store','.setup_complete','XBMCHelper.conf', 'advancedsettings.xml']
    message_header = "Creating full backup of existing build"
    message_header2 = "Creating AMObox Custom Build"
    message1 = "Archiving..."
    message2 = ""
    message3 = "Please Wait"
    if mastercopy=='true':
        ARCHIVE_CB(HOME, myfullbackup, message_header, message1, message2, message3, exclude_dirs_full, exclude_files_full)
    choice = xbmcgui.Dialog().yesno("Do you want to include your addon_data folder?", 'This contains ALL addon settings including passwords.', 'If you\'re intending on sharing this with others we strongly', 'recommend against this unless all data has been manually removed.', yeslabel='Yes',nolabel='No')
    if choice == 0:
        DeletePackages()
    elif choice == 1:
        pass
    FIX_SPECIAL(HOME)
    ARCHIVE_CB(HOME, backup_zip, message_header2, message1, message2, message3, exclude_dirs, exclude_files)  
    time.sleep(1)
    GUIname = xbmc.translatePath(os.path.join(fullbackuppath, title+'_guisettings.zip'))
    zf = zipfile.ZipFile(GUIname, mode='w')
    try:
        zf.write(GUI, 'guisettings.xml', zipfile.ZIP_DEFLATED) #Copy guisettings.xml
    except: guisuccess=0
    try:
        zf.write(xbmc.translatePath(os.path.join(HOME,'userdata','profiles.xml')), 'profiles.xml', zipfile.ZIP_DEFLATED) #Copy profiles.xml
    except: pass
    zf.close()
    if mastercopy=='true':
        zfgui = zipfile.ZipFile(myfullbackupGUI, mode='w')
        try:
            zfgui.write(GUI, 'guisettings.xml', zipfile.ZIP_DEFLATED) #Copy guisettings.xml
        except: guisuccess=0

        try:
            zfgui.write(xbmc.translatePath(os.path.join(HOME,'userdata','profiles.xml')), 'profiles.xml', zipfile.ZIP_DEFLATED) #Copy profiles.xml
        except: pass
        zfgui.close()
    if guisuccess == 0:
        dialog.ok("[COLOR red][B]FAILED![/B][/COLOR]", 'The guisettings.xml file could not be found on your', 'system, please reboot and try again.', '')
    else:
        dialog.ok("[COLOR green][B]SUCCESS![/B][/COLOR]", 'You Are Now Backed Up.')
        dialog.ok("Build Locations", 'Full Backup (only used to restore on this device): [COLOR=yellow]'+myfullbackup, '[/COLOR]Universal Backup (can be used on any device): [COLOR=yellow]'+backup_zip+'[/COLOR]')
#---------------------------------------------------------------------------------------------------
#Function to archive a single file
def ARCHIVE_SINGLE(source,destination,filestructure):
    zf = zipfile.ZipFile(destination, mode='w')
    zf.write(source, filestructure, zipfile.ZIP_DEFLATED) #Copy guisettings.xml
    zf.close()
#---------------------------------------------------------------------------------------------------
#Convert physical paths to special paths
def FIX_SPECIAL(url):
    dp.create("[COLOR=blue][B]AMO[/B][/COLOR][COLOR=green][B]box[/B][/COLOR] Custom Builds","Renaming paths...",'', 'Please Wait')
    for root, dirs, files in os.walk(url):  #Search all xml files and replace physical with special
        for file in files:
            if file.endswith(".xml"):
                 dp.update(0,"Fixing",file, 'Please Wait')
                 a=open((os.path.join(root, file))).read()
                 b=a.replace(USERDATA, 'special://profile/').replace(ADDONS,'special://home/addons/')
                 f = open((os.path.join(root, file)), mode='w')
                 f.write(str(b))
                 f.close()
#---------------------------------------------------------------------------------------------------
#Zip up tree
def ARCHIVE_FILE(sourcefile, destfile):
    zipobj = zipfile.ZipFile(destfile , 'w', zipfile.ZIP_DEFLATED)
    rootlen = len(sourcefile)
    for_progress = []
    ITEM =[]
    dp.create("[COLOR=blue][B]AMO[/B][/COLOR][COLOR=green][B]box[/B][/COLOR] Custom Builds","Archiving...",'', 'Please Wait')
    for base, dirs, files in os.walk(sourcefile):
        for file in files:
            ITEM.append(file)
    N_ITEM =len(ITEM)
    for base, dirs, files in os.walk(sourcefile):
        for file in files:
            for_progress.append(file) 
            progress = len(for_progress) / float(N_ITEM) * 100  
            dp.update(int(progress),"Backing Up",'[COLOR yellow]%s[/COLOR]'%file, 'Please Wait')
            fn = os.path.join(base, file)
            if not 'temp' in dirs:
                if not 'plugin.program.amoboxcbtool' in dirs:
                   import time
                   FORCE= '01/01/1980'
                   FILE_DATE=time.strftime('%d/%m/%Y', time.gmtime(os.path.getmtime(fn)))
                   if FILE_DATE > FORCE:
                       zipobj.write(fn, fn[rootlen:])  
    zipobj.close()
    dp.close()
#---------------------------------------------------------------------------------------------------
#Zip up tree
# "[COLOR=blue][B]AMO[/B][/COLOR][COLOR=green][B]box[/B][/COLOR] Custom Builds","Archiving...",'', 'Please Wait'
def ARCHIVE_CB(sourcefile, destfile, message_header, message1, message2, message3, exclude_dirs, exclude_files):
    zipobj = zipfile.ZipFile(destfile , 'w', zipfile.ZIP_DEFLATED)
    rootlen = len(sourcefile)
    for_progress = []
    ITEM =[]
    dp.create(message_header, message1, message2, message3)
    for base, dirs, files in os.walk(sourcefile):
        for file in files:
            ITEM.append(file)
    N_ITEM =len(ITEM)
    for base, dirs, files in os.walk(sourcefile):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        files[:] = [f for f in files if f not in exclude_files]
        for file in files:
            for_progress.append(file) 
            progress = len(for_progress) / float(N_ITEM) * 100  
            dp.update(int(progress),"Backing Up",'[COLOR yellow]%s[/COLOR]'%file, 'Please Wait')
            fn = os.path.join(base, file)
            if not 'temp' in dirs:
                if not 'plugin.program.amoboxcbtool' in dirs:
                   import time
                   FORCE= '01/01/1980'
                   FILE_DATE=time.strftime('%d/%m/%Y', time.gmtime(os.path.getmtime(fn)))
                   if FILE_DATE > FORCE:
                       zipobj.write(fn, fn[rootlen:])  
    zipobj.close()
    dp.close()
#---------------------------------------------------------------------------------------------------
#Read a zip file and extract the relevant data
def READ_ZIP(url):

    import zipfile
    
    z = zipfile.ZipFile(url, "r")
    for filename in z.namelist():
        if 'guisettings.xml' in filename:
            a = z.read(filename)
            r='<setting type="(.+?)" name="%s.(.+?)">(.+?)</setting>'% skin
            
            match=re.compile(r).findall(a)
            for type,string,setting in match:
                setting=setting.replace('&quot;','') .replace('&amp;','&') 
                xbmc.executebuiltin("Skin.Set%s(%s,%s)"%(type.title(),string,setting))  
                
        if 'favourites.xml' in filename:
            a = z.read(filename)
            f = open(FAVS, mode='w')
            f.write(a)
            f.close()  
                           
        if 'sources.xml' in filename:
            a = z.read(filename)
            f = open(SOURCE, mode='w')
            f.write(a)
            f.close()    
                         
        if 'advancedsettings.xml' in filename:
            a = z.read(filename)
            f = open(ADVANCED, mode='w')
            f.write(a)
            f.close()                 

        if 'RssFeeds.xml' in filename:
            a = z.read(filename)
            f = open(RSS, mode='w')
            f.write(a)
            f.close()                 
            
        if 'keyboard.xml' in filename:
            a = z.read(filename)
            f = open(KEYMAPS, mode='w')
            f.write(a)
            f.close()                              
#---------------------------------------------------------------------------------------------------
def FACTORY(localbuildcheck,localversioncheck,id,unlocked):
    pass
    # if localbuildcheck == factoryname:
        # updatecheck = Check_For_Factory_Update(localbuildcheck,localversioncheck,id)
            # if updatecheck == True:
                    # addDir('[COLOR=dodgerblue]'+localbuildcheck+':[/COLOR] [COLOR=lime]NEW VERSION AVAILABLE[/COLOR]',id,'showinfo','','','','')
                # else:
                    # addDir('[COLOR=lime]Current Build Installed: [/COLOR][COLOR=dodgerblue]'+localbuildcheck+'[/COLOR]',id,'showinfo','','','','')


#---------------------------------------------------------------------------------------------------
#Function to read the contents of a URL
def OPEN_URL(url):
    req = urllib2.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
    response = urllib2.urlopen(req)
    link=response.read()
    response.close()
    return link
#---------------------------------------------------------------------------------------------------
#Function to restore a community build
def RESTORE_COMMUNITY(name,url,video,description,skins,guisettingslink):
    import time
    choice4=1
    CHECK_DOWNLOAD_PATH()
    if os.path.exists(GUINEW):
        if os.path.exists(GUI):
            os.remove(GUINEW)
        else:
            os.rename(GUINEW,GUI)
    if os.path.exists(GUIFIX):
        os.remove(GUIFIX)
    if not os.path.exists(tempfile): #Function for debugging, creates a file that was created in previous call and subsequently deleted when run
        localfile = open(tempfile, mode='w+')
    if os.path.exists(guitemp):
        os.removedirs(guitemp)
    try: os.rename(GUI,GUINEW) #Rename guisettings.xml to guinew.xml so we can edit without XBMC interfering.
    except:
        dialog.ok("NO GUISETTINGS!",'No guisettings.xml file has been found.', 'Please exit XBMC and try again','')
        return
    choice = xbmcgui.Dialog().yesno(name, 'We highly recommend backing up your existing build before', 'installing any AMObox Custom Builds.', 'Would you like to perform a backup first?', nolabel='Backup',yeslabel='Install')
    if choice == 0:
        mybackuppath = xbmc.translatePath(os.path.join(USB,'AMObox Custom Builds','My Builds'))
        if not os.path.exists(mybackuppath):
            os.makedirs(mybackuppath)
        vq = _get_keyboard( heading="Enter a name for this backup" )
        if ( not vq ): return False, 0
        title = urllib.quote_plus(vq)
        backup_zip = xbmc.translatePath(os.path.join(mybackuppath,title+'.zip'))
        exclude_dirs_full =  ['plugin.program.amoboxcbtool']
        exclude_files_full = ["xbmc.log","xbmc.old.log","kodi.log","kodi.old.log",'.DS_Store','.setup_complete','XBMCHelper.conf']
        message_header = "Creating full backup of existing build"
        message1 = "Archiving..."
        message2 = ""
        message3 = "Please Wait"
        ARCHIVE_CB(HOME, backup_zip, message_header, message1, message2, message3, exclude_dirs_full, exclude_files_full)
    choice3 = xbmcgui.Dialog().yesno(name, 'Would you like to keep your existing database', 'files or overwrite? Overwriting will wipe any', 'existing library you may have scanned in.', nolabel='Overwrite',yeslabel='Keep Existing')
    if choice3 == 0: pass
    elif choice3 == 1:
        if os.path.exists(tempdbpath):
            shutil.rmtree(tempdbpath)
        try:
            shutil.copytree(DATABASE, tempdbpath, symlinks=False, ignore=shutil.ignore_patterns("Textures13.db","Addons16.db","Addons15.db","saltscache.db-wal","saltscache.db-shm","saltscache.db","onechannelcache.db")) #Create temp folder for databases, give user option to overwrite existing library
        except:
            choice4 = xbmcgui.Dialog().yesno(name, 'There was an error trying to backup some databases.', 'Continuing may wipe your existing library. Do you', 'wish to continue?', nolabel='No, cancel',yeslabel='Yes, overwrite')
            if choice4 == 1: pass
            if choice4 == 0: return
        backup_zip = xbmc.translatePath(os.path.join(USB,'Database.zip'))
        ARCHIVE_FILE(tempdbpath,backup_zip)
    if choice4 == 0: return
    time.sleep(1)
    dp.create("AMObox Custom Builds","Downloading "+description +" build.",'', 'Please Wait')
    lib=os.path.join(CBPATH, description+'.zip')
    if not os.path.exists(CBPATH):
        os.makedirs(CBPATH)
    downloader.download(url, lib, dp)
    readfile = open(CBADDONPATH, mode='r')
    default_contents = readfile.read()
    readfile.close()
    READ_ZIP(lib)
    dp.create("[COLOR=blue][B]AMO[/B][/COLOR][COLOR=green][B]box[/B][/COLOR] Custom Builds","Checking ",'', 'Please Wait')
    dp.update(0,"", "Extracting Zip Please Wait")
    extract.all(lib,HOME,dp)
    time.sleep(1)

    if localcopy == 'false':
        os.remove(lib)
    cbdefaultpy = open(CBADDONPATH, mode='w+')
    cbdefaultpy.write(default_contents)
    cbdefaultpy.close()
    try:
        os.rename(GUI,GUIFIX)
    except:
        print"NO GUISETTINGS DOWNLOADED"
    time.sleep(1)
    localfile = open(GUINEW, mode='r') #Read the original skinsettings tags and store in memory ready to replace in guinew.xml
    content = file.read(localfile)
    file.close(localfile)
    skinsettingsorig = re.compile('<skinsettings>[\s\S]*?<\/skinsettings>').findall(content)
    skinorig  = skinsettingsorig[0] if (len(skinsettingsorig) > 0) else ''
    skindefault = re.compile('<skin default[\s\S]*?<\/skin>').findall(content)
    skindefaultorig  = skindefault[0] if (len(skindefault) > 0) else ''
    lookandfeelorig = re.compile('<lookandfeel>[\s\S]*?<\/lookandfeel>').findall(content)
    lookandfeel  = lookandfeelorig[0] if (len(lookandfeelorig) > 0) else ''
    try:
        localfile2 = open(GUIFIX, mode='r')
        content2 = file.read(localfile2)
        file.close(localfile2)
        skinsettingscontent = re.compile('<skinsettings>[\s\S]*?<\/skinsettings>').findall(content2)
        skinsettingstext  = skinsettingscontent[0] if (len(skinsettingscontent) > 0) else ''
        skindefaultcontent = re.compile('<skin default[\s\S]*?<\/skin>').findall(content2)
        skindefaulttext  = skindefaultcontent[0] if (len(skindefaultcontent) > 0) else ''
        lookandfeelcontent = re.compile('<lookandfeel>[\s\S]*?<\/lookandfeel>').findall(content2)
        lookandfeeltext  = lookandfeelcontent[0] if (len(lookandfeelcontent) > 0) else ''
        replacefile = content.replace(skinorig,skinsettingstext).replace(lookandfeel,lookandfeeltext).replace(skindefaultorig,skindefaulttext)
        writefile = open(GUINEW, mode='w+')
        writefile.write(str(replacefile))
        writefile.close()
    except:
        print"NO GUISETTINGS DOWNLOADED"
    if os.path.exists(GUI):
        os.remove(GUI)
    os.rename(GUINEW,GUI)
    try:
        os.remove(GUIFIX)
    except:
        pass
    if choice3 == 1:
        extract.all(backup_zip,DATABASE,dp) #This folder first needs zipping up
        if choice4 !=1:
            shutil.rmtree(tempdbpath)
    #    os.remove(backup_zip)
    dp.close()
    os.makedirs(guitemp)
    time.sleep(1)
    xbmc.executebuiltin('UnloadSkin()') 
    time.sleep(1)
    xbmc.executebuiltin('ReloadSkin()')
    time.sleep(1)
    xbmc.executebuiltin("ActivateWindow(appearancesettings)")
    while xbmc.executebuiltin("Window.IsActive(appearancesettings)"):
        xbmc.sleep(500)
    try: xbmc.executebuiltin("LoadProfile(Master user)")
    except: pass
    dialog.ok('Step 1 complete','Change the skin to: [COLOR=lime]'+skins,'[/COLOR]Once done come back and choose install step 2 which will','re-install the guisettings.xml - this file contains all custom skin settings.')
    xbmc.executebuiltin("ActivateWindow(appearancesettings)")
    CHECK_GUITEMP(guisettingslink)
#---------------------------------------------------------------------------------------------------
#Check whether or not the guisettings fix has been done, loops on a timer.
def CHECK_GUITEMP(url):
    time.sleep(120)
    if os.path.exists(guitemp):
        choice = xbmcgui.Dialog().yesno('Run step 2 of install', 'You still haven\'t completed step 2 of the', 'install. Would you like to complete it now?', '', nolabel='No, not yet',yeslabel='Yes, complete setup')
        if choice == 0:
            CHECK_GUITEMP(url)
        elif choice == 1:
            try: xbmc.executebuiltin("PlayerControl(Stop)")       
            except: pass
            xbmc.executebuiltin("ActivateWindow(appearancesettings)")
            GUI_MERGE(url)
#---------------------------------------------------------------------------------------------------
#Function to restore a zip file 
def CHECK_DOWNLOAD_PATH():
#    if zip == '':
#        dialog.ok('[COLOR=blue][B]AMO[/B][/COLOR][COLOR=green]box[/COLOR] Custom Builds Tool','You have not set your ZIP Folder.\nPlease update the addon settings and try again.','','')
#        ADDON.openSettings(sys.argv[0])
    path = xbmc.translatePath(os.path.join(zip,'testCBFolder'))
    if not os.path.exists(zip):
        dialog.ok('[COLOR=blue][B]AMO[/B][/COLOR][COLOR=green]box[/COLOR] Custom Builds Tool','The download location you have stored does not exist .\nPlease update the addon settings and try again.','','')        
        ADDON.openSettings(sys.argv[0])
#---------------------------------------------------------------------------------------------------
#Function to restore a local copy of a CB file
#### THIS CODE BLOCK SHOULD BE MERGED INTO THE RESTORE_COMMUNITY FUNCTION BUT I RAN OUT OF TIME TO DO IT CLEANLY ###
def RESTORE_LOCAL_COMMUNITY():
    import time
    exitfunction=0
    choice4=0
    CHECK_DOWNLOAD_PATH()
    filename = xbmcgui.Dialog().browse(1, 'Select the backup file you want to restore', 'files', '.zip', False, False, USB)
    if filename == '':
        return
    if os.path.exists(GUINEW):
        if os.path.exists(GUI):
            os.remove(GUINEW)
        else:
            os.rename(GUINEW,GUI)
    if os.path.exists(GUIFIX):
        os.remove(GUIFIX)
    if not os.path.exists(tempfile): #Function for debugging, creates a file that was created in previous call and subsequently deleted when run
        localfile = open(tempfile, mode='w+')
    if os.path.exists(guitemp):
        os.removedirs(guitemp)
    try: os.rename(GUI,GUINEW) #Rename guisettings.xml to guinew.xml so we can edit without XBMC interfering.
    except:
        dialog.ok("NO GUISETTINGS!",'No guisettings.xml file has been found.', 'Please exit XBMC and try again','')
        return
    choice = xbmcgui.Dialog().yesno(name, 'We highly recommend backing up your existing build before', 'installing any builds.', 'Would you like to perform a backup first?', nolabel='Backup',yeslabel='Install')
    if choice == 0:
        mybackuppath = xbmc.translatePath(os.path.join(USB,'AMObox Custom Builds','My Builds'))
        if not os.path.exists(mybackuppath):
            os.makedirs(mybackuppath)
        vq = _get_keyboard( heading="Enter a name for this backup" )
        if ( not vq ): return False, 0
        title = urllib.quote_plus(vq)
        backup_zip = xbmc.translatePath(os.path.join(mybackuppath,title+'.zip'))
        exclude_dirs_full =  ['plugin.program.amoboxcbtool']
        exclude_files_full = ["xbmc.log","xbmc.old.log","kodi.log","kodi.old.log",'.DS_Store','.setup_complete','XBMCHelper.conf']
        message_header = "Creating full backup of existing build"
        message1 = "Archiving..."
        message2 = ""
        message3 = "Please Wait"
        ARCHIVE_CB(HOME, backup_zip, message_header, message1, message2, message3, exclude_dirs_full, exclude_files_full)
    choice3 = xbmcgui.Dialog().yesno(name, 'Would you like to keep your existing database', 'files or overwrite? Overwriting will wipe any', 'existing music or video library you may have scanned in.', nolabel='Overwrite',yeslabel='Keep Existing')
    if choice3 == 0: pass
    elif choice3 == 1:
        if os.path.exists(tempdbpath):
            shutil.rmtree(tempdbpath)
        try:
            shutil.copytree(DATABASE, tempdbpath, symlinks=False, ignore=shutil.ignore_patterns("Textures13.db","Addons16.db","Addons15.db","saltscache.db-wal","saltscache.db-shm","saltscache.db","onechannelcache.db")) #Create temp folder for databases, give user option to overwrite existing library
        except:
            choice4 = xbmcgui.Dialog().yesno(name, 'There was an error trying to backup some databases.', 'Continuing may wipe your existing library. Do you', 'wish to continue?', nolabel='No, cancel',yeslabel='Yes, overwrite')
            if choice4 == 1: pass
            if choice4 == 0: exitfunction=1;return
        backup_zip = xbmc.translatePath(os.path.join(USB,'Database.zip'))
        ARCHIVE_FILE(tempdbpath,backup_zip)
    if exitfunction == 1:
        return
    else:
        time.sleep(1)
        readfile = open(CBADDONPATH, mode='r')
        default_contents = readfile.read()
        readfile.close()
        READ_ZIP(filename)
        dp.create("[COLOR=blue][B]AMO[/B][/COLOR][COLOR=green]box[/COLOR] Custom Builds Tool","Checking ",'', 'Please Wait')
        dp.update(0,"", "Extracting Zip Please Wait")
        extract.all(filename,HOME,dp)
        time.sleep(1)
        clean_title = ntpath.basename(filename)
        writefile = open(idfile, mode='w+')
        writefile.write('id="none"\nname="'+clean_title+' [COLOR=yellow](Partially installed)[/COLOR]"\nversion="none"')
        writefile.close()
        cbdefaultpy = open(CBADDONPATH, mode='w+')
        cbdefaultpy.write(default_contents)
        cbdefaultpy.close()
        try:
            os.rename(GUI,GUIFIX)
        except:
            print"NO GUISETTINGS DOWNLOADED"
        time.sleep(1)
        localfile = open(GUINEW, mode='r') #Read the original skinsettings tags and store in memory ready to replace in guinew.xml
        content = file.read(localfile)
        file.close(localfile)
        skinsettingsorig = re.compile('<skinsettings>[\s\S]*?<\/skinsettings>').findall(content)
        skinorig  = skinsettingsorig[0] if (len(skinsettingsorig) > 0) else ''
        skindefault = re.compile('<skin default[\s\S]*?<\/skin>').findall(content)
        skindefaultorig  = skindefault[0] if (len(skindefault) > 0) else ''
        lookandfeelorig = re.compile('<lookandfeel>[\s\S]*?<\/lookandfeel>').findall(content)
        lookandfeel  = lookandfeelorig[0] if (len(lookandfeelorig) > 0) else ''
        try:
            localfile2 = open(GUIFIX, mode='r')
            content2 = file.read(localfile2)
            file.close(localfile2)
            skinsettingscontent = re.compile('<skinsettings>[\s\S]*?<\/skinsettings>').findall(content2)
            skinsettingstext  = skinsettingscontent[0] if (len(skinsettingscontent) > 0) else ''
            skindefaultcontent = re.compile('<skin default[\s\S]*?<\/skin>').findall(content2)
            skindefaulttext  = skindefaultcontent[0] if (len(skindefaultcontent) > 0) else ''
            lookandfeelcontent = re.compile('<lookandfeel>[\s\S]*?<\/lookandfeel>').findall(content2)
            lookandfeeltext  = lookandfeelcontent[0] if (len(lookandfeelcontent) > 0) else ''
            replacefile = content.replace(skinorig,skinsettingstext).replace(lookandfeel,lookandfeeltext).replace(skindefaultorig,skindefaulttext)
            writefile = open(GUINEW, mode='w+')
            writefile.write(str(replacefile))
            writefile.close()
        except:
            print"NO GUISETTINGS DOWNLOADED"
        if os.path.exists(GUI):
            os.remove(GUI)
        os.rename(GUINEW,GUI)
        try:
            os.remove(GUIFIX)
        except:
            pass
        if choice3 == 1:
            extract.all(backup_zip,DATABASE,dp) #This folder first needs zipping up
            if choice4 !=1:
                shutil.rmtree(tempdbpath)
        #    os.remove(backup_zip)
        os.makedirs(guitemp)
        time.sleep(1)
        xbmc.executebuiltin('UnloadSkin()') 
        time.sleep(1)
        xbmc.executebuiltin('ReloadSkin()')
        time.sleep(1)
        xbmc.executebuiltin("ActivateWindow(appearancesettings)")
        while xbmc.executebuiltin("Window.IsActive(appearancesettings)"):
            xbmc.sleep(500)
        try: xbmc.executebuiltin("LoadProfile(Master user)")
        except: pass
        dialog.ok('[COLOR=blue][B]AMO[/B][/COLOR][COLOR=green]box[/COLOR] Custom Builds Tool','Step 1 complete. Now please change the skin to','the one this build was designed for. Once done come back','to this addon and restore the guisettings_fix.zip')        
        xbmc.executebuiltin("ActivateWindow(appearancesettings)")
#---------------------------------------------------------------------------------------------------
#Function to restore a local copy of guisettings_fix
def RESTORE_LOCAL_GUI():
    import time
    CHECK_DOWNLOAD_PATH()
    guifilename = xbmcgui.Dialog().browse(1, 'Select the guisettings zip file you want to restore', 'files', '.zip', False, False, USB)
    if guifilename == '':
        return
    else:
        local=1
        GUISETTINGS_FIX(guifilename,local)  
#---------------------------------------------------------------------------------------------------
#Function to restore a zip file 
def REMOVE_BUILD():
    CHECK_DOWNLOAD_PATH()
    filename = xbmcgui.Dialog().browse(1, 'Select the backup file you want to DELETE', 'files', '.zip', False, False, USB)
    if filename == '':
        return
    clean_title = ntpath.basename(filename)
    choice = xbmcgui.Dialog().yesno('Delete Backup File', 'This will completely remove '+clean_title, 'Are you sure you want to delete?', '', nolabel='No, Cancel',yeslabel='Yes, Delete')
    if choice == 0:
        return
    elif choice == 1:
        os.remove(filename)
#---------------------------------------------------------------------------------------------------
#Kill Commands - these will make sure guisettings.xml sticks.
#ANDROID STILL NOT WORKING
def killxbmc():
    choice = xbmcgui.Dialog().yesno('Force Close XBMC/Kodi', 'We will now attempt to force close Kodi, this is', 'to be used if having problems with guisettings.xml', 'sticking. Would you like to continue?', nolabel='No, Cancel',yeslabel='Yes, Close')
    if choice == 0:
        return
    elif choice == 1:
        pass
    myplatform = platform()
    print "Platform: " + str(myplatform)
    if myplatform == 'osx': # OSX
        print "############   try osx force close  #################"
        try: os.system('killall -9 XBMC')
        except: pass
        try: os.system('killall -9 Kodi')
        except: pass
        dialog.ok("[COLOR=red][B]WARNING  !!![/COLOR][/B]", "If you\'re seeing this message it means the force close", "was unsuccessful. Please force close XBMC/Kodi [COLOR=lime]DO NOT[/COLOR] exit cleanly via the menu.",'')
    elif myplatform == 'linux': #Linux
        print "############   try linux force close  #################"
        try: os.system('killall XBMC')
        except: pass
        try: os.system('killall Kodi')
        except: pass
        try: os.system('killall -9 xbmc.bin')
        except: pass
        try: os.system('killall -9 kodi.bin')
        except: pass
        dialog.ok("[COLOR=red][B]WARNING  !!![/COLOR][/B]", "If you\'re seeing this message it means the force close", "was unsuccessful. Please force close XBMC/Kodi [COLOR=lime]DO NOT[/COLOR] exit cleanly via the menu.",'')
    elif myplatform == 'android': # Android  
        print "############   try android force close  #################"
        try: os.system('adb shell am force-stop org.xbmc.kodi')
        except: pass
        try: os.system('adb shell am force-stop org.kodi')
        except: pass
        try: os.system('adb shell am force-stop org.xbmc.xbmc')
        except: pass
        try: os.system('adb shell am force-stop org.xbmc')
        except: pass        
        dialog.ok("[COLOR=red][B]WARNING  !!![/COLOR][/B]", "Your system has been detected as Android, you ", "[COLOR=yellow][B]MUST[/COLOR][/B] force close XBMC/Kodi. [COLOR=lime]DO NOT[/COLOR] exit cleanly via the menu.","Pulling the power cable is the simplest method to force close.")
    elif myplatform == 'windows': # Windows
        print "############   try windows force close  #################"
        try:
            os.system('@ECHO off')
            os.system('tskill XBMC.exe')
        except: pass
        try:
            os.system('@ECHO off')
            os.system('tskill Kodi.exe')
        except: pass
        try:
            os.system('@ECHO off')
            os.system('TASKKILL /im Kodi.exe /f')
        except: pass
        try:
            os.system('@ECHO off')
            os.system('TASKKILL /im XBMC.exe /f')
        except: pass
        dialog.ok("[COLOR=red][B]WARNING  !!![/COLOR][/B]", "If you\'re seeing this message it means the force close", "was unsuccessful. Please force close XBMC/Kodi [COLOR=lime]DO NOT[/COLOR] exit cleanly via the menu.","Use task manager and NOT ALT F4")
    else: #ATV
        print "############   try atv force close  #################"
        try: os.system('killall AppleTV')
        except: pass
        print "############   try raspbmc force close  #################" #OSMC / Raspbmc
        try: os.system('sudo initctl stop kodi')
        except: pass
        try: os.system('sudo initctl stop xbmc')
        except: pass
        dialog.ok("[COLOR=red][B]WARNING  !!![/COLOR][/B]", "If you\'re seeing this message it means the force close", "was unsuccessful. Please force close XBMC/Kodi [COLOR=lime]DO NOT[/COLOR] exit via the menu.","Your platform could not be detected so just pull the power cable.")
#---------------------------------------------------------------------------------------------------
#Root menu of addon
def CATEGORIES(localbuildcheck,localversioncheck,id,unlocked):
    addDir('Addon Settings','settings','Addon_Settings','SETTINGS.png','','','Addon Settings')
    addDir('Backup My Content','url','backup_option','Backup.png','','','Back Up Your Data')
    addDir('Restore My Content','url','restore_option','Restore.png','','','Restore Your Data')
    addDir('Additional Tools','url','additional_tools','Additional_Tools.png','','','Restore Your Data')
#---------------------------------------------------------------------------------------------------
# Dialog to tell users how to register

#---------------------------------------------------------------------------------------------------
# Function to open addon settings
def Addon_Settings():
    ADDON.openSettings(sys.argv[0])
#---------------------------------------------------------------------------------------------------
# Extra tools menu
def ADDITIONAL_TOOLS():
    addDir('Delete Builds From Device','url','remove_build','Delete_Builds.png','','','Delete Build')
    addDir('Wipe My Setup (Fresh Start)','url','wipe_xbmc','Fresh_Start.png','','','Wipe your special XBMC/Kodi directory which will revert back to a vanillla build.')
    addDir('Convert Physical Paths To Special',HOME,'fix_special','Special_Paths.png','','','Convert Physical Paths To Special')
    addDir('Check my download location','url','check_storage','Check_Download.png','','','Force close kodi, to be used as last resort')
    addDir('Force Close Kodi','url','kill_xbmc','Kill_XBMC.png','','','Force close kodi, to be used as last resort')
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
#Get keyboard
def _get_keyboard( default="", heading="", hidden=False ):
    """ shows a keyboard and returns a value """
    keyboard = xbmc.Keyboard( default, heading, hidden )
    keyboard.doModal()
    if ( keyboard.isConfirmed() ):
        return unicode( keyboard.getText(), "utf-8" )
    return default
#-----------------------------------------------------------------------------------------------------------------    
#Create backup menu
def BACKUP_OPTION():
#    dialog.ok("[COLOR=red][B]VERY IMPORTANT![/COLOR][/B]", 'If you plan on creating a backup to share [COLOR=lime]ALWAYS[/COLOR] make', 'sure you\'ve deleted your addon_data folder as uninstalling', 'an addon does not remove personal data such as passwords.')             
    addDir('[COLOR=lime]Full Backup[/COLOR]','url','community_backup','Backup.png','','','Back Up Your Full System')
    addDir('Backup Just Your Addons','addons','restore_zip','Backup.png','','','Back Up Your Addons')
    addDir('Backup Just Your Addon UserData','addon_data','restore_zip','Backup.png','','','Back Up Your Addon Userdata')
    addDir('Backup Guisettings.xml',GUI,'restore_backup','Backup.png','','','Back Up Your guisettings.xml')
    if os.path.exists(FAVS):
        addDir('Backup Favourites.xml',FAVS,'restore_backup','Backup.png','','','Back Up Your favourites.xml')
    if os.path.exists(SOURCE):
        addDir('Backup Source.xml',SOURCE,'restore_backup','Backup.png','','','Back Up Your sources.xml')
    if os.path.exists(ADVANCED):
        addDir('Backup Advancedsettings.xml',ADVANCED,'restore_backup','Backup.png','','','Back Up Your advancedsettings.xml')
    if os.path.exists(KEYMAPS):
        addDir('Backup Advancedsettings.xml',KEYMAPS,'restore_backup','Backup.png','','','Back Up Your keyboard.xml')
    if os.path.exists(RSS):
        addDir('Backup RssFeeds.xml',RSS,'restore_backup','Backup.png','','','Back Up Your RssFeeds.xml')
#---------------------------------------------------------------------------------------------------
#Create restore menu
def CHECK_LOCAL_INSTALL():
    localfile = open(idfile, mode='r')
    content = file.read(localfile)
    file.close(localfile)
    localbuildmatch = re.compile('name="(.+?)"').findall(content)
    localbuildcheck  = localbuildmatch[0] if (len(localbuildmatch) > 0) else ''
    if localbuildcheck == "Incomplete":
        choice = xbmcgui.Dialog().yesno("Finish Restore Process", 'If you\'re certain the correct skin has now been set click OK', 'to finish the install process, once complete XBMC/Kodi will', ' then close. Do you want to finish the install process?', yeslabel='Yes',nolabel='No')
        if choice == 1:
            FINISH_LOCAL_RESTORE()
        elif choice ==0:
            return
#---------------------------------------------------------------------------------------------------
def FINISH_LOCAL_RESTORE():
    os.remove(idfile)
    os.rename(idfiletemp,idfile)
    xbmc.executebuiltin('UnloadSkin')    
    xbmc.executebuiltin("ReloadSkin")
    dialog.ok("Local Restore Complete", 'XBMC/Kodi will now close.', '', '')
    xbmc.executebuiltin("Quit")      
#---------------------------------------------------------------------------------------------------
# Dialog to warn users about local guisettings fix.
def LocalGUIDialog():
    dialog.ok("Restore local guisettings fix", "You should [COLOR=lime]ONLY[/COLOR] use this option if the guisettings fix", "is failing to download via the addon. Installing via this","method will mean you do not receive any updates")
    RESTORE_LOCAL_GUI()
#---------------------------------------------------------------------------------------------------
#Create restore menu
def RESTORE_OPTION():
    CHECK_LOCAL_INSTALL()
    addDir('[COLOR=lime]RESTORE LOCAL BUILD[/COLOR]','url','restore_local_CB','Restore.png','','','Back Up Your Full System')
    addDir('[COLOR=dodgerblue]Restore Local guisettings file[/COLOR]','url','LocalGUIDialog','Restore.png','','','Back Up Your Full System')
    
    if os.path.exists(os.path.join(USB,'addons.zip')):   
        addDir('Restore Your Addons','addons','restore_zip','Restore.png','','','Restore Your Addons')

    if os.path.exists(os.path.join(USB,'addon_data.zip')):   
        addDir('Restore Your Addon UserData','addon_data','restore_zip','Restore.png','','','Restore Your Addon UserData')           

    if os.path.exists(os.path.join(USB,'guisettings.xml')):
        addDir('Restore Guisettings.xml',GUI,'resore_backup','Restore.png','','','Restore Your guisettings.xml')
    
    if os.path.exists(os.path.join(USB,'favourites.xml')):
        addDir('Restore Favourites.xml',FAVS,'resore_backup','Restore.png','','','Restore Your favourites.xml')
        
    if os.path.exists(os.path.join(USB,'sources.xml')):
        addDir('Restore Source.xml',SOURCE,'resore_backup','Restore.png','','','Restore Your sources.xml')
        
    if os.path.exists(os.path.join(USB,'advancedsettings.xml')):
        addDir('Restore Advancedsettings.xml',ADVANCED,'resore_backup','Restore.png','','','Restore Your advancedsettings.xml')        

    if os.path.exists(os.path.join(USB,'keyboard.xml')):
        addDir('Restore Advancedsettings.xml',KEYMAPS,'resore_backup','Restore.png','','','Restore Your keyboard.xml')
        
    if os.path.exists(os.path.join(USB,'RssFeeds.xml')):
        addDir('Restore RssFeeds.xml',RSS,'resore_backup','Restore.png','','','Restore Your RssFeeds.xml')    
#---------------------------------------------------------------------------------------------------
#Function to restore a previously backed up zip, this includes full backup, addons or addon_data.zip
def RESTORE_ZIP_FILE(url):
    CHECK_DOWNLOAD_PATH()
    if 'addons' in url:
        ZIPFILE = xbmc.translatePath(os.path.join(USB,'addons.zip'))
        DIR = ADDONS
        to_backup = ADDONS
        
        backup_zip = xbmc.translatePath(os.path.join(USB,'addons.zip'))
    else:
        ZIPFILE = xbmc.translatePath(os.path.join(USB,'addon_data.zip'))
        DIR = ADDON_DATA
        
    if 'Backup' in name:
        DeletePackages() 
        import zipfile
        import sys
        dp.create("[COLOR=blue][B]AMO[/B][/COLOR][COLOR=green]box[/COLOR] Custom Builds Tool","Backing Up",'', 'Please Wait')
        zipobj = zipfile.ZipFile(ZIPFILE , 'w', zipfile.ZIP_DEFLATED)
        rootlen = len(DIR)
        for_progress = []
        ITEM =[]
        for base, dirs, files in os.walk(DIR):
            for file in files:
                ITEM.append(file)
        N_ITEM =len(ITEM)
        for base, dirs, files in os.walk(DIR):
            for file in files:
                for_progress.append(file) 
                progress = len(for_progress) / float(N_ITEM) * 100  
                dp.update(int(progress),"Backing Up",'[COLOR yellow]%s[/COLOR]'%file, 'Please Wait')
                fn = os.path.join(base, file)
                if not 'temp' in dirs:
                    if not 'plugin.program.amoboxcbtool' in dirs:
                       import time
                       FORCE= '01/01/1980'
                       FILE_DATE=time.strftime('%d/%m/%Y', time.gmtime(os.path.getmtime(fn)))
                       if FILE_DATE > FORCE:
                           zipobj.write(fn, fn[rootlen:]) 
        zipobj.close()
        dp.close()
        dialog.ok("[COLOR=blue][B]AMO[/B][/COLOR][COLOR=green]box[/COLOR] Custom Builds Tool", "You Are Now Backed Up", '','')   
    else:

        dp.create("[COLOR=blue][B]AMO[/B][/COLOR][COLOR=green]box[/COLOR] Custom Builds Tool","Checking ",'', 'Please Wait')
        
        import time
        dp.update(0,"", "Extracting Zip Please Wait")
        extract.all(ZIPFILE,DIR,dp)
        time.sleep(1)
        xbmc.executebuiltin('UpdateLocalAddons ')    
        xbmc.executebuiltin("UpdateAddonRepos")        
        if 'Backup' in name:
            killxbmc()
            dialog.ok("AMObox Custom Builds - Install Complete", 'To ensure the skin settings are set correctly XBMC will now', 'close. If XBMC doesn\'t close please force close (pull power', 'or force close in your OS - [COLOR=lime]DO NOT exit via XBMC menu[/COLOR])')
        else:
            dialog.ok("[COLOR=blue][B]AMO[/B][/COLOR][COLOR=green]box[/COLOR] Custom Builds Tool", "You Are Now Restored", '','')        
#---------------------------------------------------------------------------------------------------
#Function to restore a backup xml file (guisettings, sources, RSS)
def RESTORE_BACKUP_XML(name,url,description):
    if 'Backup' in name:
        TO_READ   = open(url).read()
        TO_WRITE  = os.path.join(USB,description.split('Your ')[1])
        
        f = open(TO_WRITE, mode='w')
        f.write(TO_READ)
        f.close() 
         
    else:
    
        if 'guisettings.xml' in description:
            a = open(os.path.join(USB,description.split('Your ')[1])).read()
            
            r='<setting type="(.+?)" name="%s.(.+?)">(.+?)</setting>'% skin
            
            match=re.compile(r).findall(a)
            for type,string,setting in match:
                setting=setting.replace('&quot;','') .replace('&amp;','&') 
                xbmc.executebuiltin("Skin.Set%s(%s,%s)"%(type.title(),string,setting))  
        else:    
            TO_WRITE   = os.path.join(url)
            TO_READ  = open(os.path.join(USB,description.split('Your ')[1])).read()
            
            f = open(TO_WRITE, mode='w')
            f.write(TO_READ)
            f.close()  
    dialog.ok("[COLOR=blue][B]AMO[/B][/COLOR][COLOR=green]box[/COLOR] Custom Builds Tool", "", 'All Done !','')
#---------------------------------------------------------------------------------------------------
#Function to delete the packages folder
def DeletePackages():
    print '############################################################       DELETING PACKAGES             ###############################################################'
    packages_cache_path = xbmc.translatePath(os.path.join('special://home/addons/packages', ''))
 
    for root, dirs, files in os.walk(packages_cache_path):
        file_count = 0
        file_count += len(files)
        
    # Count files and give option to delete
        if file_count > 0:
                        
            for f in files:
                os.unlink(os.path.join(root, f))
            for d in dirs:
                shutil.rmtree(os.path.join(root, d))
#---------------------------------------------------------------------------------------------------
#Function to delete the userdata/addon_data folder
def DeleteUserData():
    print '############################################################       DELETING USERDATA             ###############################################################'
    addon_data_path = xbmc.translatePath(os.path.join('special://home/userdata/addon_data', ''))
 
    for root, dirs, files in os.walk(addon_data_path):
        file_count = 0
        file_count += len(files)
        
    # Count files and give option to delete
        if file_count >= 0:
                        
            for f in files:
                os.unlink(os.path.join(root, f))
            for d in dirs:
                shutil.rmtree(os.path.join(root, d))        
#---------------------------------------------------------------------------------------------------
#Function to do a full wipe. Thanks to kozz for working out how to add an exclude clause so AMObox Custom Builds addon_data and addon isn't touched.
def WipeXBMC():
    if skin!= "skin.confluence":
        dialog.ok('[COLOR=blue][B]AMO[/B][/COLOR][COLOR=green]box[/COLOR] Custom Builds Tool','Please switch to the default Confluence skin','before performing a wipe.','')
        xbmc.executebuiltin("ActivateWindow(appearancesettings)")
        return
    else:
        choice = xbmcgui.Dialog().yesno("VERY IMPORTANT", 'This will completely wipe your install.', 'Would you like to create a backup before proceeding?', '', yeslabel='Yes',nolabel='No')
        if choice == 1:
            mybackuppath = xbmc.translatePath(os.path.join(USB,'AMObox Custom Builds','My Builds'))
            if not os.path.exists(mybackuppath):
                os.makedirs(mybackuppath)
            vq = _get_keyboard( heading="Enter a name for this backup" )
            if ( not vq ): return False, 0
            title = urllib.quote_plus(vq)
            backup_zip = xbmc.translatePath(os.path.join(mybackuppath,title+'.zip'))
            exclude_dirs_full =  ["plugin.program.amoboxcbtool", "plugin.video.adrxbmccustombuildswizard"]
            exclude_files_full = ["xbmc.log","xbmc.old.log","kodi.log","kodi.old.log",'.DS_Store','.setup_complete','XBMCHelper.conf']
            message_header = "Creating full backup of existing build"
            message1 = "Archiving..."
            message2 = ""
            message3 = "Please Wait"
            ARCHIVE_CB(HOME, backup_zip, message_header, message1, message2, message3, exclude_dirs_full, exclude_files_full)
    choice2 = xbmcgui.Dialog().yesno("ABSOLUTELY CERTAIN?!!!", 'Are you absolutely certain you want to wipe this install?', '', 'All addons and settings will be completely wiped!', yeslabel='Yes',nolabel='No')
    if choice2 == 0:
        return
    elif choice2 == 1:
        dp.create("[COLOR=blue][B]AMO[/B][/COLOR][COLOR=green]box[/COLOR] Custom Builds Tool","Wiping Install",'', 'Please Wait')
        try:
            for root, dirs, files in os.walk(HOME,topdown=True):
                dirs[:] = [d for d in dirs if d not in EXCLUDES]
                for name in files:
                    try:
                        os.remove(os.path.join(root,name))
                        os.rmdir(os.path.join(root,name))
                    except: pass
                        
                for name in dirs:
                    try: os.rmdir(os.path.join(root,name)); os.rmdir(root)
                    except: pass
        except: pass
    REMOVE_EMPTY_FOLDERS()
    REMOVE_EMPTY_FOLDERS()
    REMOVE_EMPTY_FOLDERS()
    REMOVE_EMPTY_FOLDERS()
    REMOVE_EMPTY_FOLDERS()
    REMOVE_EMPTY_FOLDERS()
    REMOVE_EMPTY_FOLDERS()
    dialog.ok('[COLOR=blue][B]AMO[/B][/COLOR][COLOR=green]box[/COLOR] Custom Builds Tool','Wipe Successful, please restart XBMC/Kodi for changes to take effect.','','')

#---------------------------------------------------------------------------------------------------
#Function to do remove all empty folders after delete       
def REMOVE_EMPTY_FOLDERS():
#initialize the counters
    print"########### Start Removing Empty Folders #########"
    empty_count = 0
    used_count = 0
    for curdir, subdirs, files in os.walk(HOME):
        if len(subdirs) == 0 and len(files) == 0: #check for empty directories. len(files) == 0 may be overkill
            empty_count += 1 #increment empty_count
            os.rmdir(curdir) #delete the directory
            print "successfully removed: "+curdir
        elif len(subdirs) > 0 and len(files) > 0: #check for used directories
            used_count += 1 #increment used_count
#---------------------------------------------------------------------------------------------------
#Function to do a full wipe - this is called when doing a fresh CB install.
#Thanks to kozz for working out how to add an exclude clause so AMObox Custom Builds addon_data and addon isn't touched.
def WipeInstall():
    if skin!= "skin.confluence":
        dialog.ok('[COLOR=blue][B]AMO[/B][/COLOR][COLOR=green]box[/COLOR] Custom Builds Tool','Please switch to the default Confluence skin','before performing a wipe.','')
        xbmc.executebuiltin("ActivateWindow(appearancesettings)")       
    else:
        choice = xbmcgui.Dialog().yesno("ABSOLUTELY CERTAIN?!!!", 'Are you absolutely certain you want to wipe this install?', '', 'All addons and settings will be completely wiped!', yeslabel='Yes',nolabel='No')
        if choice == 0:
            return
        elif choice == 1:
            dp.create("[COLOR=blue][B]AMO[/B][/COLOR][COLOR=green]box[/COLOR] Custom Builds Tool","Wiping Install",'', 'Please Wait')
            addonPath=xbmcaddon.Addon(id=AddonID).getAddonInfo('path'); addonPath=xbmc.translatePath(addonPath); 
            xbmcPath=os.path.join(addonPath,"..",".."); xbmcPath=os.path.abspath(xbmcPath); failed=False  
            try:
                for root, dirs, files in os.walk(xbmcPath,topdown=True):
                    dirs[:] = [d for d in dirs if d not in EXCLUDES]
                    for name in files:
                        try: os.remove(os.path.join(root,name))
                        except: pass
                    for name in dirs:
                        try: os.rmdir(os.path.join(root,name))
                        except: pass
            except: pass
        REMOVE_EMPTY_FOLDERS()
        REMOVE_EMPTY_FOLDERS()
        REMOVE_EMPTY_FOLDERS()
        REMOVE_EMPTY_FOLDERS()
        REMOVE_EMPTY_FOLDERS()
        REMOVE_EMPTY_FOLDERS()
        REMOVE_EMPTY_FOLDERS()
#---------------------------------------------------------------------------------------------------
#Get params and clean up into string or integer
def get_params():
        param=[]
        paramstring=sys.argv[2]
        if len(paramstring)>=2:
                params=sys.argv[2]
                cleanedparams=params.replace('?','')
                if (params[len(params)-1]=='/'):
                        params=params[0:len(params)-2]
                pairsofparams=cleanedparams.split('&')
                param={}
                for i in range(len(pairsofparams)):
                        splitparams={}
                        splitparams=pairsofparams[i].split('=')
                        if (len(splitparams))==2:
                                param[splitparams[0]]=splitparams[1]
                                
        return param
#---------------------------------------------------------------------------------------------------
#Main addDirectory function - xbmcplugin.addDirectoryItem()
def addDirectoryItem(handle, url, listitem, isFolder):
    xbmcplugin.addDirectoryItem(handle, url, listitem, isFolder)
#---------------------------------------------------------------------------------------------------
#Add a standard directory and grab fanart and iconimage from artpath defined in global variables
def addDir(name,url,mode,iconimage = '',fanart = '',video = '',description = ''):
    if len(iconimage) > 0:
        iconimage = ARTPATH + iconimage
    else:
        iconimage = 'DefaultFolder.png'
        
    u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&fanart="+urllib.quote_plus(fanart)+"&video="+urllib.quote_plus(video)+"&description="+urllib.quote_plus(description)
    ok=True
    liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo( type="Video", infoLabels={ "Title": name, "Plot": description } )
    liz.setProperty( "Fanart_Image", fanart )
    liz.setProperty( "Build.Video", video )
    if (mode==None) or (mode=='grab_builds_premium') or (mode=='Search_Private') or (mode=='additional_tools') or (mode=='search_builds') or (mode=='manual_search') or (mode=='restore_option') or (mode=='backup_option') or (mode=='cb_root_menu') or (mode=='genres') or (mode=='grab_builds') or (mode=='community_menu') or (mode=='instructions') or (mode=='countries')or (url==None) or (len(url)<1):
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
    else:
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=False)
    return ok
#---------------------------------------------------------------------------------------------------
def addDir2(name,url,mode,iconimage = '',fanart = '',video = '',description = ''):
    if len(iconimage) > 0:
        iconimage = ARTPATH + iconimage
    else:
        iconimage = 'DefaultFolder.png'
        
    u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&fanart="+urllib.quote_plus(fanart)+"&video="+urllib.quote_plus(video)+"&description="+urllib.quote_plus(description)
    ok=True
    liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo( type="Video", infoLabels={ "Title": name, "Plot": description } )
    liz.setProperty( "Fanart_Image", fanart )
    liz.setProperty( "Build.Video", video )
    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
    return ok
#---------------------------------------------------------------------------------------------------
#Add a standard directory for the builds. Essentially the same as above but grabs unique artwork from previous call
def addBuildDir(name,url,mode,iconimage,fanart,video,description,skins,guisettingslink):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&iconimage="+urllib.quote_plus(iconimage)+"&fanart="+urllib.quote_plus(fanart)+"&video="+urllib.quote_plus(video)+"&description="+urllib.quote_plus(description)+"&skins="+urllib.quote_plus(skins)+"&guisettingslink="+urllib.quote_plus(guisettingslink)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name, "Plot": description } )
        liz.setProperty( "Fanart_Image", fanart )
        liz.setProperty( "Build.Video", video )
        if (mode==None) or (mode=='restore_option') or (mode=='backup_option') or (mode=='cb_root_menu') or (mode=='genres') or (mode=='grab_builds') or (mode=='community_menu') or (mode=='instructions') or (mode=='countries')or (url==None) or (len(url)<1):
            ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
        else:
            ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=False)
        return ok
#---------------------------------------------------------------------------------------------------
#Add a directory for the description, this requires multiple string to be called from previous menu
def addDescDir(name,url,mode,iconimage,fanart,buildname,author,version,description,updated,skins,videoaddons,audioaddons,programaddons,pictureaddons,sources,adult):
        iconimage = ARTPATH + iconimage
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&iconimage="+urllib.quote_plus(iconimage)+"&fanart="+urllib.quote_plus(fanart)+"&author="+urllib.quote_plus(author)+"&description="+urllib.quote_plus(description)+"&version="+urllib.quote_plus(version)+"&buildname="+urllib.quote_plus(buildname)+"&updated="+urllib.quote_plus(updated)+"&skins="+urllib.quote_plus(skins)+"&videoaddons="+urllib.quote_plus(videoaddons)+"&audioaddons="+urllib.quote_plus(audioaddons)+"&buildname="+urllib.quote_plus(buildname)+"&programaddons="+urllib.quote_plus(programaddons)+"&pictureaddons="+urllib.quote_plus(pictureaddons)+"&sources="+urllib.quote_plus(sources)+"&adult="+urllib.quote_plus(adult)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name, "Plot": description } )
        liz.setProperty( "Fanart_Image", fanart )
        liz.setProperty( "Build.Video", video )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=False)
        return ok
#---------------------------------------------------------------------------------------------------
#Function to return the platform XBMC is currently running on.
#Could possibly do away with this and use xbmc.getInfoLabel("System.BuildVersion") in the killxbmc function
def platform():
    if xbmc.getCondVisibility('system.platform.android'):
        return 'android'
    elif xbmc.getCondVisibility('system.platform.linux'):
        return 'linux'
    elif xbmc.getCondVisibility('system.platform.windows'):
        return 'windows'
    elif xbmc.getCondVisibility('system.platform.osx'):
        return 'osx'
    elif xbmc.getCondVisibility('system.platform.atv2'):
        return 'atv2'
    elif xbmc.getCondVisibility('system.platform.ios'):
        return 'ios'
#---------------------------------------------------------------------------------------------------
# Addon starts here
params=get_params()
url=None
name=None
buildname=None
updated=None
author=None
version=None
mode=None
iconimage=None
description=None
video=None
link=None
skins=None
videoaddons=None
audioaddons=None
programaddons=None
audioaddons=None
sources=None
local=None

try:
        url=urllib.unquote_plus(params["url"])
except:
        pass
try:
        guisettingslink=urllib.unquote_plus(params["guisettingslink"])
except:
        pass
try:
        name=urllib.unquote_plus(params["name"])
except:
        pass
try:
        iconimage=urllib.unquote_plus(params["iconimage"])
except:
        pass
try:
        fanart=urllib.unquote_plus(params["fanart"])
except:
        pass
try:        
        mode=str(params["mode"])
except:
        pass
try:
        link=urllib.unquote_plus(params["link"])
except:
        pass
try:
        skins=urllib.unquote_plus(params["skins"])
except:
        pass
try:
        videoaddons=urllib.unquote_plus(params["videoaddons"])
except:
        pass
try:
        audioaddons=urllib.unquote_plus(params["audioaddons"])
except:
        pass
try:
        programaddons=urllib.unquote_plus(params["programaddons"])
except:
        pass
try:
        pictureaddons=urllib.unquote_plus(params["pictureaddons"])
except:
        pass
try:
        local=urllib.unquote_plus(params["local"])
except:
        pass
try:
        sources=urllib.unquote_plus(params["sources"])
except:
        pass
try:
        adult=urllib.unquote_plus(params["adult"])
except:
        pass
try:
        buildname=urllib.unquote_plus(params["buildname"])
except:
        pass
try:
        updated=urllib.unquote_plus(params["updated"])
except:
        pass
try:
        version=urllib.unquote_plus(params["version"])
except:
        pass
try:
        author=urllib.unquote_plus(params["author"])
except:
        pass
try:        
        description=urllib.unquote_plus(params["description"])
except:
        pass
try:        
        video=urllib.unquote_plus(params["video"])
except:
        pass

        
if mode==None or url==None or len(url)<1:
        VideoCheck()
elif mode=='backup_option':
        BACKUP_OPTION()
elif mode=='additional_tools':
        print "############   ADDITIONAL TOOLS  #################"
        ADDITIONAL_TOOLS()   
elif mode=='community_backup':
        print "############   COMMUNITY BACKUP  #################"
        COMMUNITY_BACKUP()
elif mode=='restore_backup':
        print "############   RESTORE_BACKUP_XML #################"
        RESTORE_BACKUP_XML(name,url,description)
elif mode=='restore_option':
        print "############   RESTORE_OPTION   #################"
        RESTORE_OPTION()
elif mode=='restore_zip':
        print "############   RESTORE_ZIP_FILE   #################"
        RESTORE_ZIP_FILE(url)         
elif mode=='restore_community':
        print "############   RESTORE_COMMUNITY BUILD  #################"
        RESTORE_COMMUNITY(name,url,video,description,skins,guisettingslink)        
elif mode=='wipe_xbmc':
        print "############   WIPE XBMC   #################"
        WipeXBMC()
elif mode=='description':
        print "############   BUILD DESCRIPTION   #################"
        DESCRIPTION(name,url,buildname,author,version,description,updated,skins,videoaddons,audioaddons,programaddons,pictureaddons,sources,adult)
elif mode=='community_menu':
        print "############   BUILD COMMUNITY LIST   #################"
        COMMUNITY_MENU(url)        
elif mode=='play_video':
        print "############   PLAY VIDEO   #################"
        PLAYVIDEO(url)
elif mode=='instructions':
        print "############   INSTRUCTIONS MENU   #################"
        INSTRUCTIONS(url)
elif mode=='instructions_1':
        print "############   SHOW INSTRUCTIONS 1   #################"
        Instructions_1()
elif mode=='instructions_2':
        print "############   SHOW INSTRUCTIONS 2   #################"
        Instructions_2()
elif mode=='instructions_3':
        print "############   SHOW INSTRUCTIONS 3   #################"
        Instructions_3()
elif mode=='instructions_4':
        print "############   SHOW INSTRUCTIONS 4   #################"
        Instructions_4()
elif mode=='instructions_5':
        print "############   SHOW INSTRUCTIONS 5   #################"
        Instructions_5()
elif mode=='instructions_6':
        print "############   SHOW INSTRUCTIONS 6   #################"
        Instructions_6()
elif mode=='cb_root_menu':
        print "############   AMObox Custom Builds Menu   #################"
        CB_Root_Menu()
elif mode=='genres':
        print "############   Build GENRE1 Menu   #################"
        GENRES()
elif mode=='countries':
        print "############   Build COUNTRIES Menu   #################"
        COUNTRIES()
elif mode=='search_builds':
        print "############   MANUAL SEARCH BUILDS   #################"
        SEARCH_BUILDS()
elif mode=='manual_search':
        print "############   MANUAL SEARCH BUILDS   #################"
        MANUAL_SEARCH()
elif mode=='grab_builds':
        print "############   GRAB PUBLIC BUILDS   #################"
        grab_builds(url)
elif mode=='grab_builds_premium':
        print "############   GRAB PREMIUM BUILDS   #################"
        grab_builds_premium(url)
elif mode=='guisettingsfix':
        print "############   GUISETTINGS FIX   #################"
        GUISETTINGS_FIX(url,local)
elif mode=='showinfo':
        print "############   SHOW BASIC BUILD INFO   #################"
        SHOWINFO(url)
elif mode=='remove_build':
        print "############   SHOW BASIC BUILD INFO   #################"
        REMOVE_BUILD()
elif mode=='kill_xbmc':
        print "############   ATTEMPT TO KILL XBMC/KODI   #################"
        killxbmc()
elif mode=='fix_special':
        print "############   FIX SPECIAL PATHS   #################"
        FIX_SPECIAL(url)
elif mode=='restore_local_CB':
        print "############   FIX SPECIAL PATHS   #################"
        RESTORE_LOCAL_COMMUNITY()
elif mode=='restore_local_gui':
        print "############   FIX SPECIAL PATHS   #################"
        RESTORE_LOCAL_GUI()
elif mode=='Addon_Settings':
        print "############   Open Addon Settings   #################"
        Addon_Settings()
elif mode=='Register':
        print "############   Open Register dialog   #################"
        Register()
elif mode=='LocalGUIDialog':
        print "############   Open Local GUI dialog   #################"
        LocalGUIDialog()
elif mode=='Search_Private':
        print "############   Private search   #################"
        PRIVATE_SEARCH(url)
elif mode=='check_storage':
        print "############   Check Storage Location   #################"
        CheckPath.CheckPath()
xbmcplugin.endOfDirectory(int(sys.argv[1]))