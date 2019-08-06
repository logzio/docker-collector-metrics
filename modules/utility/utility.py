import os
import logging

logger = logging.getLogger(__name__)


def set_key_from_env(conf, key, env_name, default=None):
    if default is not None:
        value = os.getenv(env_name, default)
    else:
        try:
            value = os.environ[env_name]
        except KeyError:
            return
    conf[key] = value
    logger.debug("Set {0} from os.environ[{1}] with {2}".format(key, env_name, value))


def set_mapping_from_env(conf, key, mapping):
    # map should be {
    #                   key: env_name,
    #                   key2: env_name2
    #               }
    conf_map = {}
    for k, env_name in mapping.items():
        try:
            value = os.environ[env_name]
            conf_map[k] = value
            logger.debug("Set {0} from os.environ[{1}] with {2}".format(k, env_name, value))
        except KeyError:
            return

    conf[key] = conf_map
