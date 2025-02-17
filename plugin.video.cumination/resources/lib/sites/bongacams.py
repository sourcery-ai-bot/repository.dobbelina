'''
    Cumination
    Copyright (C) 2017 Whitecream, hdgdl, Team Cumination
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import os
import sqlite3
import json
import re
from resources.lib import utils
from resources.lib.adultsite import AdultSite

site = AdultSite('bongacams', '[COLOR hotpink]bongacams.com[/COLOR]', 'https://bongacams.com/', 'bongacams.png', 'bongacams', True)


@site.register(default_mode=True)
def Main():
    female = utils.addon.getSetting("chatfemale") == "true"
    male = utils.addon.getSetting("chatmale") == "true"
    couple = utils.addon.getSetting("chatcouple") == "true"
    trans = utils.addon.getSetting("chattrans") == "true"
    site.add_dir('[COLOR red]Refresh bongacams.com images[/COLOR]', '', 'clean_database', '', Folder=False)

    bu = "http://tools.bongacams.com/promo.php?c=226355&type=api&api_type=json&categories[]="
    if female:
        site.add_dir('[COLOR hotpink]Female[/COLOR]', '{0}female'.format(bu), 'List', '', '')
    if couple:
        site.add_dir('[COLOR hotpink]Couples[/COLOR]', '{0}couples'.format(bu), 'List', '', '')
    if male:
        site.add_dir('[COLOR hotpink]Male[/COLOR]', '{0}male'.format(bu), 'List', '', '')
    if trans:
        site.add_dir('[COLOR hotpink]Transsexual[/COLOR]', '{0}transsexual'.format(bu), 'List', '', '')
    site.add_dir('Hour\'s TOP chat rooms', 'https://bongacams.com/ajax-top-room-contest', 'List2', '', '')
    site.add_dir('New North America & Western Europe\'s contest - Queen of Queens', 'https://bongacams.com/ajax-queen-of-queens-contest', 'List3', '', '')
    site.add_dir('New international contest - Queen of Queens', 'https://bongacams.com/ajax-queen-of-queens-contest-international', 'List3', '', '')

    utils.eod()


@site.register()
def List(url):
    if utils.addon.getSetting("chaturbate") == "true":
        clean_database(False)

    data = utils._getHtml(url)
    model_list = json.loads(data)
    for model in model_list:
        img = 'https:' + model['profile_images']['thumbnail_image_big_live']
        username = model['username']
        name = model['display_name']
        age = model['display_age']
        name += f' [COLOR hotpink][{age}][/COLOR]'
        if model['hd_cam']:
            name += ' [COLOR gold]HD[/COLOR]'
        subject = ''
        if model.get('hometown'):
            subject += f"Location: {model.get('hometown')}"
        if model.get('homecountry'):
            subject += (
                f", {model.get('homecountry')}\n"
                if subject
                else f"Location: {model.get('homecountry')}\n"
            )
        if model['ethnicity']:
            subject += f"\n- {model['ethnicity']}\n"
        if model['primary_language']:
            subject += f"- Speaks {model['primary_language']}\n"
        if model['secondary_language']:
            subject = f"{subject[:-1]}, {model['secondary_language']}\n"
        if model['eye_color']:
            subject += f"- {model['eye_color']} Eyed\n"
        if model['hair_color']:
            subject = f"{subject[:-1]} {model['hair_color']}\n"
        if model['height']:
            subject += f"- {model['height']} tall\n"
        if model['weight']:
            subject += f"- {model['weight']} weight\n"
        if model['bust_penis_size']:
            subject += (
                f"- {model['bust_penis_size']} Boobs\n"
                if 'Female' in model['gender']
                else f"- {model['bust_penis_size']} Cock\n"
            )
        if model['pubic_hair']:
            subject = f"{subject[:-1]} and {model['pubic_hair']} Pubes\n"
        if model['vibratoy']:
            subject += u'- Lovense Toy\n\n'
        if model['turns_on']:
            subject += f"- Likes: {model['turns_on']}\n"
        if model['turns_off']:
            subject += f"- Dislikes: {model['turns_off']}\n\n"
        if model.get('tags'):
            subject += u', '.join(model.get('tags'))
        site.add_download_link(name, username, 'Playvid', img, subject.encode('utf-8') if utils.PY2 else subject, noDownload=True)
    utils.eod()


@site.register(clean_mode=True)
def clean_database(showdialog=True):
    conn = sqlite3.connect(utils.TRANSLATEPATH("special://database/Textures13.db"))
    try:
        with conn:
            list = conn.execute("SELECT id, cachedurl FROM texture WHERE url LIKE '%%%s%%';" % "bongacams.com")
            for row in list:
                conn.execute(f"DELETE FROM sizes WHERE idtexture LIKE '{row[0]}';")
                try:
                    os.remove(utils.TRANSLATEPATH(f"special://thumbnails/{row[1]}"))
                except:
                    pass
            conn.execute("DELETE FROM texture WHERE url LIKE '%%%s%%';" % "bongacams.com")
            if showdialog:
                utils.notify('Finished', 'bongacams.com images cleared')
    except:
        pass


@site.register()
def Playvid(url, name):
    vp = utils.VideoPlayer(name)
    vp.progress.update(25, "[CR]Loading video page[CR]")
    try:
        postRequest = [
            ('method', 'getRoomData'),
            ('args[]', str(url)),
            ('args[]', ''),
            ('args[]', '')
        ]
        hdr = utils.base_hdrs
        hdr.update({
            'Cookie': 'bonga20120608=4dc36bf33c316636a744faef8379be54',
            'X-ab-Split-Group': 'f2085b5fd8de2b4f7c9542009568798a157a99eeeb710d9679acca6621f17672793720ada24e7a68',
            'X-Requested-With': 'XMLHttpRequest'
        })
        response = utils._postHtml('{0}tools/amf.php'.format(site.url), form_data=postRequest, headers=hdr, compression=False)
    except:
        utils.notify('Oh oh', 'Couldn\'t find a playable webcam link', icon='thumb')
        return None

    amf_json = json.loads(response)
    if amf_json['status'] == 'error':
        utils.notify('Oh oh', 'Couldn\'t find a playable webcam link', icon='thumb')
        return

    if amf_json.get('performerData', {}).get('showType') == 'private':
        utils.notify(name, 'Model in private chat', icon='thumb')
        vp.progress.close()
        return

    amf = amf_json.get('localData', {}).get('videoServerUrl')

    if amf is None:
        utils.notify(name, 'Model Offline', icon='thumb')
        vp.progress.close()
        return
    elif amf.startswith("//mobile"):
        videourl = f'https:{amf}/hls/stream_{url}.m3u8'
    else:
        videourl = f'https:{amf}/hls/stream_{url}/playlist.m3u8'

    videourl += '|User-Agent={0}'.format(utils.USER_AGENT)
    vp.progress.update(75, "[CR]Found Stream[CR]")
    vp.play_from_direct_link(videourl)


@site.register()
def List2(url):
    site.add_download_link('[COLOR red][B]Refresh[/B][/COLOR]', url, 'utils.refresh', '', '', noDownload=True)
    if utils.addon.getSetting("online_only") == "true":
        url = f'{url}?online_only=1'
        site.add_download_link('[COLOR red][B]Show all models[/B][/COLOR]', url, 'online', '', '', noDownload=True)
    else:
        site.add_download_link('[COLOR red][B]Show only models online[/B][/COLOR]', url, 'online', '', '', noDownload=True)

    if utils.addon.getSetting("chaturbate") == "true":
        clean_database(False)
    headers = {'X-Requested-With': 'XMLHttpRequest'}
    data = utils._getHtml(url, site.url, headers=headers)
    match = re.compile('class="top_ranks(.+?)class="title_h3', re.I | re.M | re.S).findall(data)
    if not match:
        match = re.compile('class="top_others(.+?)class="title_h3', re.I | re.M | re.S).findall(data)
    match = re.compile('class="top_thumb".+?href="([^"]+)".+?src="([^"]+)".+?class="mn_lc">(.+?)</span>', re.I | re.M | re.S).findall(match[0])
    for url, img, name in match:
        if 'profile' in url:
            name = f'[COLOR hotpink][Offline][/COLOR] {name}'
            url = "  "
        site.add_download_link(name, url[1:], 'Playvid', f'https:{img}', '')
    utils.eod()


@site.register()
def List3(url):
    site.add_download_link('[COLOR red][B]Refresh[/B][/COLOR]', url, 'utils.refresh', '', '', noDownload=True)
    if utils.addon.getSetting("online_only") == "true":
        url = f'{url}?online_only=1'
        site.add_download_link('[COLOR red][B]Show all models[/B][/COLOR]', url, 'online', '', '', noDownload=True)
    else:
        site.add_download_link('[COLOR red][B]Show only models online[/B][/COLOR]', url, 'online', '', '', noDownload=True)

    if utils.addon.getSetting("chaturbate") == "true":
        clean_database(False)
    headers = {'X-Requested-With': 'XMLHttpRequest'}
    data = utils._getHtml(url, site.url, headers=headers)
    match = re.compile('class="top_ranks(.+?)trs_actions', re.I | re.M | re.S).findall(data)
    match = re.compile('class="top_thumb".+?href="([^"]+)".+?src="([^"]+)".+?class="mn_lc">(.+?)</span>', re.I | re.M | re.S).findall(match[0])
    for url, img, name in match:
        if 'profile' in url:
            name = f'[COLOR hotpink][Offline][/COLOR] {name}'
            url = "  "
        site.add_download_link(name, url[1:], 'Playvid', f'https:{img}', '')
    utils.eod()


@site.register()
def online(url):
    if utils.addon.getSetting("online_only") == "true":
        utils.addon.setSetting("online_only", "false")
    else:
        utils.addon.setSetting("online_only", "true")
    utils.refresh()
