'''
    Scratch Statistics Fetcher v1.0.1
    Created for use with Scratch Statistics Server v1.0.1

    Created by Scratch user, Gaza101.
    Licensed under GNU General Public License v3.
    www.garethpw.net
'''

import json
from HTMLParser import HTMLParser
from urllib2 import urlopen

class FollowParser(HTMLParser):
    def __init__(self):
        self.reset()
        self.tag_h2 = False #Used so we can tell if we're in the heading when processing the HTML
    def handle_starttag(self,tag,attrs):
        if tag == "h2":
            self.tag_h2 = True #Update to True when we're in the heading
    def handle_endtag(self,tag):
        if tag == "h2":
            self.tag_h2 = False #Update to False when we leave the heading
    def handle_data(self,data):
        if self.tag_h2: #When in the heading,
            try:
                self.value = int(data[data.index('(')+1:data.index(')')]) #Attempt to grab and save the number from inside the brackets
            except ValueError: #If we fail, do nothing and move on
                pass

def get_user_info(user,to=1):
    u = json.loads(urlopen("https://api.scratch.mit.edu/users/"+user,timeout=to).read().decode("utf-8"))
    info = {}
    info['id'],info['joined'],info['country'] = u['id'],u['history']['joined'],u['profile']['country']
    return info

def get_user_following_count(user,to=1):
    p = FollowParser()
    p.feed(urlopen("https://scratch.mit.edu/users/"+user+"/following/",timeout=to).read().decode("utf-8"))
    return p.value

def get_user_followers_count(user,to=1):
    p = FollowParser()
    p.feed(urlopen("https://scratch.mit.edu/users/"+user+"/followers/",timeout=to).read().decode("utf-8"))
    return p.value
        
def get_user_project_stats(user,project,to=1):
    return json.loads(urlopen("https://api.scratch.mit.edu/users/"+user+"/projects/"+str(project),timeout=to).read().decode("utf-8"))['stats']

def get_user_projects_stats(user,to=1):
    ps = [0]
    info = {"comments": 0,"favorites": 0,"loves": 0,"views": 0}
    o = 0
    while ps != []:
        ps = json.loads(urlopen("https://api.scratch.mit.edu/users/"+user+"/projects?offset="+str(o),timeout=to).read().decode("utf-8"))
        for p in ps:
            for k,v in p['stats'].iteritems():
                info[k] += v
        o += len(ps)
    return info

def get_user_dynamic_stats(user,to=1):
    info = {"following": get_user_following_count(user,to),
            "followers": get_user_followers_count(user,to)}
    info['stats'] = get_user_projects_stats(user,to)
    return info

def get_user_all_stats(user,to=1):
    info = get_user_info(user,to)
    info.update(get_user_dynamic_stats(user,to))
    return info
