__author__ = 'NaDa'
# -*- coding: utf-8 -*-



class config:
    DB_URL = 'mysql://gncloud:gncloud@db/gncloud?charset=utf8'
    IMAGE_PATH = '/var/lib/gncloud/Web/static/assets/gn_images'
    RUN_STATUS = 'Running'
    REMOVE_STATUS = 'Removed'
    DELETING_STATUS = 'Deleting'
    STARTING_STATUS = 'Starting'
    ERROR_STATUS = 'Error'
    SUSPEND_STATUS = 'Suspend'
    NGINX_CONF_PATH = '/etc/nginx'
    AGENT_PORT = '8180'