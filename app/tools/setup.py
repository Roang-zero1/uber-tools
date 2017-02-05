"""
Application setup helper

This module provides functions that are used to setup the application envoronment.
"""
import json
import logging
import logging.config
import os

logger = logging.getLogger(__name__)

def setup_logging(
    level=None,
    default_path='logging.json',
    default_level=logging.INFO,
    env_key='LOG_CFG'
):
  """Setup logging configuration

  Args:
    default_path: The dafault path used to load the logging configuration.
    default_level: The log level used if no configuration is found.
    env_key: The environment key to check for an alternative path.

  """
  path = default_path
  value = os.getenv(env_key, None)
  if value:
    path = value
  if os.path.exists(path):
    with open(path, 'rt') as settings_file:
      config = json.load(settings_file)
    if level:
      config['root']['level'] = level
    logging.config.dictConfig(config)
  else:
    logging.basicConfig(level=level or default_level)
  logging.getLogger("urllib3").setLevel(logging.WARNING)

def loadconfig(
    default_path='config.json',
    env_key='UBT_CFG'
):
  """Load and set up configuration

  Args:
    default_path: The dafault path used to load the app configuration.
    env_key: The environment key to check for an alternative path.

  Returns:
    dict: The configuration for the app

  """
  path = default_path
  value = os.getenv(env_key, None)
  if value:
    path = value
  if os.path.exists(path):
    try:
      with open(path, 'rt') as settings_file:
        config = json.load(settings_file)
    except (FileNotFoundError, ValueError) as ex:
      logger.error("Logging configuration could not be read:\n%s", ex)
      exit(1)
    config['general'] = config.get('general', {})
    config['domains'] = config.get('domains', {})
  return config
