#!/usr/bin/env python3

import os
import sys

try:
    sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
    sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))
except:
    sys.path.append("..")
    sys.path.append("../..")

from spiral import ronin

cases = {
    'JavaTokenMarker': ['Java', 'Token', 'Marker'],
    'ullMax': ['ull', 'Max'],
    'cmdextdir': ['cmd', 'ext', 'dir'],
    'jrender': ['j', 'render'],
    'mythread': ['my', 'thread'],
    'JRApiWriter': ['JR', 'Api', 'Writer'],
    'ijException': ['ij', 'Exception'],
    'pixellate': ['pixellate'],
    'hostloader': ['host', 'loader'],
    'tagcount': ['tag', 'count'],
    'calleeNode': ['callee', 'Node'],
    'WMLTimerElementImpl': ['WML', 'Timer', 'Element', 'Impl'],
    'PRINTHOOD': ['PRINT', 'HOOD'],
    'patternstok': ['patterns', 'tok'],
    'needsibm': ['needs', 'ibm'],
    'rthandler': ['rt', 'handler'],
    'finalizeLength': ['finalize', 'Length'],
    'iwebnavigation': ['iweb', 'navigation'],
    'getint': ['get', 'int'],
    'getinteger': ['get', 'integer'],
    'numberoferrorgroups': ['number', 'of', 'error', 'groups'],
    'isinstance': ['is', 'instance'],
    'nwritten': ['n', 'written'],
    'thisisatest': ['this', 'is', 'a', 'test'],
    'vframe': ['v', 'frame'],
    'xmldoc': ['xml', 'doc'],
    'singlexmin': ['single', 'x', 'min'],
    'icause': ['i', 'cause'],
    'somevar': ['some', 'var'],
    'argv': ['arg', 'v'],
    'usage_getdata': ['usage', 'get', 'data'],
    'GPSmodule': ['GPS', 'module'],
    'bigTHING': ['big', 'THING'],
    'ABCFooBar': ['ABC', 'Foo', 'Bar'],
    'getMAX': ['get', 'MAX'],
    'SqlList': ['Sql', 'List'],
    'ASTVisitor': ['AST', 'Visitor'],
    'isnumber': ['is', 'number'],
    'threshold': ['threshold'],
    'initdb': ['init', 'db'],
    'terraindata': ['terrain', 'data'],
    'trigname': ['trig', 'name'],
    'undirected': ['undirected'],
    'usemap': ['use', 'map'],
    'updatecpu': ['update', 'cpu'],
    'textnode': ['text', 'node'],
    'connectpath': ['connect', 'path'],
    'mpegts': ['mpegts'],
    'iskeyword': ['is', 'keyword'],
    'mixmonitor': ['mix', 'monitor'],
    'sandcx': ['sandcx'],
    'isbetterfile': ['is', 'better', 'file'],
    'lunch_defendj': ['lunch', 'defend', 'j'],
    'm_pk2len': ['m', 'pk', '2', 'len'],
    'pcmret': ['pcm', 'ret'],
    'hisip': ['his', 'ip'],
    'autocommit': ['autocommit'],
    'httpexceptions': ['http', 'exceptions'],
    'sampfmt': ['samp', 'fmt'],
    'uval': ['u', 'val'],
    'readcmd': ['read', 'cmd'],
    'nonnegativedecimaltype': ['nonnegative', 'decimal', 'type'],
    'filesaveas': ['file', 'save', 'as'],
    'filesave': ['file', 'save'],
    'wickedweather': ['wicked', 'weather'],
    'liquidweather': ['liquid', 'weather'],
    'driveourtrucks': ['drive', 'our', 'trucks'],
    'gocompact': ['go', 'compact'],
    'slimprojector': ['slim', 'projector'],
    'farsidebag' : ['far', 'side', 'bag'],
    'urlparser': ['url', 'parser'],
    'altscore': ['alt', 'score'],
    'rescale': ['rescale'],
    'csize': ['c', 'size'],
    'xmax': ['x', 'max'],
    'cdplayer': ['cd', 'player'],
    'cdimage': ['cd', 'image'],
    'xmin': ['x', 'min'],
    'iptool': ['ip', 'tool'],
    'getxy': ['get', 'xy'],
    'TRAinfo': ['TRA', 'info'],
    'initVtbl': ['init', 'V', 'tbl'],
}

successes = 0
failures = 0
for identifier, expected in sorted(cases.items()):
    result = ronin.split(identifier)
    if result != expected:
        failures +=1
        print('{}: {}'.format(identifier, result))
    else:
        successes +=1
print('{} failures, {} successes'.format(failures, successes))
