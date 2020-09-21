import logging
import os
import socket
from ruamel.yaml import YAML

SOCKET_TIMEOUT = 3
FIRST_CHAR = 0
METRICBEAT_CONF_PATH = "/etc/metricbeat/metricbeat.yml"
DEFAULT_LOG_LEVEL = "INFO"
LOG_LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
SUPPORTED_MODULES = ["docker", "system", "aws"]
SINGLE_MODULE_INDEX = 0
LOGZIO_LISTENER_ADDRESS = "listener.logz.io:5015"


url = LOGZIO_LISTENER_ADDRESS


def get_listener_url(region):
    return LOGZIO_LISTENER_ADDRESS.replace("listener.", "listener{}.".format(get_region_code(region)))


def get_region_code(region):
    if region != "us" and region != "":
        return "-{}".format(region)
    return ""


def _set_url():
    global url
    region = ""
    is_region = False
    if 'LOGZIO_REGION' in os.environ:
        region = os.environ['LOGZIO_REGION']
        is_region = True
        if 'LOGZIO_URL' in os.environ:
            logger.warning("Both LOGZIO_REGION and LOGZIO_URL were entered! Using LOGZIO_REGION variable.")
    else:
        if 'LOGZIO_URL' in os.environ and os.environ['LOGZIO_URL'] != "":
            url = "{}:5015".format(os.environ['LOGZIO_URL'])
            logger.warning("Please note that LOGZIO_URL is deprecated!")
        else:
            is_region = True

    if is_region:
        url = get_listener_url(region)


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
    try:
        modules = [m.strip() for m in os.environ["LOGZIO_MODULES"].split(",")]
    except KeyError:
        logger.error("Required at least one module")
        raise
    _enable_modules(modules)
    if os.environ["CLOUD_METADATA"] == "true":
        _enable_cloud_metadata(modules)
    _add_data_by_module(modules)


def _enable_modules(modules):
    yaml = YAML()
    yaml.preserve_quotes = True
    for module in modules:
        if module not in SUPPORTED_MODULES:
            logger.error("Unsupported module: {}".format(module))
            raise RuntimeError
        with open("modules/{}.yml".format(module), "r+") as module_file:
            module_yaml = yaml.load(module_file)
            module_yaml[SINGLE_MODULE_INDEX]["enabled"] = True
            _dump_and_close_file(module_yaml, module_file)


def _enable_cloud_metadata(modules):
    yaml = YAML()
    yaml.preserve_quotes = True
    for module in modules:
        if module not in SUPPORTED_MODULES:
            logger.error("Unsupported module: {}".format(module))
            raise RuntimeError
        with open("modules/{}.yml".format(module), "r+") as module_file:
            module_yaml = yaml.load(module_file)
            module_yaml[SINGLE_MODULE_INDEX]["processors"] = [dict(add_cloud_metadata=dict(timeout="3s"))]
            _dump_and_close_file(module_yaml, module_file)


def _add_shipping_data():
    token = os.environ["LOGZIO_TOKEN"]

    yaml = YAML()
    yaml.preserve_quotes = True
    with open("metricbeat.yml") as default_metricbeat_yaml:
        conf = yaml.load(default_metricbeat_yaml)

    conf["output.logstash"]["hosts"] = url
    conf["fields"]["token"] = token
    conf["fields"]["type"] = os.getenv("LOGZIO_TYPE", "docker-collector-metrics")

    additional_field = _get_additional_fields()

    hostname = _get_host_name()
    if hostname is not '':
        conf["name"] = hostname
    if len(additional_field) > 0:
        conf["fields"]["dim"] = {}
    for key in additional_field:
        conf["fields"]["dim"][key] = additional_field[key]

    with open(METRICBEAT_CONF_PATH, "w+") as main_metricbeat_yaml:
        logger.debug("Using the following meatricbeat configuration: {}".format(conf))
        yaml.dump(conf, main_metricbeat_yaml)


def _get_additional_fields():
    try:
        additional_fields = os.environ["LOGZIO_EXTRA_DIMENSIONS"]
    except KeyError:
        return {}

    fields = {}
    filtered = dict(parse_entry(entry) for entry in additional_fields.split(";"))

    for key, value in filtered.items():
        if value[FIRST_CHAR] == "$":
            try:
                fields[key] = os.environ[value[FIRST_CHAR+1:]]
            except KeyError:
                fields[key] = "Error parsing environment variable"
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


def _add_data_by_module(modules):
    for module in modules:
        module_name = module.lower()
        if module_name == "aws":
            _add_aws_shipping_data()


def _add_aws_shipping_data():
    aws_namespaces = _get_aws_namespaces()
    if len(aws_namespaces) > 0:
        try:
            access_key_id = os.environ["AWS_ACCESS_KEY"]
            access_key = os.environ["AWS_SECRET_KEY"]
            aws_region = os.environ["AWS_REGION"]
            yaml = YAML()
            yaml.preserve_quotes = True

            with open("modules/aws.yml", "r+") as module_file:
                module_yaml = yaml.load(module_file)
                module_yaml[SINGLE_MODULE_INDEX]["metrics"] = []
                for aws_namespace in aws_namespaces:
                    module_yaml[SINGLE_MODULE_INDEX]["metrics"].append({"namespace": aws_namespace})
                    tags_val = _get_tags_value(aws_namespace)
                    if tags_val != "":
                        module_yaml[SINGLE_MODULE_INDEX]["metrics"][-1]["tags.resource_type_filter"] = tags_val
                module_yaml[SINGLE_MODULE_INDEX]["access_key_id"] = access_key_id
                module_yaml[SINGLE_MODULE_INDEX]["secret_access_key"] = access_key
                module_yaml[SINGLE_MODULE_INDEX]["default_region"] = aws_region
                _dump_and_close_file(module_yaml, module_file)
        except KeyError:
            logger.error("Could not find aws access key or secret key or region: {}".format(KeyError))


def _get_tags_value(aws_namespace):
    aws_namespace_lower = aws_namespace.lower()
    if "aws/" in aws_namespace_lower:
        service_name = aws_namespace_lower.split("/")[1]
        if service_name == "ebs":
            return "ec2:snapshot"
        elif service_name == "elb" or service_name == "applicationelb" or service_name == "networkelb":
            return "elasticloadbalancing"
        elif service_name == "amazonmq":
            return "mq"
        elif service_name == "efs":
            return "elasticfilesystem"
        else:
            return service_name
    else:
        return aws_namespace_lower


def _get_aws_namespaces():
    aws_namespaces = []

    try:
        aws_namespaces = os.environ["AWS_NAMESPACES"].split(',')
    except KeyError:
        logger.error("Could not find aws services: {}".format(KeyError))
    return aws_namespaces


def _dump_and_close_file(module_yaml, module_file):
    yaml = YAML()
    yaml.preserve_quotes = True
    module_file.seek(0)
    yaml.dump(module_yaml, module_file)
    module_file.truncate()
    module_file.close()


def _get_debug_mode():
    debug = os.getenv("DEBUG", "false")
    if debug == "true":
        return '-d "*"'
    else:
        return ""


def _get_host_name():
    return os.getenv("HOSTNAME", '')


logger = _create_logger()
_set_url()
_is_open()
_add_modules()
_add_shipping_data()
debug_mode = _get_debug_mode()

os.system("metricbeat -e {}".format(debug_mode))
