#!/usr/bin/python
# -*- coding: iso-8859-15 -*-

import datetime

from httpclient import HttpClient

from json import loads,dumps

from subprocess import Popen
from shlex import split

#
# Connect to www.filmon.com and
# retrieve RTMP streaming properties (JSON)
#
channel = '14'
quality = 'high'

website = 'http://www.filmon.com/tv/bbc-one'
fallback_player = 'http://www.filmon.com/tv/modules/FilmOnTV/files/flashapp/filmon/FilmonPlayer.swf?v=56'

client = HttpClient(debug=True)

# Extract URL to FilmOn player
client.GET(website)
page = str(client.Page)
key = '{"streamer":"'
i = page.find(key)
if i > -1:
    j = page.find('"',i+len(key))
    player = page[i+len(key):j].replace('\\/','/')
    if player.find('.swf') > -1:
        player = 'http://www.filmon.com'+player
    else:
        player = fallback_player
else:
    player = fallback_player
print 'Player: '+player

# Get channel info
client.GET('http://www.filmon.com/index/popout?channel_id='+channel+'&quality='+quality)
client.POST(
            '/ajax/getChannelInfo',
            {
             'channel_id': channel,
             'quality':    quality
             },
            {
             'Origin':          'http://www.filmon.com',
             'X-Requested-With':'XMLHttpRequest',
             'Content-Type':    'application/x-www-form-urlencoded; charset=UTF-8',
             'DNT':             '1'
             }
            )
reply = str(client.Page)
print ''

#
# Parse the channel list (JSON) and
# finde the RTMP settings for BBC One
#

open(str(channel)+' '+quality+'.raw.json','w').write( reply )
config = loads(reply)
open(config['alias']+' '+quality+'.formatted.json','w').write( dumps(config, sort_keys=True, indent=4) )
print 'Channel:     '+config['title']
print 'URL:         '+config['serverURL']

#
# Setup custom RTMP handler with the parsed RTMP properties
#
i = config['serverURL'].find('/',8)
host = config['serverURL'][len('rtmp://'):i]
app = config['serverURL'][i+1:]
print 'Host:        '+host
print 'App:         '+app
print 'Playpath:    '+config['streamName']
rtmp_config = {
          'pageUrl':    website,
          'swfUrl':     player,
          'flashVer':   'LNX 11,1,102,55',
          'protocol':   '0',
          'host':       host,
          'app':        app,
          'playpath':   config['streamName']
          }
print ''

def rtmpdump(params):
    cmd = 'rtmpdump'
    for key in params.keys():
        cmd += ' --'+key+'="'+params[key]+'"'
    cmd += ' -o "'+config['title']+' '+datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+'.mp4"'
    return cmd 

#
# Begin streaming and save stream to disk
#
cmd = rtmpdump(rtmp_config)
print cmd
Popen(split(cmd)).wait()
