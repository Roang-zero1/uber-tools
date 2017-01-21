import json
import logging
import os

logger = logging.getLogger(__name__)

def loadconfig(
    default_path='config.json',
    env_key='UBT_CFG'
):
  """Load and set up configuration

  """
  path = default_path
  value = os.getenv(env_key, None)
  if value:
      path = value
  if os.path.exists(path):
    try:
      with open(path, 'rt') as f:
          config = json.load(f)
    except (FileNotFoundError, ValueError) as e:
      logger.error("Logging configuration could not be read:\n{}".format(e))
      exit(1)
    config['general'] = config.get('general',{})
    config['domains'] = config.get('domains',{})
  return config
