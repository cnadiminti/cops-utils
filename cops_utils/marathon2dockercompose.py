#!/usr/bin/python
######################################################################
#
# (C) Copyright  Chandra, Nadiminti 2015-16
#
######################################################################
#
# @filename : marathon2dockercompose.py
#
# @author   : Chandra Mohan Babu Nadiminti
#
# @create   : 08/08/2016
#
# @purpose  :
#
# @component:
#
# @comments :
#
######################################################################

######################################################################
# Package Imports
######################################################################
import subprocess
import json
import yaml
import requests
from requests.auth import HTTPBasicAuth
import sys
import argparse

######################################################################
# Procedures
######################################################################
compose = {'version': '2'}


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

def help_doc():
    print  '\n', \
           'Utility to create a docker-compose file with the containers details from Marathon \n', \
           '\n', \
           'Usage: python marathon2dockercompose.py (-b|--baseurl url) (-u|--user user) ', \
	   '(-p|--pswd password) or (-h|--help) \n', \
           '\n', \
           '-b or --baseurl    Marathon Base URL \n', \
           '-u or --user    Marathon Login user name \n', \
           '-p or --pswd    Marahon Login password \n', \
           '-h or --help    Print this and exit'

def main():
    print 'Welcome!!!'
    if ("-h" or "--help") in sys.argv:
        help_doc()
        sys.exit()
    elif ("-b" or "--baseurl" or "-u" or "--user" or "-p" or "--pswd") in sys.argv:
        base_url, user, pswd = arguments_parse()
    else:
        print '\n', \
            'Enter a valid argument tag or use "-h" for Help \n'
        sys.exit()
    resp = requests.get(base_url, verify=False,
                        auth=HTTPBasicAuth(user, pswd))
    parse_apps(json.loads(resp.content)['apps'])

def arguments_parse():
    parser = argparse.ArgumentParser()
    parser.add_argument('-b','--baseurl', help='Marathon API URL')
    parser.add_argument('-u','--user', help='Marathon user name')
    parser.add_argument('-p','--pswd', help='Marathon login password')
    args = parser.parse_args()
    base_url=args.baseurl
    user=args.user
    pswd=args.pswd
    return base_url, user, pswd

if __name__ == '__main__':
    main()
