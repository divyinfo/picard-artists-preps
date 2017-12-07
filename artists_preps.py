# -*- coding: utf-8 -*-

PLUGIN_NAME = "Artists Preps"
PLUGIN_AUTHOR = "divyinfo"
PLUGIN_DESCRIPTION = '''<p>Standardize artist tag & album artist tag.</p>
<ul>
    <li>Convert Artist A & Artist B to Artist A; Artist B</li>
    <li>Separators can be <code>;</code> <code>&</code> <code>,</code> <code>\\</code> <code>/</code> <code>+</code></li>
    <li>Extra spaces will be stripped</li>
    <li>utf8 encoded gb2312 tag values will be converted back to regular utf8</li>
</ul>
'''
PLUGIN_VERSION = "0.1"
PLUGIN_API_VERSIONS = ["1.0"]


from picard.log import info, warning, error

from picard.metadata import register_track_metadata_processor

from picard.file import File
from picard.cluster import Cluster, ClusterList

from picard.track import Track
from picard.album import Album

from picard.ui.itemviews import BaseAction, register_album_action, register_cluster_action, register_clusterlist_action, register_track_action, register_file_action

import re, os


def sanitize_chn(s):
    try:
        return s.encode('latin1').decode('gb2312')
    except UnicodeError:
        return s

def prep_file(file):
    if (isinstance(file, File)):
        
        # info(file.__class__.__name__ + ' PrepArtistsFile called: ')
        
        for k, v in file.metadata.items():
            new_v = sanitize_chn(file.metadata[k].strip())
            if file.metadata[k] != new_v:
                # info('%s: %s -> %s', k, file.metadata[k], new_v)
                file.metadata[k] = new_v
                file.set_pending()
            else:
                # info('%s: %s', k, v)
                pass

        prep_artists(file)

        # info('---' + os.linesep)

def prep_artists(file):
    for k in ['artist', 'albumartist', 'composer', 'conductor']:
        s = re.sub(r"([^;&,\/\\+]+)\s*(;|&|,|\/|\\|\+)\s*", '\\1; ', file.metadata[k]).strip()
        if s != file.metadata[k]:
            file.metadata[k] = s
            file.set_pending()

class PrepArtistsAction(BaseAction):
    NAME = 'Prep artists'

    def callback(self, objs):
        for obj in objs:
            if (isinstance(obj, File)):
                prep_file(obj)
            elif (isinstance(obj, Cluster) or \
                isinstance(obj, ClusterList) or \
                isinstance(obj, Track) or \
                isinstance(obj, Album)):
                for f in obj.iterfiles():
                    prep_file(f)

register_file_action(PrepArtistsAction())
register_cluster_action(PrepArtistsAction())
register_clusterlist_action(PrepArtistsAction())

register_track_action(PrepArtistsAction())
register_album_action(PrepArtistsAction())