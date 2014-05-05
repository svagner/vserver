import ConfigParser
import os

class Config(object):
    def __init__(self):
        ConfigFile = '/etc/vserver.cfg'
        self.config = ConfigParser.ConfigParser()
        try:
            self.config.readfp(open(ConfigFile))
        except IOError, e:
            print "Can't open config "+ConfigFile+": "+os.strerror(e.errno)
            exit(1)
        webConfig = self.config.items("web")    
        self.options = {}
        self.options['web'] = {}
        self.options['database'] = {}
        for item in webConfig:
            self.options['web'][item[0]] = item[1] 
        # Set default opetions    
        if not 'host' in self.options['web']:
            self.options['web']['host'] = '0.0.0.0'
        try:        
            self.options['web']['port'] = self.config.getint("web", "port")   
        except ConfigParser.NoOptionError, e:
            self.options['web']['port'] = 8080

        if not 'debug' in self.options['web']:
            self.options['web']['debug'] = False

        if not 'testing' in self.options['web']:
            self.options['web']['testing'] = False

        try:        
            self.options['database']['file'] = self.config.get("database", "file")   
        except ConfigParser.NoOptionError, e:
            self.options['database']['file'] = 'db.sql'
            
    def GetOptionsFor(self, section):
        if not self.options[section]:
            return
        return self.options[section]
