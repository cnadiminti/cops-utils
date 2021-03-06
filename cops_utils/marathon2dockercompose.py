#!/usr/bin/python
#
# @authors   : Chandra Nadiminti, Ajay Balasa
#
# @create   : 08/08/2016
#
# @purpose  :
#
# @component:
#
# @comments :

######################################################################
# Package Imports
######################################################################
import json
import yaml
import requests
from requests.auth import HTTPBasicAuth
import argparse
import sys
import logging

######################################################################
# Procedures
######################################################################
compose = {'version': '2'}
logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)


def parse_app(app):
    content = {}
    name = app['id'].strip('/') + '.service.consul'
    command = []
    if app['cmd']:
        command.append(app['cmd'])
    if app['args']:
        command.extend(app['args'])
    ports = []
    if command:
        content['command'] = command
    if 'portMappings' in app['container']['docker']:
        for p in app['container']['docker']['portMappings']:
            ports.append("%s:%s" % (p['hostPort'], p['containerPort']))
    if ports:
        content['ports'] = ports
    content['image'] = app['container']['docker']['image']
    if app['env']:
        content['environment'] = app['env']
    for param in app['container']['docker']['parameters']:
        # Replace hyphens with underscore
        key = param['key'].replace('-', '_')
        # name is already taken from app['id']
        if key == 'name':
            continue
        # TODO
        if key == 'publish':
            continue
        if (key == 'expose' or
                key == 'cap_add' or
                key == 'cap_drop'):
            content[key] = [param['value']]
        else:
            content[key] = param['value']
    return {'name': name,
            'value': content}


def parse_apps(apps):
    services = {}
    for app in apps:
        print app['id']
        # json.dump(app, sys.stdout, indent=2)
        if 'container' not in app.keys():
            print 'NO container TAG in ' + app['id']
            continue
        if (not app['container'] or
                'type' not in app['container'].keys()):
            print 'NO container or container-type TAG in ' + app['id']
            continue
        if (app['container']['type']).lower() != 'docker':
            print app['id'] + '====' + app['container']['type']
            continue
        docker_app = parse_app(app)
        services[docker_app['name']] = docker_app['value']

    compose['services'] = services
    out = open('docker-compose.yml', 'w')
    yaml.safe_dump(compose,
                   stream=out,
                   indent=4,
                   # explicit_start=True,
                   default_flow_style=False
                   )


def main():
    base_url, user, pswd = arguments_parse()
    try:
        resp = requests.get(base_url, timeout=5, verify=False,
                            auth=HTTPBasicAuth(user, pswd))
        resp.raise_for_status()
    except requests.exceptions.Timeout:
        logging.error("Request timed out after specified timeout value.")
        sys.exit(1)
    except requests.exceptions.InvalidURL:
        logging.error("Invalid URL")
        sys.exit(1)
    except requests.exceptions.ConnectionError:
        logging.error("Connection errors")
        sys.exit(1)
    except requests.exceptions.SSLError:
        logging.error("SSL errors")
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        logging.error(e)
        sys.exit(1)

    parse_apps(json.loads(resp.content)['apps'])


def arguments_parse():
    parser = argparse.ArgumentParser(description='Utility to create a \
            docker-compose file with the containers details from Marathon')
    parser.add_argument('--url', help='Marathon base API URL \
                        Ex: https://mantl-cisco.com//marathon/v2/apps',
                        required=True)
    parser.add_argument('-u', '--user', help='Marathon login user name',
                        required=True)
    parser.add_argument('-p', '--pswd', help='Marathon login password',
                        required=True)
    args = parser.parse_args()
    base_url = args.url
    user = args.user
    pswd = args.pswd
    return base_url, user, pswd

if __name__ == '__main__':
    main()
