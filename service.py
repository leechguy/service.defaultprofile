import os, time, xbmc, xbmcaddon
import profilesxml, settingsxml

class DefaultProfile:
    addon_id = 'service.defaultprofile'
    Addon = xbmcaddon.Addon(addon_id)
    
    profiles = profilesxml.ProfilesXml(os.path.join(xbmc.translatePath('special://masterprofile'), 'profiles.xml'))
    settings = settingsxml.SettingsXml(os.path.join(xbmc.translatePath('special://masterprofile'), 'addon_data', addon_id, 'settings.xml'))

    sleep_time = 1000


    def runService(self):

        self.log('Starting: ' + self.Addon.getAddonInfo('name') + ' v' + self.Addon.getAddonInfo('version'))


        # only allow configuration of the addon by the master user
        if self.isMasterProfile():
            self.Addon.setSetting('isMasterUser', 'true')
        else:
            self.Addon.setSetting('isMasterUser', 'false')

        useLoginScreen = self.profiles.getUseLoginScreen().lower() == 'true'

        # don't waist cpu cycles when we don't use autologin 
        if not useLoginScreen:
            default_profile = self.getDefaultProfile()
            active_profile = xbmc.getInfoLabel('System.ProfileName')   

            self.log('Default Profile: ' + default_profile)
            self.log('Active Profile.: ' + active_profile)

            # this can only happen when XBMC crashed
            if active_profile != default_profile and default_profile != "":
                self.log('Changing profile to the default profile: ' + default_profile)
                xbmc.executebuiltin("XBMC.LoadProfile(" + default_profile + ", prompt)")
        
        # run until XBMC quits
        while(not xbmc.abortRequested):
            xbmc.sleep(self.sleep_time)

        self.log('Waking up, preparing to exit')

        default_profile = self.getDefaultProfile()
        active_profile = xbmc.getInfoLabel('System.ProfileName')

        self.log('Default Profile: ' + default_profile)
        self.log('Active Profile.: ' + active_profile)

        if active_profile != default_profile and default_profile != "":
            self.profiles.setLastloadedValue(default_profile)
            self.log('Updated profiles.xml. Set lastloaded value to profile id of: ' + default_profile)

    def getDefaultProfile(self):
        profile = ""
        try:
            self.settings.parse()
            profile = self.settings.getSetting('defaultProfile')
        except Exception, err:
            self.log(str(err))
        return profile

    def isMasterProfile(self):
        return (xbmc.translatePath('special://masterprofile') == xbmc.translatePath('special://profile'))

    def log(self, message):
        xbmc.log('service.defaultprofile: ' + message)


