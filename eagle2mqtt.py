import os
import schedule
import time
import eagle200_reader as eagle

from datetime import datetime
from paho.mqtt.client import Client as Mqtt
from paho.mqtt.publish import multiple as publish_multiple

from socket import gaierror
from requests.exceptions import ReadTimeout


def get_env_config():
  return {
    'eagle': {
        'ip': os.environ['EAGLE_IP'],
        'cloudid': os.environ['EAGLE_CLOUDID'],
        'installcode': os.environ['EAGLE_INSTALL_CODE']
    },
    'mqtt': {
        'host': os.environ['MQTT_HOST'],
        'user': os.environ['MQTT_USER'],
        'pass': os.environ['MQTT_PASS'],
        'root': os.environ['MQTT_ROOT']
    },
    'refresh': os.environ['REFRESH'] #seconds
  }


def job():
  conf = get_env_config()

  try:
    device = eagle.EagleReader(
      conf['eagle']['ip'],
      conf['eagle']['cloudid'],
      conf['eagle']['installcode']
    )
  except ReadTimeout:
    device = None

  if device == None:
    print(f'requests.exceptions.ReadTimeout for Eagle200 at {conf["eagle"]["ip"]}')
    return
    
  instant_demand = device.instantanous_demand()
  total_delivered = device.summation_delivered()

  # doesn't give any good error value... Just check for any Nones

  if conf['mqtt']['root'] == None or conf['mqtt']['root'] == '':
    mqttRoot = ''
  else:
    mqttRoot = conf['mqtt']['root'].rstrip('/') + '/'

  if (instant_demand != None and total_delivered != None):
    try:
      publish_multiple(
        [
            {'topic': f'{mqttRoot}instant_demand', 'payload': instant_demand},
            {'topic': f'{mqttRoot}total_delivered', 'payload': total_delivered}
        ],
        auth={'username': conf['mqtt']['user'], 'password': conf['mqtt']['pass']},
        hostname=conf['mqtt']['host']
      )
    except gaierror:
      print(f"socket.gaierror in publish_multiple on: {conf['mqtt']['host']}")


if __name__ == '__main__':
  job()
  schedule.every(int(get_env_config()['refresh'])).seconds.do(job)
  print(schedule.jobs)

  while True:
    schedule.run_pending()
    time.sleep(1)
