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
    if data['type'] == 'pokemon' :
        log.debug('POST request is a pokemon.')
        Thread(target=alerts.trigger_pkmn, args=(data['message']), ).start()
    elif data['type'] == 'pokestop' :
        log.debug('Pokestop notifications not yet implimented.')
    elif data['type'] == 'pokegym' :
        log.debug('Pokegym notifications not yet implimented.')

    return 'OK'


if __name__ == '__main__':
    with open('config.json', 'r') as f:
        config = json.loads(f.read())
    if config['debug']:
        logging.basicConfig(level=logging.DEBUG)
    else :
        logging.getLogger('werkzeug').setLevel(logging.ERROR)
        logging.getLogger('requests').setLevel(logging.DEBUG)
        logging.getLogger('alarm').setLevel(logging.INFO)

    app.run(debug=config['debug'],host=config['host'], port=config['port'])
