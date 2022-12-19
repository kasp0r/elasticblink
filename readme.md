## README

### Introduction
`Elasticblink` is a basic Python application which monitors the health status of an Elasticsearch (ES)
cluster and outputs the health as a color on a Blinkstick USB LED. Currently, this application operates with 
Elasticsearch 7.x or below clusters. 

![nano_gif](./resources/elasticblink_test_pattern.gif)

### Requirements

To the use the application you'll require:
* An Elasticsearch cluster (https://www.elastic.co/guide/en/elasticsearch/reference/7.17/index.html)
* One Blinkstick (https://www.blinkstick.com). This script was tested with a Blinkstick Nano (https://www.blinkstick.com/products/blinkstick-nano)
* Parameters to connect to the Elasticsearch cluster (config.json)
* Optional: Raspberry Pi 4 to execute on. Details on deploying Elasticsearch 7.x on a Raspberry Pi may be found here: https://rudiball.com/wp/a-basic-install-of-elasticsearch-on-a-raspberry-pi-4

### Setup and Configuration

You'll need Python 3. This setup assumes the existence of PIP. The `requirements.txt` file contains pacakages for installation.
```commandline
pip install -r requirements.txt
```

A base configuration file can be found in the root directory (`config.json`). This file handles credentials and parameters for connection
to the Elasticsearch cluster as well as color configurations for `Elasticblink`.

Example configuration:
```json
{
  "elastic_credentials": {
    "protocol": "http",
    "host": "192.168.1.10",
    "port": 9200,
    "user": "changeme",
    "pass": "changeme"
  },
  "cluster_name": "elastic_cluster",
  "poll_period_seconds": 60,
  "status_color": {
    "green": [0, 0, 255],
    "yellow": [255, 255, 0],
    "red" : [255, 0, 0]
  }
}
```

The `elasic_credentials` section of the configuration is required and used for specifying the Elasticsearch host and user credentials. The `protocol` can be specified as `http` or `https`.
In this example we've used the IP address `192.168.1.10` to reference the master ES node, but another `hostname` can easily be provided. Default `port` and `user` and `pass` details are also
supplied. 

The `cluster_name` references the cluster which will be monitored from the `cat/health` endpoint. This is configured in the Elasticsearch configuration YAMLs. It can also be found by visiting the `_cat/health` endpoint. 

A `poll_period_seconds` specifies how often the cluster will be polled for its status. By default this is set to `60` seconds. 

The `status_color` dictionary is read raw for referencing status. Elasticsearch typically uses three colors to define status (green, yellow and red). Each status is associated with a list of integers representing Red-Green-Blue values with a minimum of 0 and a maximum of 255.
The configuration allows one to use or modify these statuses. You can for instance make the `green` status another color (non-green) by modifying the RGB array value. In such case that the Blinkstick cannot communicate with the Elasticsearch cluster, then it will show a holding `white` LED light. A message about an issue determining the cluster will be produced in the log.

### Usage

Once configuration has been set the usage of the script is fairly straightforward with the `--help` flag showing help on usage:

```bash
# HELP
> python elasticblink.py --help 
usage: elasticblink.py [-h] --config CONFIG [--initialisation_test {yes,no}]

Version 1.0. Simple script to monitor an ElasticSearch cluster or node status
and produce a status on a Blinkstick.

options:
  -h, --help            show this help message and exit
  --config CONFIG, -k CONFIG
                        Configuration file to read parameters and
                        configurations from (default: config.json)
  --initialisation_test {yes,no}, -t {yes,no}
                        Turn off or on the initialisation test executed before
                        monitoring. This test will check both the Blinkstick
                        and the Elasticsearch connection.

Process finished with exit code 0
```

Example execution. The Blinkstick should shine the status of the Elasticsearch cluster.
```bash
# Example usage of configuration config.json
> python elasticblink.py -k=config.json 
2022-12-18 12:52:27,588 [INFO] Arguments: Namespace(config='config.json', initialisation_test='yes')
2022-12-18 12:52:27,588 [INFO] Configuration JSON read from: /mnt/elasticblink/config.json
2022-12-18 12:52:29,207 [INFO] Blinkstick: BS044665-3.0 turned off
2022-12-18 12:52:29,213 [INFO] GET http://192.168.2.10:9200/ [status:200 request:0.006s]
2022-12-18 12:52:29,215 [INFO] HEAD http://192.168.2.10:9200/ [status:200 request:0.001s]
2022-12-18 12:52:29,215 [INFO] Elasticsearch Connection Ping Test SUCCESS!
2022-12-18 12:52:30,253 [INFO] GET http://192.168.2.10:9200/ [status:200 request:0.004s]
2022-12-18 12:52:30,255 [INFO] GET http://192.168.2.10:9200/_cat/health?format=json [status:200 request:0.002s]
```

When first executed the script performs, by default, a test where it rotates the colors of the Blinkstick between red, green and blue to check if requests are working.

### Release Notes
* v1.0 Provision of base script connects to Elasticsearch 7.x clusters and works with Blinkstick Nano.

### References

* Blinkstick: https://www.blinkstick.com
* Elasticsearch 7.x: https://www.elastic.co/guide/en/elasticsearch/reference/7.17/index.html