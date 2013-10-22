import os
try:
    from configparser import RawConfigParser as INIParser
except ImportError:
    from ConfigParser import RawConfigParser as INIParser

__all__ = ['get_config']


def get_config(config_file):
    if not os.path.isabs(config_file):
        config_file = os.path.abspath(config_file)
    config = INIParser()
    with open(config_file) as f:
        config.readfp(f)

    def _parse_value(v):
        if v.lower() == 'true':
            return True
        if v.lower() == 'false':
            return False
        return v

    return {k: _parse_value(v) for k, v in config.items('app:main')}

