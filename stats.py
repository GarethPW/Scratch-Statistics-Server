'''
    Scratch Statistics Server v1.0.0
    Based on Scratch Comments Server v1.2.2

    Created by Scratch user, Gaza101.
    Licensed under GNU General Public License v3.
    www.garethpw.net
'''

from sys import exit as sysexit
if __name__ not in ("__main__","__builtin__"): sysexit()

# === Initialisation ===

import config,scratchapi,scratchstats
import getpass,os,time,urllib2
from io import open

def info(s,c=0,l=True,v=False,f=True):
    m = '['+["INFO","WARNING","ERROR"][c]+"] "+s
    if (not v) or (v and verbose):
        print m
    if l and logging:
        log.write(unicode(time.strftime("[%H:%M:%S] ",time.gmtime()))+unicode(m)+u'\n')
        if f:
            log.flush()
            os.fsync(log.fileno())

def custom_fallback(prompt="Password: ",stream=None):
    info("Unable to hide password. Make sure no-one else can see your screen!",1,False)
    res = getpass._raw_input(prompt)
    os.system("cls" if os.name == "nt" else "clear")
    print (  "Gaza101's Scratch Statistics Server v"+ver
            +"\nWith thanks to Dylan5797 and DadOfMrLog\n" )
    return res

getpass.fallback_getpass = custom_fallback

ver = "1.0.0"

os.system("cls" if os.name == "nt" else "clear")

print (  "Gaza101's Scratch Statistics Server v"+ver
        +"\nWith thanks to Dylan5797 and DadOfMrLog\n" )

enc = str()
stats = []
new_stats = {}
brk = False

# === Configuration ===

default_config = ( {"login_prompt"   : "true" },
                   {"username"       : ''     },
                   {"password"       : ''     },
                   {"user"           : ''     },
                   {"project"        : 0      },
                   {"delay"          : 60     },
                   {"connect_timeout": 10     },
                   {"logging"        : "true" },
                   {"verbose"        : "true" },
                   {"config_version" : 1      }  )
default_config_u = (
u'''# Prompt for login? Set to false to automagically login with preset username and
# password.
login_prompt: true

# Details used to log into Scratch if login_prompt has been set to false.
# Surround your password with quotation marks if it has whitespace at the start
# or end.
username: 
password: 

# The user to monitor.
user: 

# Project ID to send statistics to.
project: 0

# The time between each statistics update in minutes. It is recommended that
# this is not set below 10.
delay: 60

# The maximum amount of time that the program can spend retrieving statistics
# data in seconds. Leave this at 10 if you're unsure.
connect_timeout: 10

# If logging is enabled, data will be recorded to the stats.log file.
logging: true

# If verbose mode is enabled, information that would normally be recorded in the
# log alone will also be displayed in the console.
verbose: true

# Do not change this value! Seriously - it could reset your config.
config_version: 1''')

info("Loading config.yml...",l=False)

conf = config.Config("config.yml")

if (    "config_version" not in conf.config
     or conf.config['config_version'] not in (1,)
     or tuple in [type(conf.config[i]) for i in conf.config]    ):
    info("config.yml does not exist or is corrupted. Recreating with default values.",2,False)
    with open(conf.name,'r') as c, open(conf.name+".broken",'w') as b:
        c.seek(0)
        b.write(c.read())
        c.close()
        b.close()
    with open(conf.name,'w') as f:
        f.write(default_config_u)
        f.close()
    info("Please fill in config.yml appropriately and restart the program afterwards.",l=False)
    raw_input("Press enter to exit...")
    sysexit()
else:
    for i in default_config[:-1]:
        if i.keys()[0] not in conf.config:
            info(i.keys()[0]+" key missing from config.yml Recreating with default value.",1,False)
            conf.write(i)

try:
    login_prompt    = bool(  conf.config['login_prompt']    )
    username        = str(   conf.config['username']        )
    password        = str(   conf.config['password']        )
    user            = str(   conf.config['user']            )
    project         = int(   conf.config['project']         )
    delay           = float( conf.config['delay']           )
    connect_timeout = float( conf.config['connect_timeout'] )
    logging         = bool(  conf.config['logging']         )
    verbose         = bool(  conf.config['verbose']         )
    config_version  = int(   conf.config['config_version']  )
except ValueError:
    info("A key in config.yml has an illegal value. Please fix the value and restart the program.",2,False)
    raw_input("Press enter to exit...")
    sysexit()

info("config.yml loaded.",l=False)

# === Log ===

if logging:
    info("Loading stats.log...",l=False)
    try:
        log = open("stats.log",'a',encoding="utf-8-sig")
    except IOError:
        logging = False
        info("Unable to open stats.log. Continuing with logging disabled.",1)
    else:
        log.write(  u'\n'
                   +unicode(time.strftime(u"%Y-%m-%d %H:%M:%S UTC",time.gmtime()))
                   +u'\n'                                                          )
        info("stats.log loaded.")
else:
    info("Logging is disabled")

# === Authentication ===

if login_prompt:
    while True:
        username = raw_input("[PROMPT] Username: ")
        password = getpass.getpass("[PROMPT] Password: ")
        try:
            scratch = scratchapi.ScratchUserSession(username,password)
            if scratch.tools.verify_session():
                break
        except Exception:
            pass
        info("Login failed. Please try again.",2,False)
    info("Successfully logged in with account, "+username+'.')
else:
    info("Automatic login is enabled. Logging into user, "+username+'.')
    for i in range(1,6):
        info("Attempt "+str(i)+"...")
        try:
            scratch = scratchapi.ScratchUserSession(username,password)
            if scratch.tools.verify_session():
                break
        except Exception:
            pass
        if i == 5:
            info("Unsuccessful after five attempts.",2)
            raw_input("Press enter to exit...")
            sysexit()
        time.sleep(1)
    info("Successfully logged in with account, "+username+'.')

# === Main Loop ===

info("Initialisation successful.")

while True:
    while True:
        for i in range(3):
            info("Fetching statistics...",v=True)
            try:
                new_stats = scratchstats.get_user_dynamic_stats(user,connect_timeout)
            except urllib2.HTTPError as e:
                info("HTTP error "+str(e.code)+" when obtaining statistics. Does the user exist?",1,f=False)
                info("Reason: "+str(e.reason),1,v=True)
            except urllib2.URLError as e:
                info("URL error when obtaining statistics.",1,f=False)
                info("Reason: "+str(e.reason),1,v=True)
            except Exception as e:
                info("Unknown error when obtaining statistics.",1,f=False)
                info("Reason: "+str(e.__class__.__name__),1,v=True)
            else:
                if new_stats != stats:
                    stats = []
                    for k in ("following","followers"):
                        stats.append(str(new_stats[k]))
                    for k in ("views","loves","favorites","comments"):
                        stats.append(str(new_stats['stats'][k]))
                    enc = "0x"+'a'.join(stats)+'a'
                    info("Statistics generated!",v=True,f=False)
                    info("Encoded: "+(enc[:30]+"..." if len(enc) > 30 else enc),v=True,f=False)
                    info("Sending encoded data...",v=True,f=False)
                    try:
                        scratch.cloud.set_var("stats",enc,project)
                    except Exception:
                        info("Failed to send encoded data.",1)
                    else:
                        info("Successful!",v=True)
            if logging:
                log.flush()
                os.fsync(log.fileno())
            try:
                if not scratch.tools.verify_session():
                    raise Exception
            except Exception:
                brk = True
                break
            break
        if brk:
            brk = False
            break
        else:
            tc = time.time()+60*delay
            while time.time() < tc:
                time.sleep(1)
    info("Session invalidated. Did Scratch go down?",1)
    while True:
        if not verbose:
            info("Attempting to start new session...",l=False)
        for i in range(1,4):
            info("Attempting to start new session... (Attempt "+str(i)+')',v=True)
            try:
                scratch = scratchapi.ScratchUserSession(username,password)
                if scratch.tools.verify_session():
                    info("Successful!")
                    break
            except Exception:
                pass
            if i == 3:
                info("Unsuccessful. Sleeping for one minute.",1)
            else:
                time.sleep(delay)
        else:
            tc = time.time()+60*delay
            while time.time() < tc:
                time.sleep(1)
            continue
        break
