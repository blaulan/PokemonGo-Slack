#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import logging
from slacker import Slacker
from datetime import datetime
from math import radians, acos, sin, cos


log = logging.getLogger(__name__)


class Alaem_Manager:

    def __init__(self):
        with open('config.json', 'r') as f:
            self.config = json.loads(f.read())
            self.slack = Slack_Alarm(self.config)
            self.groups = self.config['groups']
            self.radius = {k:self.groups[v] for k,v in self.config['pokemon'].items()}
            self.lat, self.lon = [float(i) for i in self.config['poi'].split(',')]
            self.seen = {}

        with open('locales/pokemon.en.json', 'r') as f:
            self.pkmn_names = json.loads(f.read().decode('utf-8'))

    # send a notification to alarm about a found pokemon
    def trigger_pkmn(self, pkmn):
        if pkmn['encounter_id'] in self.seen:
            return

        disappear_time = datetime.utcfromtimestamp(pkmn['disappear_time'])
        pktime, pkduration = pkmn_time(disappear_time)
        distance = pkmn_dist(
            self.lat, self.lon,
            float(pkmn['latitude']), float(pkmn['longitude'])
        )
        pkinfo = {
            'id': pkmn['pokemon_id'],
            'name': self.pkmn_names[str(pkmn['pokemon_id'])],
            'link': pkmn_link(pkmn['latitude'], pkmn['longitude']),
            'duration': pkduration,
            'disappear_time': pktime,
            'distance': distance
        }

        if self.radius[pkinfo['name']] < distance:
            log.debug(u'{name} notification is disabled.'.format(**pkinfo).encode('utf-8'))
        else:
            log.info(u'{name} notication was triggered.'.format(**pkinfo).encode('utf-8'))
            self.slack.pokemon_alert(pkinfo)
            self.seen[pkmn['encounter_id']] = disappear_time

        if len(self.seen) > 10000:
            now = datetime.now()
            self.seen = {k:v for k,v in self.seen.items() if v <= now}


class Slack_Alarm:

    def __init__(self, settings):
        self.client = Slacker(settings['api_key'])
        self.channel = settings['channel']
        self.icon_url = settings['icon_url']
        self.alert_text = (
            u'<{link}|A wild *{name}* is {distance:.2f}m away!> ' +
            u'Available until {disappear_time} ({duration}).'
        )

        log.info('Slack Alarm Intialized.')
        self.client.chat.post_message(
            channel=self.channel,
            username='PokeAlarm',
            text='PokeAlarm activated! We will alert this channel about pokemon.'
        )

    def pokemon_alert(self, pkinfo):
        self.client.chat.post_message(
            channel=self.channel,
            username=pkinfo['name'].encode('utf-8'),
            text=self.alert_text.format(**pkinfo).encode('utf-8'),
            icon_url=self.icon_url.format(**pkinfo).encode('utf-8')
        )


def pkmn_link(lat, lon):
    lat_lon = '{},{}'.format(repr(lat), repr(lon))
    return 'https://www.google.com/maps/dir/Current+Location/{}'.format(lat_lon)


def pkmn_time(time):
    s = (time - datetime.now()).total_seconds()
    (m, s) = divmod(s, 60)
    (h, m) = divmod(m, 60)

    return time.strftime('%H:%M:%S'), '{:.0f}m {:.0f}s'.format(m, s)


def pkmn_dist(lat1, lon1, lat2, lon2, R=6371008):
    lat1, lon1, lat2, lon2 = (radians(i) for i in (lat1, lon1, lat2, lon2))
    return R*acos(sin(lat1)*sin(lat2)+cos(lat1)*cos(lat2)*cos(lon2-lon1))
