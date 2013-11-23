#!/usr/bin/python
# -*- coding: iso-8859-15 -*-

from httpclient import HttpClient

from json import loads as importJSON
from json import dumps as exportJSON

from subprocess import Popen
from shlex import split

#
# Connect to www.filmon.com and
# retrieve RTMP streaming properties (JSON)
#
channel = '14'
quality = 'low'
client = HttpClient(debug=True)
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

#
# Parse the channel list (JSON) and
# finde the RTMP settings for BBC One
#

config = importJSON( str(client.Page) )[0]
open(config['alias']+' '+quality+'.json','w').write( exportJSON(config, sort_keys=True, indent=4) );
print 'Channel: '+config['title']
print 'URL:     '+config['serverURL']
print 'Stream:  '+config['streamName']

#
# Setup custom RTMP handler with the parsed RTMP properties
#
rtmp_config = {
          'pageUrl':    'http://www.filmon.com/tv/bbc-one',
          'swfUrl':     'http://www.filmon.com/tv/modules/FilmOnTV/files/fla.shapp/filmon/FilmonPlayer.swf?v=28',
          'flashVer':   'LNX 11,1,102,55',
          'rtmp':       config['serverURL'],
          'playpath':   config['streamName']
          }

def rtmpdump(config):
    cmd = 'rtmpdump'
    for key in config.keys():
        cmd += ' --'+key+'="'+config[key]+'"'
    cmd += ' --live -o stream.mp4'
    return cmd 

#
# Begin streaming and save stream to disk
#
cmd = rtmpdump(rtmp_config)
print cmd
Popen(split(cmd)).wait()
