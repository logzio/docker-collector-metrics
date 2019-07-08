import logging
import os
import socket

from ruamel.yaml import YAML
from modules import setups

SOCKET_TIMEOUT = 3
METRICBEAT_CONF_PATH = "/etc/metricbeat/metricbeat.yml"
MODULES_DIR = "modules.d/"
DEFAULT_LOG_LEVEL = "INFO"
LOG_LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


def _get_logger():
    try:
        user_level = os.environ["LOGZIO_LOG_LEVEL"].upper()
        level = user_level if user_level in LOG_LEVELS else DEFAULT_LOG_LEVEL
    except KeyError:
        level = DEFAULT_LOG_LEVEL

    logging.basicConfig(format='%(asctime)s\t\t%(levelname)s\t[%(name)s]\t%(filename)s:%(lineno)d\t%(message)s',
                        level=level)
    return logging.getLogger(__name__)


def _is_open():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(SOCKET_TIMEOUT)
    host, port = url.split(":")
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
        if "custom" in modules:
            if len(modules) == 0:
                return
            else:
                logger.error("We support custom modules configuration or our own but not both")
                raise RuntimeError

    except KeyError:
        logger.error("Required at least one module")
        raise RuntimeError

    _dump_modules(modules)


def _dump_modules(modules):
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

    conf["output.logstash"]["hosts"].append(url)
    conf["fields"]["token"] = token
    conf["fields"]["type"] = os.getenv("LOGZIO_TYPE", "docker-collector-metrics")

    with open(METRICBEAT_CONF_PATH, "w+") as yml:
        logger.debug("Using the following meatricbeat configuration: {}".format(conf))
        yaml.dump(conf, yml)


url = os.environ["LOGZIO_URL"]
token = os.environ["LOGZIO_TOKEN"]
logger = _get_logger()

_is_open()
_add_modules()
_add_shipping_data()

os.system("metricbeat -e")
