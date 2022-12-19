'''
Simple application which watches a specified Elasticsearch Cluster or Node and status lights a Blinkstick a color of state.
For usage with Elasticsearch 7.x (https://www.elastic.co/guide/en/elasticsearch/reference/7.17)

MIT License
Copyright (c) 2022 Rudi Ball
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

'''
import argparse
import json
import logging
import random
import time
import sys
from blinkstick import blinkstick
from elasticsearch import Elasticsearch
import pathlib
import traceback

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        #logging.FileHandler("transmitter.debug.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('elastic_blink')
version = 1.0

def generate_random_color():
    r = random.randint(100, 255)
    g = random.randint(100, 255)
    b = random.randint(100, 255)
    return [r, g, b]

def turn_off():
    for bstick in blinkstick.find_all():
        bstick.turn_off()
        logger.info(f"Blinkstick: {bstick.get_serial()} turned off")

def turn_on(base_color=[255, 0, 0]):
    for bstick in blinkstick.find_all():
        bstick.set_color(red=base_color[0], green=base_color[1], blue=base_color[2])
        logger.debug(f"Blinkstick: {bstick.get_serial()} turned on with color: {base_color}")

def set_random_color():
    for bstick in blinkstick.find_all():
        bstick.set_random_color()


def connect_to_elastic(config_json):
    if 'elastic_credentials' in config_json:
        params = config_json['elastic_credentials']
        host = f"{params['protocol']}://{params['host']}:{params['port']}"
        es = Elasticsearch(
            host,
            basic_auth=(
                str(params['user']),
                str(params['pass'])
            )
        )
        return es
    else:
        return None

def signal_unknown():
    turn_on([255, 255, 255])
    time.sleep(1)
    turn_off()
    time.sleep(1)
    turn_on([255, 255, 255])
    time.sleep(1)

def process_cluster_status(config_json, polling_time_seconds=60):
    es = connect_to_elastic(config_json)
    color_lookup = {
        "green": [0, 0, 255],
        "yellow": [255, 255, 0],
        "red": [255, 0, 0]
    } # default configuration

    if 'status_color' in config_json:
        color_lookup = config_json['status_color']
        logging.debug(f"Configuration found for `status_color`")
    if 'poll_period_seconds' in config_json:
        polling_time_seconds = int(config_json['poll_period_seconds'])
        logging.debug(f"Configuration found for `poll_period_seconds` using: {polling_time_seconds} seconds")
    logging.debug(f"Polling Elasticsearch CLUSTER Status - Poll Period in Seconds: {polling_time_seconds}")
    # check CAT Cluster status returned as JSON
    entries = es.cat.health(format='json')
    found = False
    for ent in entries:
        if ent['cluster'] == config_json['cluster_name']:
            use_color = color_lookup[ent['status']]
            turn_on(use_color)
            found = True
    if found == False:
        logging.warning(f"Could not find the cluster specified in the configuration: {config_json['cluster_name']}")
        signal_unknown()

    time.sleep(int(polling_time_seconds))

def test_colors():
    test_colors = [
        [255, 0, 0],  # red
        [0, 255, 0],  # green
        [0, 0, 255]   # blue
    ]
    for c in test_colors:
        turn_on(c)
        time.sleep(0.5)
    turn_off()


def check_elastic_status(config_json):
    es = connect_to_elastic(config_json)
    if not es.ping():
        logger.error(f"Elasticsearch Connection Ping Test FAILED. Please check your Elasticsearch configuration supplied in the config.json file.")
        exit(-1)
    else:
        logger.info(f"Elasticsearch Connection Ping Test SUCCESS!")

def do_initialisation_test(config_json):
    test_colors()
    check_elastic_status(config_json)
    turn_off()
    time.sleep(1)

def run(arguments):
    logger.info(f"Arguments: {str(arguments)}")
    config_json = dict()
    initialized = False
    path_to_config = pathlib.Path(str(arguments.config)).absolute()
    if not path_to_config.exists():
        logger.error(f"Config file specified does not exist: {path_to_config}. Please check these details.")
        exit(-1)

    # Loop and re-read the configuration at each poll - thie means you
    # can modify the configuration file during operation to push in different settings
    # during the execution
    while True:

        try:

            # read the configuration JSON file
            logging.info(f'Configuration JSON read from: {path_to_config.absolute()}')
            with open(str(path_to_config)) as json_file:
                config_json = json.load(json_file)

            # initialise
            if str(arguments.initialisation_test) == "yes" and initialized == False:
                do_initialisation_test(config_json)
                initialized = True

            if 'cluster_name' in config_json:
                process_cluster_status(config_json)
            else:
                logger.error("Missing 'cluster_name' attribute in your JSON configuration. This should be present referencing the cluster you wish to monitor")
                exit(-1)

        except KeyboardInterrupt:
            logging.info(f"Keyboard Interrupt. Exiting.")
            traceback.print_exc()
            turn_off()
            exit(-1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=f'Version {version}. Simple script to monitor an ElasticSearch cluster or node status and produce a status on a Blinkstick.')
    parser.add_argument('--config', "-k",
                        type=str,
                        required=True,
                        default='config.json',
                        help='Configuration file to read parameters and configurations from (default: config.json)')
    parser.add_argument('--initialisation_test', "-t",
                        type=str,
                        required=False,
                        default='yes',
                        choices=['yes','no'],
                        help='Turn off or on the initialisation test executed before monitoring. This test will check both the Blinkstick and the Elasticsearch connection.')
    args = parser.parse_args()
    run(arguments=args)
