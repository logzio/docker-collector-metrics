import logging
import os
import socket
import glob

from ruamel.yaml import YAML
from modules import setups

SOCKET_TIMEOUT = 3
FIRST_CHAR = 0
METRICBEAT_CONF_PATH = "/etc/metricbeat/metricbeat.yml"
MODULES_DIR = os.environ["LOGZIO_MODULES_PATH"]
DEFAULT_LOG_LEVEL = "INFO"
LOG_LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


def _create_logger():
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
    if _custom_modules():
        logger.debug("Using custom modules")
        return
    try:
        modules = [m.strip() for m in os.environ["LOGZIO_MODULES"].split(",")]
    except KeyError:
        logger.error("Required at least one module")
        raise

    _enable_modules(modules)


def _custom_modules():
    return len(glob.glob("{}/*.yml".format(MODULES_DIR)))


def _enable_modules(modules):
    yaml = YAML()
    supported_modules = dict((name, setup) for name, setup in setups)
    for module in modules:
        if module in supported_modules:
            conf = supported_modules[module]()
            with open("{0}/{1}{2}".format(MODULES_DIR, module, ".yml"), "w+") as conf_yaml:
                logger.debug("Adding the following conf: {}".format(conf))
                yaml.dump(conf, conf_yaml)
        else:
            logger.error("Unsupported module: {}".format(module))
            raise RuntimeError


def _add_shipping_data():
    token = os.environ["LOGZIO_TOKEN"]

    yaml = YAML()
    with open("metricbeat.yml") as default_metricbeat_yaml:
        conf = yaml.load(default_metricbeat_yaml)

    conf["output.logstash"]["hosts"].append(url)
    conf["fields"]["token"] = token
    conf["fields"]["type"] = os.getenv("LOGZIO_TYPE", "docker-collector-metrics")

    additional_field = _get_additional_fields()
    for key in additional_field:
        conf["fields"][key] = additional_field[key]

    with open(METRICBEAT_CONF_PATH, "w+") as main_metricbeat_yaml:
        logger.debug("Using the following meatricbeat configuration: {}".format(conf))
        yaml.dump(conf, main_metricbeat_yaml)


def _get_additional_fields():
    try:
        additional_fields = os.environ["LOGZIO_ADDITIONAL_FIELDS"]
    except KeyError:
        return {}

    fields = {}
    filtered = dict(parse_entry(entry) for entry in additional_fields.split(";"))

    for key, value in filtered.items():
        if value[FIRST_CHAR] == "$":
            try:
                fields[key] = os.environ[value[FIRST_CHAR+1:]]
            except KeyError:
                continue
        else:
            fields[key] = value

    return fields


def parse_entry(entry):
    try:
        key, value = entry.split("=")
    except ValueError:
        raise ValueError("Failed to parse entry: {}".format(entry))

    if key == "" or value == "":
        raise ValueError("Failed to parse entry: {}".format(entry))
    return key, value


url = os.environ["LOGZIO_URL"]
logger = _create_logger()

_is_open()
_add_modules()
_add_shipping_data()

os.system("metricbeat -e")
