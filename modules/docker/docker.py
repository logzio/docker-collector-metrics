import logging
import os

from ruamel.yaml import YAML

DOCKER_YML_PATH = "{}/docker.yml".format(os.path.dirname(os.path.realpath(__file__)))
MODULE_NAME = "docker"

logger = logging.getLogger(__name__)


def _exclude_containers(conf):
    exclude_list = [container.strip() for container in os.environ["DOCKER_SKIP_CONTAINER_NAME"].split(",")]

    drop_event = {"drop_event": {"when": {"or": []}}}
    conf["processors"] = []
    conf["processors"].append(drop_event)

    for container_name in exclude_list:
        contains = {"contains": {"docker.container.name": container_name}}
        conf["processors"][0]["drop_event"]["when"]["or"].append(contains)
        logger.debug("Adding {0} to the exclude containers list".format(container_name))


def _include_containers(conf):
    include_list = [container.strip() for container in os.environ["DOCKER_MATCH_CONTAINER_NAME"].split(",")]

    drop_event = {"drop_event": {"when": {"and": []}}}
    conf["processors"] = []
    conf["processors"].append(drop_event)

    for container_name in include_list:
        contains = {"not": {"contains": {"docker.container.name": container_name}}}
        conf["processors"][0]["drop_event"]["when"]["and"].append(contains)
        logger.debug("Adding {0} to the include containers list".format(container_name))


def _filter_containers(conf):
    if "DOCKER_MATCH_CONTAINER_NAME" in os.environ and "DOCKER_SKIP_CONTAINER_NAME" in os.environ:
        logging.error("Can have only one of DOCKER_SKIP_CONTAINER_NAME or DOCKER_MATCH_CONTAINER_NAME")
        raise KeyError
    elif "DOCKER_MATCH_CONTAINER_NAME" in os.environ:
        _include_containers(conf)
    elif "DOCKER_SKIP_CONTAINER_NAME" in os.environ:
        _exclude_containers(conf)


def _set_period(conf):
    try:
        period = os.environ["DOCKER_PERIOD"]
    except KeyError:
        return

    conf["period"] = period
    logger.debug("Set docker period to {0}".format(period))


def _set_certificate(conf):
    try:
        ssl_conf = {
            "certificate_authority": os.environ["DOCKER_CERTIFICATE_AUTHORITY"],
            "certificate": os.environ["DOCKER_CERTIFICATE"],
            "key": os.environ["DOCKER_KEY"],
        }
    except KeyError:
        return

    conf["ssl"] = ssl_conf
    logger.debug("Set ssl parameters: {0}".format(ssl_conf))


def _set_cpu_per_core(conf):
    try:
        enable_cpu_per_core = os.environ["DOCKER_CPU_PER_CORE"]
    except KeyError:
        return

    conf["cpu.cores"] = enable_cpu_per_core
    logger.debug("Set cpu cores flag to {0}".format(enable_cpu_per_core))


def _set_host(conf):
    conf["hosts"].append("unix:///var/run/docker.sock")


def name():
    return MODULE_NAME


def setup():
    yaml = YAML()
    with open(DOCKER_YML_PATH) as docker_yml:
        conf = yaml.load(docker_yml)

    _set_period(conf[0])
    _set_certificate(conf[0])
    _set_cpu_per_core(conf[0])
    _set_host(conf[0])
    _filter_containers(conf[0])
    logger.debug("docker module setup: {}".format(conf))

    return conf
