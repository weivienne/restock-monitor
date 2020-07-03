import requests
import sys 
import time
import random
import json
import sqlite3
from log import log as log
from threading import Thread
from datetime import datetime
from bs4 import BeautifulSoup as soup
from discord_hooks import Webhook
from multiprocessing import Process


class FileNotFound(Exception):
    ''' Raised when a file required for the program to operate is missing. '''

class NoDataLoaded(Exception):
    ''' Raised when the file is empty. '''

def read_from_txt(path):
    '''
    (None) -> list of str
    Loads up all sites from the sitelist.txt file in the root directory.
    Returns the sites as a list
    '''
    # Initialize variables
    raw_lines = []
    lines = []

    # Load data from the txt file
    try:
        f = open(path, "r")
        raw_lines = f.readlines()
        f.close()

    # Raise an error if the file couldn't be found
    except:
        log('e', "Couldn't locate <" + path + ">.")
        raise FileNotFound()

    if(len(raw_lines) == 0):
        raise NoDataLoaded()

    # Parse the data
    for line in raw_lines:
        lines.append(line.strip("\n"))

    # Return the data
    return lines

'''
Sends a discord alert when an item is back in stock
'''
def alert_notification(name, link):

    embed = Webhook(webhook, color=123123)

    embed.set_author(name='NSE Tropicals')
    embed.set_desc("RESTOCK: " + name.get_text())

    embed.add_field(name=name.get_text(), value=link)

    embed.set_footer(text='Created by weivienne', ts=True)

    embed.post()

'''
Send a discord alert when the monitor fail to connect to a link
'''
def alert_crash(link):
    embed = Webhook(webhook, color=123123)
    embed.set_desc("FAILED TO CONNECT: " + link)
    embed.post()

'''
Add product to the 
'''
def check_site(site):
    while(True):
        log('i', "Monitoring site <" + site + ">.")
        
        link = site
        working = False

        # Get the products on the site
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
            response = requests.get(link, timeout=3, verify=False, headers=headers)
        except Exception as e:
            log('e', "Connection to URL <" + link + "> failed.")
            log('e', str(e))
            alert_crash(link)
            break

        xml = soup(response.text, "html.parser")
        # print(xml)

        # Get the name of the restock item
        name = xml.find("h1", {"class": "product_title"})

        if (xml.findAll("p", {"class": "stock"}) and xml.findAll("p", {"class": "out-of-stock"})):
            log('i', "Out of stock: " + name.string.encode('utf-8'))
        else:
            log('i', "In stock: " + name.string.encode('utf-8'))

            alert_notification(name, link)      # Send alert
            print(".")
            sys.exit()

        print(".")

        # Wait the specified timeframe before checking the site again
        time.sleep(delay)


''' --------------------------------- RUN --------------------------------- '''

if(__name__ == "__main__"):
    # Ignore insecure messages
    requests.packages.urllib3.disable_warnings()

    # Initialize settings
    webhook = "https://discord.com/api/webhooks/727779885782925353/4q2r5eRozoyP_AdaVCy3BZelphahdmwJ7LJqnCmg782i0Ki6k4PhF_SmglxbSCiEOREV"  # Put your webhook link here
    delay = 60  # Seconds. Lots of sites = longer delay to avoid bans

    # Store sites from txt files
    websites = read_from_txt("websites.txt")
    total_sites = len(websites)
    log('i', str(total_sites) + " sites loaded.")

    # Loop through each Shopify site
    for site in websites:
        # Monitor for new products
        t = Thread(target=check_site, args=(site,))
        t.start()
        time.sleep(1)

