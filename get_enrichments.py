#!/usr/bin/env python
# -*- coding: utf-8 -*-

from termcolor import colored
from optparse import OptionParser
import re
import requests
import urllib
import json

from pprintpp import pprint


OPENAIRE_API_GET_SUBS = "http://api.openaire.eu/broker/subscriptions?email="

OPENAIRE_API_GET_SUB = "http://api.openaire.eu/broker/scroll/notifications/bySubscriptionId/"

OPENAIRE_API_GET_SCROLL = "http://api.openaire.eu/broker/scroll/notifications/"

# només confiar si > CONFIABLE
CONFIABLE = 0.66

orcids = []


#####
#####
#####
# https://develop.openaire.eu/broker.html
# http://api.openaire.eu/broker/swagger-ui.html#/


banner_name='''
####################################################################################
####################################################################################
####################################################################################

    ______    _______    _______  _____  ___        __        __      _______    _______                                     
   /    " \  |   __ "\  /"     "|(\"   \|"  \      /""\      |" \    /"      \  /"     "|                                    
  // ____  \ (. |__) :)(: ______)|.\\   \    |    /    \     ||  |  |:        |(: ______)                                    
 /  /    ) :)|:  ____/  \/    |  |: \.   \\  |   /' /\  \    |:  |  |_____/   ) \/    |                                      
(: (____/ // (|  /      // ___)_ |.  \    \. |  //  __'  \   |.  |   //      /  // ___)_                                     
 \        / /|__/ \    (:      "||    \    \ | /   /  \\  \  /\  |\ |:  __   \ (:      "|                                    
  \"_____/ (_______)    \_______) \___|\____\)(___/    \___)(__\_|_)|__|  \___) \_______)                                    
                                                                                                                             
  ________  ____  ____   _______    _______    _______   ________  ___________  __      ______    _____  ___    ________     
 /"       )("  _||_ " | /" _   "|  /" _   "|  /"     "| /"       )("     _   ")|" \    /    " \  (\"   \|"  \  /"       )    
(:   \___/ |   (  ) : |(: ( \___) (: ( \___) (: ______)(:   \___/  )__/  \\__/ ||  |  // ____  \ |.\\   \    |(:   \___/     
 \___  \   (:  |  | . ) \/ \       \/ \       \/    |   \___  \       \\_ /    |:  | /  /    ) :)|: \.   \\  | \___  \       
  __/  \\   \\ \__/ //  //  \ ___  //  \ ___  // ___)_   __/  \\      |.  |    |.  |(: (____/ // |.  \    \. |  __/  \\      
 /" \   :)  /\\ __ //\ (:   _(  _|(:   _(  _|(:      "| /" \   :)     \:  |    /\  |\\        /  |    \    \ | /" \   :)     
(_______/  (__________) \_______)  \_______)  \_______)(_______/       \__|   (__\_|_)\"_____/    \___|\____\)(_______/      
                                                                                                                             
  _______  _____  ___    _______    __     ______    __    __   ___      ___   _______  _____  ___  ___________              
 /"     "|(\"   \|"  \  /"      \  |" \   /" _  "\  /" |  | "\ |"  \    /"  | /"     "|(\"   \|"  \("     _   ")             
(: ______)|.\\   \    ||:        | ||  | (: ( \___)(:  (__)  :) \   \  //   |(: ______)|.\\   \    |)__/  \\__/              
 \/    |  |: \.   \\  ||_____/   ) |:  |  \/ \      \/      \/  /\\  \/.    | \/    |  |: \.   \\  |   \\_ /                 
 // ___)_ |.  \    \. | //      /  |.  |  //  \ _   //  __  \\ |: \.        | // ___)_ |.  \    \. |   |.  |                 
(:      "||    \    \ ||:  __   \  /\  |\(:   _) \ (:  (  )  :)|.  \    /:  |(:      "||    \    \ |   \:  |                 
 \_______) \___|\____\)|__|  \___)(__\_|_)\_______) \__|  |__/ |___|\__/|___| \_______) \___|\____\)    \__|    

####################################################################################
####################################################################################
####################################################################################
'''
banner_author='\t'*8+'Oriol Olivé\n'

banner=colored(banner_name,'yellow',attrs=['bold'])+'\n'+banner_author

##################################################################
##################################################################
##################################################################
##################################################################
##################################################################
# LOGS
##################################################################
##################################################################
##################################################################
##################################################################
##################################################################
def INFO(msg):
    print(colored("[+]\t%s" %msg, 'blue' , attrs=['bold']))

def SUCCESS(msg):
    print(colored("[*]\t%s" %msg, 'green' , attrs=['bold']))

def WARN(msg):
    print(colored("[*]\t%s" %msg, 'yellow' , attrs=['bold']))

def ERROR(msg):
    print(colored("[!]\t%s" %msg, 'red' , attrs=['bold']), file=sys.stderr)

##################################################################
##################################################################
##################################################################
##################################################################
##################################################################
# main
##################################################################
##################################################################
##################################################################
##################################################################
##################################################################
def main():
    # banner
    print(banner)
    
    parser = OptionParser(usage=colored("%prog -e email@example.com -f file_name", 'blue', attrs=['bold']),
    epilog=colored("ex: python %s -e email@example.com -f orcids_20210601.json" %__file__, 'blue', attrs=['bold']))

    parser.get_option("-h").__dict__['help']=colored("Mostra aquesta ajuda i surt", 'blue', attrs=['bold'])

    parser.add_option("-e", "--email", dest="email", type="string",
                      help=colored("email del manager del repositori a OPENAIRE", 'blue', attrs=['bold']), metavar="EMAIL")
                      
    parser.add_option("-f", "--file", dest="file_orcids", type="string",
                          help=colored("Fitxer on guardar el resultat", 'blue', attrs=['bold']), metavar="FILENAME")

    # get args
    (options, args) = parser.parse_args()

    # variables
    email = None
    file_orcids = None
    
    if(options.email):
        email = options.email
        if(options.file_orcids):
           file_orcids = options.file_orcids
           getSubs(email) 
        else:
           parser.print_help()
           exit(1) 
    else:
        parser.print_help()
        exit(1)
        
    count_orcids = len(orcids)
    if(count_orcids > 0):
        print("Recuperats %d ORCIDS" %count_orcids)
        
        
        with open(file_orcids, 'w') as f:
          json.dump(orcids, f, indent = 4)
          
    else:
        print("Cap ORCID recuperat")
        
    
######################
# get subscriptions
#####################
def getSubs(email):
    # escape @
    url_req = OPENAIRE_API_GET_SUBS + urllib.parse.quote_plus(email)
    
    #print(url_req)
    INFO("Buscant subscripcions x email: %s" %email)
    response = requests.get(url_req)
    if(response.status_code == 200):
        SUCCESS("Connexió amb API OPENAIRE establerta")  
        
        data = response.json()
        
        # només ORCID x ara
        for subsc in data:
            
            if(subsc['topic'] == 'ENRICH/MISSING/AUTHOR/ORCID'):
                #print(subsc['subscriptionId'])
                subId = subsc['subscriptionId']
                
                getSub(subId)
            
            
    
    
######################
# get subscription
#####################
def getSub(subId):

    url_req = OPENAIRE_API_GET_SUB + subId
    
    #print(url_req)
    INFO("Buscant subscripció: %s" %subId)
    
    getORCIDS(url_req)
    
######################
# get orcids
#####################
def getORCIDS(url_req):
    response = requests.get(url_req)
    if(response.status_code == 200):
        SUCCESS("Connexió amb API OPENAIRE establerta")  
        
        data = response.json()   
        
        completed = data['completed']
        nextId = data['id']
        values = data['values']
        
        for value in values:
            trust = value['trust']
            if(trust >= CONFIABLE):
                handle = value['originalId']
                autor = value['message']['creators[0].fullname'] 
                orcid = value['message']['creators[0].orcid'] 
                titol = value['title']
                
                print("%s %s %s [%d]" %(handle, autor, orcid, trust))
                print()
                
                item = {}
                item['autor'] = autor
                item['orcid'] = orcid
                item['titol'] = titol
                item['handle'] = handle
                
                orcids.append(item)
                
        
        #pprint(data)
        
        if(completed == False):
            url = OPENAIRE_API_GET_SCROLL + nextId
            
            INFO("NEXT: %s" %nextId)
            
            getORCIDS(url)


# load main
if __name__ == "__main__":
    main()
