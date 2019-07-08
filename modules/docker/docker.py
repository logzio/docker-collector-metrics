import logging
import os

from ruamel.yaml import YAML

DOCKER_YML_PATH = "{}/docker.yml".format(os.path.dirname(os.path.realpath(__file__)))
MODULE_NAME = "docker"

logger = logging.getLogger(__name__)


def _exclude_containers(conf):
    exclude_list = [container.strip() for container in os.environ["dockerSkipContainerName"].split(",")]

    drop_event = {"drop_event": {"when": {"or": []}}}
    conf[0]["processors"] = []
    conf[0]["processors"].append(drop_event)

    for container_name in exclude_list:
        contains = {"contains": {"docker.container.name": container_name}}
        conf[0]["processors"][0]["drop_event"]["when"]["or"].append(contains)
        logger.debug("Adding {0} to the exclude containers list".format(container_name))


def _include_containers(conf):
    include_list = [container.strip() for container in os.environ["dockerMatchContainerName"].split(",")]

    drop_event = {"drop_event": {"when": {"and": []}}}
    conf[0]["processors"] = []
    conf[0]["processors"].append(drop_event)

    for container_name in include_list:
        contains = {"not": {"contains": {"docker.container.name": container_name}}}
        conf[0]["processors"][0]["drop_event"]["when"]["and"].append(contains)
        logger.debug("Adding {0} to the include containers list".format(container_name))


def _filter_containers(conf):
    if "dockerMatchContainerName" in os.environ and "dockerSkipContainerName" in os.environ:
        logging.error("Can have only one of dockerSkipContainerName or dockerMatchContainerName")
        raise KeyError
    elif "dockerMatchContainerName" in os.environ:
        _include_containers(conf)
    elif "dockerSkipContainerName" in os.environ:
        _exclude_containers(conf)


def _set_period(conf):
    try:
        p = os.environ["dockerPeriod"]
    except KeyError:
        return

    conf[0]["period"] = p
    logger.debug("Set docker period to {0}".format(p))


def _set_certificate(conf):
    try:
        ssl = {
            "certificate_authority": os.environ["dockerCertificateAuthority"],
            "certificate": os.environ["dockerCertificate"],
            "key": os.environ["dockerKey"],
        }
    except KeyError:
        return

    conf[0]["ssl"] = ssl
    logger.debug("Set ssl parameters: {0}".format(ssl))


def _set_cpu_per_core(conf):
    try:
        cpu = os.environ["dockerCPUPerCore"]
    except KeyError:
        return

    conf[0]["cpu.cores"] = cpu
    logger.debug("Set cpu cores flag to {0}".format(cpu))


def _set_host(conf):
    conf[0]["hosts"].append("unix:///var/run/docker.sock")


def name():
    return MODULE_NAME


def setup():
    yaml = YAML()
    with open(DOCKER_YML_PATH) as docker_yml:
        conf = yaml.load(docker_yml)

    _set_period(conf)
    _set_certificate(conf)
    _set_cpu_per_core(conf)
    _set_host(conf)
    _filter_containers(conf)
    logger.debug("docker module setup: {}".format(conf))

    return conf
