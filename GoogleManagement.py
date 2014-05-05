#!/usr/bin/python
import atom
import gdata.apps.client
import gdata.data
import gdata.contacts.client
import gdata.contacts.data
import gdata
import json

class GoogleDirectory(object):
    def __init__(self, user, password):
        domain_index = user.find('@')
        domain = user[domain_index+1:]
        self.client = gdata.apps.client.AppsClient(domain=domain)
        self.client.ssl = True
        self.client.ClientLogin(email=user, password=password, source='directory_v1')

    def RetrieveAllUsers(self):    
        feed = self.client.RetrieveAllUsers()
        for i, entry in enumerate(feed.entry):
            print entry

    def RetrieveUser(self, username):    
        user = self.client.RetrieveUser(username)
        return user

    def ModifyUser(self, profile, data):
        if 'family_name' in data:
            profile.name.family_name = data['family_name']
        if 'given_name' in data:
            profile.name.given_name = data['given_name']
        return profile    

    def UpdateUser(self, username, data):    
        return self.client.UpdateUser(username, data)

    def __XMLXtoStruct(self, data):
        myData = {}
        myData['user_name'] = data.login.user_name
        myData['suspended'] = data.login.suspended
        myData['admin'] = data.login.admin
        myData['agreed_to_terms'] = data.login.agreed_to_terms
        return myData

    def XMLXtoJSON(self, data):
        if hasattr(data, '__iter__'):
            GUsers = []
            for user in data:
                GUsers.append(self.__XMLXtoStruct(user))
            return GUsers    
        else:
            return json.dumps(self.__XMLXtoStruct(data))    

class GoogleApps(object):
    def __init__(self, user, password):
        domain_index = user.find('@')
        domain = user[domain_index+1:]
        self.client = gdata.apps.client.AppsClient(domain=domain)
        self.client.ssl = True
        self.client.ClientLogin(email=user, password=password, source='apps')


class GoogleContacts(object):

    def __init__(self, user, password):
        domain_index = user.find('@')
        self.domain = user[domain_index+1:]
        self.contacts_client = gdata.contacts.client.ContactsClient(domain=self.domain)
        self.contacts_client.client_login(email=user, password=password, source='shared_contacts_profiles', account_type='HOSTED')

    def __GetContactId(self, user_email):
        feed = self.contacts_client.GetContacts()
        for i, entry in enumerate(feed.entry):
            for email in entry.email:
                print email.address
                if email.address == user_email:
                    return entry.id.text
        return        

    def __GetProfileId(self, user_email):
        feed_url = self.contacts_client.GetFeedUri(kind='profiles', contact_list=self.domain, projection='full')
        feed = self.contacts_client.get_feed(feed_url, auth_token=None, desired_class=gdata.contacts.data.ProfilesFeed)
        for i, entry in enumerate(feed.entry):
            for email in entry.email:
                if email.address == user_email:
                    return entry.id.text
        return        

    def ModifyProfile(self, user, data):
        if 'orgName' and 'orgTitle' in data:
            user.organization = gdata.data.Organization(
                label='Work',
                primary='true',
                name=gdata.data.OrgName(text=data['orgName']),
                title=gdata.data.OrgTitle(text=data['orgTitle'])
        )
        if 'phone_erize' in data and data['phone_erize'] == 'True':    
            for number in user.phone_number:
                user.phone_number.remove(number)
        if 'phone' in data:
            for key in data['phone']:
                for number in user.phone_number:
                    if number.label == key:
                        user.phone_number.remove(number)
            user.phone_number.append(gdata.data.PhoneNumber(data['phone'][key], label=key))    
        return user    

    def GetProfile(self, email):
        user = self.contacts_client.GetProfile(self.__GetProfileId(email))
        return user

    def GetProfilePhoto(self, href):
        try:
            return self.contacts_client.get_photo(href)
        except gdata.client.RequestError:    
            return '404'

    def GetAllProfiles(self):
        feed_url = self.contacts_client.GetFeedUri(kind='profiles', contact_list=self.domain, projection='full')
        feed = self.contacts_client.get_feed(feed_url, auth_token=None, desired_class=gdata.contacts.data.ProfilesFeed)
        return feed.entry       
    
    def UpdateProfile(self, user):
        return self.contacts_client.UpdateProfile(user)

    def GetContact(self, email):
        userId = self.__GetContactId(email)
        if userId:
            contact = self.contacts_client.GetContact(userId)
            return contact
        return

    def retrieve_contact(self):
        contact = self.contacts_client.GetContact('https://www.google.com/m8/feeds/contacts/default/full/contactId')
        return contact

    def CreateNewContact(self, data):
        new_contact = gdata.contacts.data.ContactEntry()
        new_contact.name = gdata.data.Name(full_name=gdata.data.FullName(text=data.name)) 
        new_contact.email.append(gdata.data.Email(address=data.email, primary='true',rel=gdata.data.WORK_REL))
        feed_url = self.contacts_client.GetFeedUri(contact_list=self.domain, projection='full')
        print feed_url

        contact_entry = self.contacts_client.CreateContact(new_contact, feed_url)
        print "Contact's ID: %s" % contact_entry

    def PrintAllContacts(self):
        feed = self.contacts_client.GetContacts()
        for i, entry in enumerate(feed.entry):
            print '\n%s %s ID: %s' % (i+1, entry.name.full_name.text, entry.id.text)
            if entry.content:
                print '    %s' % (entry.content.text)
            for email in entry.email:
                if email.primary and email.primary == 'true':
                    print '    %s' % (email.address)
            for group in entry.group_membership_info:
                print '    Member of group: %s' % (group.href)
            for extended_property in entry.extended_property:
                if extended_property.value:
                    value = extended_property.value
                else:
                    value = extended_property.GetXmlBlob()
                print '    Extended Property - %s: %s' % (extended_property.name, value)

    def XMLXtoJSON(self, data):
        GUser = {}
        GUser['given_name'] = data.name.given_name.text
        GUser['family_name'] = data.name.family_name.text
        GUser['email'] = [] 
        for email in data.email:
            GUser['email'].append(email.address)
        GUser['phone_number'] = [] 
        for phone in data.phone_number:
            Phone = {}
            Phone['label'] = phone.label
            Phone['number'] = phone.text
            GUser['phone_number'].append(Phone)
        GUser['orgName'] = data.organization.name.text
        GUser['orgTitle'] = data.organization.title.text
        GUser['birthday'] = data.birthday
        GUser['occupation'] = data.occupation
        GUser['status'] = data.status.text
        GUser['rights'] = data.rights
        GUser['priority'] = data.priority
        GUser['gender'] = data.gender
        GUser['control'] = data.control
        GUser['batch_status'] = data.batch_status
        GUser['sensitivity'] = data.sensitivity
        GUser['published'] = data.published
        return json.dumps(GUser)    
