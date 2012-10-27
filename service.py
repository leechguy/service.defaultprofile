import os, time, xbmc, xbmcaddon
import profilesxml, settingsxml

CHECK_TIME_DISABLED = 1893477600 # unix timestamp for 1/1/2030
RESUME_TIMEOUT = 5
SLEEP_TIME = 1000

class DefaultProfile:
    addon_id = 'service.defaultprofile'
    Addon = xbmcaddon.Addon(addon_id)
    
    profiles = profilesxml.ProfilesXml(os.path.join(xbmc.translatePath('special://masterprofile'), 'profiles.xml'))
    settings = settingsxml.SettingsXml(os.path.join(xbmc.translatePath('special://masterprofile'), 'addon_data', addon_id, 'settings.xml'))


    def runService(self):

        self.log('Starting: ' + self.Addon.getAddonInfo('name') + ' v' + self.Addon.getAddonInfo('version'))

        # only allow configuration of the addon by the master user
        if self.isMasterProfile():
            self.Addon.setSetting('isMasterUser', 'true')
        else:
            self.Addon.setSetting('isMasterUser', 'false')

        use_login_screen = self.profiles.getUseLoginScreen().lower() == 'true'
        default_profile = self.getDefaultProfile()
        active_profile = xbmc.getInfoLabel('System.ProfileName')   

        self.log('Default Profile: ' + default_profile)
        self.log('Active Profile.: ' + active_profile)

        # don't waist cpu cycles when we don't use autologin 
        if not use_login_screen:
            # this can only happen when XBMC crashed
            if active_profile != default_profile and default_profile != "":
                self.log('Changing profile to the default profile: ' + default_profile)
                xbmc.executebuiltin("XBMC.LoadProfile(" + default_profile + ", prompt)")

        use_idle_timer = self.getUseIdleTimer() == 'true'
        max_idle_time = self.getMaxIdleTime() * 60
        use_resume_watchdog = self.getUseResumeWatchdog() == 'true'
        check_time = time.time()
        resume_watchdog_time = time.time()
        # run until XBMC quits
        while(not xbmc.abortRequested):

            if not use_idle_timer:
                # skip all, go to sleep
                pass
            elif xbmc.Player().isPlaying():
                # while playing media we reset the check_time to prevent that we're being
                # logged out immediately after playing stops
                check_time = time.time()
            elif xbmc.getGlobalIdleTime() == 0:
                # user activity so we reset the check_time to 'now'
                check_time = time.time()
            elif (time.time() - check_time) > max_idle_time and xbmc.getInfoLabel('System.ProfileName') != default_profile:
                idle_time = time.time() - check_time
                # set check_time to 1/1/2030 so we only swap profiles / perform logout once
                # until the user comes back
                check_time = CHECK_TIME_DISABLED
                if use_login_screen:
                    self.log("System idle for %d seconds; logging out." % idle_time)
                    xbmc.executebuiltin('System.LogOff')
                elif xbmc.getInfoLabel('System.ProfileName') != default_profile:
                    self.log("System idle for %d seconds; switching to default profile" % idle_time)
                    xbmc.executebuiltin("XBMC.LoadProfile(" + default_profile + ", prompt)")

            if use_resume_watchdog:
                if (time.time() - resume_watchdog_time) > RESUME_TIMEOUT and xbmc.getInfoLabel('System.ProfileName') != default_profile:
                    if use_login_screen:
                        self.log("System resuming after suspend; logging out.")
                        xbmc.executebuiltin('System.LogOff')
                    elif xbmc.getInfoLabel('System.ProfileName') != default_profile:
                        self.log("System resuming after suspend; switching to default profile")
                        xbmc.executebuiltin("XBMC.LoadProfile(" + default_profile + ", prompt)")
                resume_watchdog_time = time.time()

            if not xbmc.abortRequested:
                xbmc.sleep(SLEEP_TIME)

        self.log('Preparing to exit')

        default_profile = self.getDefaultProfile()
        active_profile = xbmc.getInfoLabel('System.ProfileName')

        self.log('Default Profile: ' + default_profile)
        self.log('Active Profile.: ' + active_profile)

        if active_profile != default_profile and default_profile != "":
            self.profiles.setLastloadedValue(default_profile)
            self.log('Updated profiles.xml. Set lastloaded value to profile id of: ' + default_profile)

    def getDefaultProfile(self):
        return self.getAddonSetting('defaultProfile')

    def getUseIdleTimer(self):
        return self.getAddonSetting('useIdleTimer')

    def getMaxIdleTime(self):
        max_idle_time = self.getAddonSetting('maxIdleTime').rstrip('0').rstrip('.')
        if max_idle_time == "":
            max_idle_time = "5"
        return int(max_idle_time)

    def getUseResumeWatchdog(self):
        return self.getAddonSetting('useResumeWatchdog')

    def getAddonSetting(self, setting):
        value = ""
        try:
            self.settings.parse()
            value = self.settings.getSetting(setting)
        except Exception, err:
            self.log(str(err))
        return value

    def isMasterProfile(self):
        return (xbmc.translatePath('special://masterprofile') == xbmc.translatePath('special://profile'))

    def log(self, message):
        xbmc.log('service.defaultprofile: ' + message)


