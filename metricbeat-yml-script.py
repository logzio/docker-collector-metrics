import sys
from ruamel.yaml import YAML
import os
import socket


def isOpen():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(3)

    logzio_url = os.environ["LOGZIO_URL"]
    logzio_url_arr = logzio_url.split(":")

    result = sock.connect_ex((logzio_url_arr[0], int(logzio_url_arr[1])))
    if result == 0:
        print("connection established")
    else:
        print("Can't connect to the listener, please remove any firewall settings\n")
        print("""Host: %s \nPort: %s""" % (logzio_url_arr[0], logzio_url_arr[1]))
        sys.exit(1)

def add_shipping_data():
    yaml = YAML()
    with open("default_metricbeat.yml") as file:
        config_dic = yaml.load(file)

    config_dic["output.logstash"]["hosts"].append(os.environ["LOGZIO_URL"])
    config_dic["metricbeat.modules"][0]["hosts"].append("unix:///var/run/docker.sock")
    config_dic["fields"]["token"] = os.environ["LOGZIO_TOKEN"]

    with open("/etc/metricbeat/metricbeat.yml", "w+") as file:
        yaml.dump(config_dic, file)

def exclude_containers():
    yaml = YAML()
    with open("/etc/metricbeat/metricbeat.yml") as file:
        config_dic = yaml.load(file)

    exclude_list = os.environ["skipContainerName"].split(",")

    drop_event = {"drop_event": {"when": {"or": []}}}
    config_dic["metricbeat.modules"][0]["processors"] = []
    config_dic["metricbeat.modules"][0]["processors"].append(drop_event)

    for name in exclude_list:
        contains = {"contains": {"docker.container.name": name}}
        config_dic["metricbeat.modules"][0]["processors"][0]["drop_event"]["when"]["or"].append(contains)

    with open("/etc/metricbeat/metricbeat.yml", "w+") as file:
        yaml.dump(config_dic, file)

def include_containers():
    yaml = YAML()
    with open("/etc/metricbeat/metricbeat.yml") as file:
        config_dic = yaml.load(file)

    include_list = os.environ["matchContainerName"].split(",")

    drop_event = {"drop_event": {"when": {"and": []}}}
    config_dic["metricbeat.modules"][0]["processors"] = []
    config_dic["metricbeat.modules"][0]["processors"].append(drop_event)

    for name in include_list:
        contains = {"not": {"contains": {"docker.container.name": name}}}
        config_dic["metricbeat.modules"][0]["processors"][0]["drop_event"]["when"]["and"].append(contains)

    with open("/etc/metricbeat/metricbeat.yml", "w+") as file:
        yaml.dump(config_dic, file)


isOpen()

add_shipping_data()

if "matchContainerName" in os.environ and "skipContainerName" in os.environ:
    print("Can have only one of skipContainerName or matchContainerName")
    sys.exit(1)
elif "matchContainerName" in os.environ:
    include_containers()

os.system("metricbeat -e")
