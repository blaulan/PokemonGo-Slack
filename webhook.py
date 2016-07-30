#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import logging
from flask import Flask, request
from alarm import Alaem_Manager
from threading import Thread


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(module)14s] [%(levelname)7s] %(message)s'
)
log = logging.getLogger()

app = Flask(__name__)
alerts = Alaem_Manager()


@app.route('/',methods=['POST'])
def trigger_alert():
    log.debug('POST request response has been triggered.')
    data = json.loads(request.data.decode('utf-8'))
    if data['type'] == 'pokemon':
        log.debug('POST request is a pokemon ({pokemon_id}).'.format(**data['message']))
        Thread(target=alerts.trigger_pkmn, args=(data['message'], )).start()
    elif data['type'] == 'location':
        log.debug('POST request is a location ({lat},{lon}).'.format(**data['message']))
        global alerts
        alerts.lat = data['message']['lat']
        alerts.lon = data['message']['lon']

    return 'OK'


if __name__ == '__main__':
    with open('config.json', 'r') as f:
        config = json.loads(f.read())
    if config['debug']:
        logging.getLogger().setLevel(logging.DEBUG)
        logging.getLogger('alarm').setLevel(logging.DEBUG)
    else :
        logging.getLogger('requests').setLevel(logging.DEBUG)
        logging.getLogger('alarm').setLevel(logging.INFO)

    app.run(debug=config['debug'], host=config['host'], port=config['port'])
