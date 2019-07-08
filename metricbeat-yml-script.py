import logging
import os
import socket

from ruamel.yaml import YAML
from modules import setups

# set vars and consts
logzio_url = os.environ["LOGZIO_URL"]
logzio_token = os.environ["LOGZIO_TOKEN"]

SOCKET_TIMEOUT = 3
METRICBEAT_CONF_PATH = "/etc/metricbeat/metricbeat.yml"
MODULES_DIR = "modules.d/"


logging.basicConfig(format='%(asctime)s\t\t%(levelname)s\t[%(name)s]\t%(filename)s:%(lineno)d\t%(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


def _is_open():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(SOCKET_TIMEOUT)
    host, port = logzio_url.split(":")
    result = sock.connect_ex((host, int(port)))
    if result == 0:
        logger.info("Connection Established")
    else:
        logger.error("Can't connect to the listener, please remove any firewall settings to host:{0} port:{1}"
                     .format(host, port))
        raise ConnectionError


def _add_modules():
    try:
        modules = [m.strip() for m in os.environ["LOGZIO_MODULES"].split(",")]
        if len(modules) == 1 and modules[0] == "custom":
            return
    except KeyError:
        logger.error("Required at least one module")
        raise RuntimeError

    yaml = YAML()
    supported_modules = dict((name, setup) for name, setup in setups)
    for module in modules:
        if module in supported_modules:
            conf = supported_modules[module]()
            with open("{0}{1}{2}".format(MODULES_DIR, module, ".yml"), "w+") as yml:
                logger.debug("Adding the following conf: {}".format(conf))
                yaml.dump(conf, yml)
        else:
            logger.error("Unsupported module: {}".format(module))
            raise RuntimeError


def _add_shipping_data():
    yaml = YAML()
    with open("metricbeat.yml") as yml:
        conf = yaml.load(yml)

    conf["output.logstash"]["hosts"].append(logzio_url)
    conf["fields"]["token"] = logzio_token
    conf["fields"]["type"] = os.getenv("LOGZIO_TYPE", "docker-collector-metrics")

    with open(METRICBEAT_CONF_PATH, "w+") as yml:
        logger.debug("Using the following meatricbeat configuration: {}".format(conf))
        yaml.dump(conf, yml)


_is_open()
_add_modules()
_add_shipping_data()

os.system("metricbeat -e")
