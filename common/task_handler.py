#!/usr/bin/env python

# Run a standalone AL service

import json
import logging
import os
import time
import yaml
import tempfile
import shutil

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from assemblyline.common import log

from svc_client import Client

log.init_logging('assemblyline.task_handler', log_level=logging.DEBUG)
log = logging.getLogger('assemblyline.task_handler')

svc_api_host = os.environ['SERVICE_API_HOST']
# name = os.environ['SERVICE_PATH']

# svc_name = name.split(".")[-1].lower()

svc_client = Client(svc_api_host)

result_found = False


class MyHandler(FileSystemEventHandler):
    def __init__(self, observer):
        object.__init__(self)
        self.observer = observer

    def process(self, event):
        """
        event.event_type
            'modified' | 'created' | 'moved' | 'deleted'
        event.is_directory
            True | False
        event.src_path
            path/to/observed/file
        """
        global result_found

        # the file will be processed there
        log.info(event.src_path)
        log.info(event.event_type)
        self.observer.stop()
        log.info("stopped")
        result_found = True

    def on_modified(self, event):
        self.process(event)

    def on_created(self, event):
        # self.process(event)
        pass


def done_task(task, result, folder_path):
    try:
        svc_client.task.done_task(task=task,
                                  result=result)
    finally:
        if os.path.isdir(folder_path):
            shutil.rmtree(folder_path)


def get_classification(yml_classification=None):
    log.info('Getting classification definition...')

    if yml_classification is None:
        yml_classification = "/etc/assemblyline/classification.yml"

    # Get classification definition and save it
    classification = svc_client.help.get_classification_definition()
    with open(yml_classification, 'w') as fh:
        yaml.dump(classification, fh)


def get_systems_constants(json_constants=None):
    log.info('Getting system constants...')

    if json_constants is None:
        json_constants = "/etc/assemblyline/constants.json"

        # Get system constants and save it
        cosntants = svc_client.help.get_systems_constants()
        with open(json_constants, 'w') as fh:
            json.dump(cosntants, fh)


def get_task(service_config):
    task = svc_client.task.get_task(service_name=service_config['SERVICE_NAME'],
                                    service_version=service_config['SERVICE_VERSION'],
                                    service_tool_version=service_config['TOOL_VERSION'],
                                    file_required=service_config['SERVICE_FILE_REQUIRED'])
    return task


def get_service_config(yml_config=None):
    if yml_config is None:
        # service_path = os.environ['SERVICE_PATH']

        yml_config = "/etc/assemblyline/service_config.yml"

    # Load from the yaml config
    while True:
        log.info('Trying to load service config YAML...')
        if os.path.exists(yml_config):
            with open(yml_config) as yml_fh:
                service_config = yaml.safe_load(yml_fh.read())
            return service_config
        else:
            time.sleep(5)


def task_handler(service_config):
    task = get_task(service_config)
    my_observer = Observer()
    my_event_handler = MyHandler(my_observer)

    # Create an observer
    folder_path = os.path.join(tempfile.gettempdir(), task['service_name'].lower(), task['sid'])
    go_recursively = True

    my_observer.schedule(my_event_handler, folder_path, recursive=go_recursively)

    # Start the observer
    my_observer.start()

    while not result_found:
        log.debug(f'Waiting for result.json in: {folder_path}')
        time.sleep(1)

    result_json_path = os.path.join(folder_path, 'result.json')
    with open(result_json_path, 'r') as f:
        result = json.load(f)
    done_task(task, result, folder_path)


if __name__ == '__main__':
    get_classification()
    get_systems_constants()
    service = get_service_config()

    task_handler(service)