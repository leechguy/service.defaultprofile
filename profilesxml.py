import re
from xml.dom.minidom import parse

class ProfilesXml:
    """
    This class handles all interaction with XBMC's profiles.xml file.
    """
    def __init__(self, profilesXml):
        self.profilesXml = profilesXml

    def getText(self, nodelist):
        rc = []
        for node in nodelist:
            if node.nodeType == node.TEXT_NODE:
                rc.append(node.data)
        return ''.join(rc)

    def getUseLoginScreen(self):
        dom = parse(self.profilesXml)
        return self.getText(dom.getElementsByTagName('useloginscreen')[0].childNodes)

    def getProfileId(self, config, profile_name):
        for node in config.getElementsByTagName('profile'):
            id = self.getText(node.getElementsByTagName('id')[0].childNodes)
            name = self.getText(node.getElementsByTagName('name')[0].childNodes)
            if name == profile_name:
                return id

        # profile not found!
        return -1

    def setLastloadedValue(self, profile_name):
        dom = parse(self.profilesXml)
        id = self.getProfileId(dom, profile_name)
        if id != -1:
            lastloaded = "<lastloaded>%s</lastloaded>" % id
            profilesXml = self.readProfileXml()
            result = re.sub(r'<lastloaded>.*</lastloaded>', lastloaded, profilesXml)
            self.writeProfileXml(result)

    def readProfileXml(self):
        fh = file(self.profilesXml, 'r')
        profileXml = fh.read()
        fh.close()
        return profileXml

    def writeProfileXml(self, contents):
        fh = file(self.profilesXml, 'w')
        fh.write(contents)
        fh.close()
