from GoogleManagement import GoogleContacts, GoogleDirectory
from Settings import Secret
from Auth import InternalAuth
import gdata
import json

class APIFunctions(object):

    def __init__(self, config):
        self.google_user = config.google_user
        self.google_password = config.google_password
        self.config = config
        crypto = Secret(config.secret)
        self.contact_client = GoogleContacts(crypto.GetEnCryptedSecret(config.google_user), crypto.GetEnCryptedSecret(config.google_password))
        self.directory_client = GoogleDirectory(crypto.GetEnCryptedSecret(config.google_user), crypto.GetEnCryptedSecret(config.google_password))
        self.types = {\
                'google': {\
                    'profile': {\
                        'edit': {\
                            'user_profile':  self.__UpdateProfile__\
                        },\
                        'get': {\
                            'user_profile':  self.__GetProfile__\
                            }\
                             
                    },\
                    'users': {\
                        'get': {\
                            'user': self.__GetUser__\
                        },\
                        'edit': {\
                            'user': self.__UpdateUser__\
                            }\
                    }\
                },\
                'users': {\
                    'internal': {\
                        'add': {\
                            'user': self.__AddInternalUser__\
                        },\
                        'delete': {\
                            'user': self.__DeleteInternalUser__\
                        },\
                    },\
                },\
        }
    
    def __UpdateProfile__(self, data):
        user = self.contact_client.GetProfile(data['email'])
        user = self.contact_client.ModifyProfile(user, data)
        res = self.contact_client.UpdateProfile(user)    
        return "OK"

    def __UpdateUser__(self, data):
        if 'email' in data:    
            name_index = data['email'].find('@')
            name = data['email'][:name_index]
            profile = self.directory_client.RetrieveUser(name)
            profile = self.directory_client.ModifyUser(profile, data)
            res = self.directory_client.UpdateUser(name, profile)    
        return "OK"    

    def __GetProfilePhoto__(self):
#        def download_photo(gd_client, contact_url):
#https://developers.google.com/google-apps/contacts/v3/?csw=1#retrieving_a_contacts_photo    
        contact = gd_client.GetContact(contact_url)
        hosted_image_binary = gd_client.GetPhoto(contact_entry)
        image_file = open('test.jpg', 'wb')
        image_file.write(hosted_image_binary)
        image_file.close()

    def __GetProfile__(self, data):
        user = self.contact_client.GetProfile(data['email'])
        data = self.contact_client.XMLXtoJSON(user)
        return data

    def __GetUser__(self, data):
        user = self.directory_client.RetrieveUser(data['login'])
        data = self.directory_client.XMLXtoJSON(user)
        return data

    def __AddInternalUser__(self, data):
        newUser = InternalAuth(self.config)
        newUser.AddUser(data)

    def __DeleteInternalUser__(self, data):    
        User = InternalAuth(self.config)
        print data
        User.DeleteUser(data)

    def execute(self, obj):    
        if self.types[obj['type']][obj['api']][obj['action']][obj['object']] and obj['data']:
            return self.types[obj['type']][obj['api']][obj['action']][obj['object']](obj['data']) 

    def getApiTypes(self):
        return self.types
