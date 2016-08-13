from compose.cli.command import project_from_options
from compose.cli.main import TopLevelCommand
from compose.config import errors
from docopt import docopt
from inspect import getdoc
import json
import logging
import sys


logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)


def isValidComposeFile(file_name=None):
    command = TopLevelCommand(None)
    config_help = getdoc(TopLevelCommand)
    if file_name:
        config_options = docopt(config_help, ['-f', file_name], None)
    else:
        config_options = docopt(config_help, None, None)
    command_help = getdoc(command.config)
    command_options = docopt(
        command_help, config_options['ARGS'], options_first=True)
    command_options['--quiet'] = True

    try:
        command.config(config_options, command_options)
    except errors.ComposeFileNotFound:
        logging.warning('Compose File Not Found')
        return False
    except errors.ConfigurationError:
        logging.exception("Something awful happened!")
        return False
    return True


def _create_container_config(client, image, command=None,
                             hostname=None, user=None,
                             detach=False, stdin_open=False, tty=False,
                             mem_limit=None, ports=None, environment=None,
                             dns=None, volumes=None, volumes_from=None,
                             network_disabled=False, name=None,
                             entrypoint=None,
                             cpu_shares=None, working_dir=None,
                             domainname=None,
                             memswap_limit=None, cpuset=None,
                             host_config=None,
                             mac_address=None, labels=None,
                             volume_driver=None,
                             stop_signal=None, networking_config=None):
    return client.create_container_config(image, command, hostname, user,
                                          detach, stdin_open,
                                          tty, mem_limit, ports, environment,
                                          dns, volumes, volumes_from,
                                          network_disabled, entrypoint,
                                          cpu_shares, working_dir, domainname,
                                          memswap_limit, cpuset, host_config,
                                          mac_address, labels, volume_driver,
                                          stop_signal, networking_config,
                                          )


def get_run_payload(config, name):
    logging.debug(json.dumps(config, indent=2))
    command = 'docker run \\'
    command += '\n  --name ' + name
    image = ''
    cmd = ''
    for opt in config:
        val = config[opt]
        opt = opt.lower()
        if opt == 'image':
            image = val
            continue
        elif opt == 'cmd' and val:
            for arg in val:
                cmd += ' \\\n      ' + arg
            continue
        elif opt == 'env' and val:
            command += ' \\'
            command += '\n'
            command += '  --%s=%s' % (opt, json.dumps(val))
            continue
        elif opt == 'labels':
            continue  # TODO: Ignored for now
        elif opt == 'networkingconfig':
            continue  # TODO: Ignored for now
        elif opt == 'exposedports':
            continue  # TODO: Ignored for now
        elif opt == 'hostconfig':
            for sub_opt in val:
                if sub_opt == 'NetworkMode' and val[sub_opt]:
                    command += ' \\'
                    command += '\n'
                    command += '  --net=%s ' % val[sub_opt]
                elif sub_opt == 'Links' and val[sub_opt]:
                    command += ' \\'
                    command += '\n'
                    command += '  --link=%s ' % val[sub_opt]
                elif sub_opt == 'PortBindings' and val[sub_opt]:
                    for port in val[sub_opt]:
                        command += ' \\'
                        command += '\n'
                        command += '  --publish=%s:%s' % (
                            port.split('/')[0],
                            val[sub_opt][port][0]['HostPort']
                        )
                else:
                    # TODO
                    continue
            continue
        elif val:
            msg = '%s Unhadled option %s=%s' % (name, opt, val)
            logging.warn(msg)
    if image:
        command += ' \\\n  ' + image
    if cmd:
        command += cmd
    return command


def get_run_output(file_name=None):
    config_help = getdoc(TopLevelCommand)
    config_options = docopt(config_help, None, None)
    if file_name:
        config_options = docopt(config_help, ['-f', file_name], None)
    else:
        config_options = docopt(config_help, None, None)
    project = project_from_options('.', config_options)

    services = project.get_services(include_deps=True)
    commands = []
    for svc in services:
        # print 'link_names==> %s' % svc.get_link_names()
        # print 'volumes_from_names==> %s' % svc.get_volumes_from_names()
        # print 'linked_service_names==> %s' % svc.get_linked_service_names()
        # print 'get_dependency_names==> %s' % svc.get_dependency_names()
        container_options = svc._get_container_create_options({}, 1)
        name = container_options.pop('name', None)
        logging.debug('==> Service Name=' + name)
        config = _create_container_config(project.client, **container_options)
        commands.append(get_run_payload(config, name))
        for command in commands:
            print ('Hello')
            print (command)


def main():
    test_dc_file = 'docker-compose-test.yml'
    if isValidComposeFile(test_dc_file):
        logging.debug("Valid Compose-file")
        get_run_output(test_dc_file)
    else:
        logging.warning("In-Valid Compose-file: " + test_dc_file)
        sys.exit(1)


if __name__ == '__main__':
    main()
