import os
from ..utility.utility import set_key_from_env, set_mapping_from_env
from ruamel.yaml import YAML
import logging

logger = logging.getLogger(__name__)
MODULE_NAME = "system"
SYSTEM_YML_PATH = "{}/system.yml".format(os.path.dirname(os.path.realpath(__file__)))


def _set_period(conf):
    set_key_from_env(conf, "period", "SYSTEM_PERIOD")


def _set_host(conf):
    set_key_from_env(conf, "system.hostName", "HOSTNAME")


def name():
    return MODULE_NAME


def setup():
    yaml = YAML()
    with open(SYSTEM_YML_PATH) as system_yml:
        conf = yaml.load(system_yml)

    _set_period(conf[0])
    _set_host(conf[0])
    logger.debug("system module setup: {}".format(conf))
    return conf
