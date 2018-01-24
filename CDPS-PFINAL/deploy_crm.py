#!/usr/bin/python

import os
import sys
import argparse
import logging
from subprocess import call

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('pfinalp2')

execute_commands = True


def install_crm(node):
    """

    :return:
    """
    result = 0
    global execute_commands

    # Install nodejs and npm
    #
    cmd_list = ['apt-get update',
                'apt-get -y install curl',
                'curl -sL https://deb.nodesource.com/setup_8.x | sudo bash -',
                'sudo apt-get -y install nodejs']
    for cmd in cmd_list:
        cmd_line = 'sudo lxc-attach --clear-env -n {0} -- bash -c \"{1}\"'.format(node, cmd)
        if execute_commands:
            result = call(cmd_line, shell=True)
        logger.debug('%s -> %d' % (cmd_line, result))
        assert result == 0, 'Error (%d) executing command: %s' % (result, cmd_line)

    # Install CRM app
    #
    cmd_list = ['cd /usr/src; git clone https://github.com/CORE-UPM/CRM_2017.git', # Install app
                'cd /usr/src/CRM_2017; npm install',
                'cd /usr/src/CRM_2017; npm install forever']
    for cmd in cmd_list:
        cmd_line = 'sudo lxc-attach --clear-env -n {0} -- bash -c \"{1}\"'.format(node, cmd)
        if execute_commands:
            result = call(cmd_line, shell=True)
        logger.debug('%s -> %d' % (cmd_line, result))
        assert result == 0, 'Error (%d) executing command: %s' % (result, cmd_line)


def config_nas(node):
    """

    :return:
    """
    result = 0
    global execute_commands

    cmd_list = ['mkdir -p /mnt/nas',
                'mount -t glusterfs 10.1.4.21:/nas /mnt/nas',
                'cd /usr/src/CRM_2017/public; ln -s /mnt/nas ./upload']
    for cmd in cmd_list:
        cmd_line = 'sudo lxc-attach --clear-env -n {0} -- bash -c \"{1}\"'.format(node, cmd)
        if execute_commands:
            result = call(cmd_line, shell=True)
        logger.debug('%s -> %d' % (cmd_line, result))
        assert result == 0, 'Error (%d) executing command: %s' % (result, cmd_line)


def migrate_and_seed(node):
    """

    CMD npm run-script migrate_local ; npm run-script seed_local

    :return:
    """
    result = 0
    global execute_commands

    environment = "DATABASE_URL='postgres://postgres:pass123@10.1.4.31:5432/postgres'"
    cmd = 'cd /usr/src/CRM_2017; npm run-script migrate_local ; npm run-script seed_local'

    cmd_line = 'sudo lxc-attach --clear-env -n {0} -- bash -c \"export {1}; {2}\"'.format(node, environment, cmd)
    if execute_commands:
        result = call(cmd_line, shell=True)
    logger.debug('%s -> %d' % (cmd_line, result))
    assert result == 0, 'Error (%d) executing command: %s' % (result, cmd_line)


def start_crm_app(node):
    """

    Environment variables needed to configure CRM app:
    DATABASE_URL=

    Run CRM server in background:
    ./node_modules/forever/bin/forever start ./bin/www

    :return:
    """
    result = 0
    global execute_commands

    environment = "export DATABASE_URL='postgres://postgres:pass123@10.1.4.31:5432/postgres'; export CRM_TITLE='CRM (located at {0})'".format(node)
    cmd = 'cd /usr/src/CRM_2017; ./node_modules/forever/bin/forever start ./bin/www'

    cmd_line = 'sudo lxc-attach --clear-env -n {0} -- bash -c \"{1};{2}\"'.format(node, environment, cmd)
    if execute_commands:
        result = call(cmd_line, shell=True)
    logger.debug('%s -> %d' % (cmd_line, result))
    assert result == 0, 'Error (%d) executing command: %s' % (result, cmd_line)


def main():

    parser = argparse.ArgumentParser(description='Script to deploy a scalable CRM system')

    commands_allowed = ['create', 'deploy', 'shutdown', 'start', 'start_app', 'destroy']
    parser.add_argument('commands', metavar='command', nargs='+', choices=commands_allowed,
                        help='command to execute (' + ', '.join(commands_allowed) + ')')
    parser.add_argument('--nodes', dest='nodes', default='all', help='nodes to execute "command"')
    parser.add_argument('--print', dest='only_print', action='store_true',
                        help='Do no execute commands, only printed out on the screen')

    args = parser.parse_args()
    print('Scripts arguments: %s' % args)

    if not os.geteuid() == 0:
        sys.exit("\nOnly root can run this script\n")

    global execute_commands
    if args.only_print:
        execute_commands = False

    result = 0

    for command in args.commands:
        if command == 'create':
            # Create and start the scenario
            #
            cmd = 'sudo vnx -f pfinal.xml --create'
            if execute_commands:
                result = call(cmd, shell=True)
            logger.debug('%s -> %d' % (cmd, result))
            assert result == 0, 'Error (%d) executing command: %s' % (result, cmd)

        elif command == 'deploy':
            # Deploy the nodes of the scenario
            #
            nodes = args.nodes.split(',')
            logger.debug('Nodes %s' % nodes)

            if 'all' in nodes or 'nas' in nodes:
                logger.info('Deploy nas...')
                cmd = './scripts/config_nas.sh'
                if execute_commands:
                    result = call(cmd, shell=True)
                logger.debug('%s -> %d' % (cmd, result))
                assert result == 0, 'Error (%d) executing command: %s' % (result, cmd)

            if 'all' in nodes or 'db' in nodes:
                logger.info('Deploy db...')
                cmd = './scripts/postgresql_deploy.sh'
                if execute_commands:
                    result = call(cmd, shell=True)
                logger.debug('%s -> %d' % (cmd, result))
                assert result == 0, 'Error (%d) executing command: %s' % (result, cmd)

            if 'all' in nodes or 's1' in nodes:
                logger.info('Deploy s1...')

                node = 's1'

                install_crm(node)
                config_nas(node)

                migrate_and_seed(node)  # only executed in s1

                start_crm_app(node)
            if 'all' in nodes or 's2' in nodes:
                logger.info('Deploy s2...')

                node = 's2'

                install_crm(node)
                config_nas(node)

                start_crm_app(node)

            if 'all' in nodes or 's3' in nodes:
                logger.info('Deploy s3...')

                node = 's3'

                install_crm(node)
                config_nas(node)
                start_crm_app(node)

            if 'all' in nodes or 'lb' in nodes:
                logger.info('Deploy lb...')

                cmd = './scripts/start_load_balancer.sh'
                if execute_commands:
                    result = call(cmd, shell=True)
                logger.debug('%s -> %d' % (cmd, result))
                assert result == 0, 'Error (%d) executing command: %s' % (result, cmd)

            if 'all' in nodes or 'fw' in nodes:
                logger.info('Deploy fw...')

                cmd = './scripts/start_firewall.sh'
                if execute_commands:
                    result = call(cmd, shell=True)
                logger.debug('%s -> %d' % (cmd, result))
                assert result == 0, 'Error (%d) executing command: %s' % (result, cmd)

        elif command == 'start_app':
            # Start app in the nodes of the scenario
            #
            nodes = args.nodes.split(',')
            logger.debug('Nodes %s' % nodes)

            if 'all' in nodes or 's1' in nodes:
                logger.info('Start CRM app at s1...')

                node = 's1'
                start_crm_app(node)

            if 'all' in nodes or 's2' in nodes:
                logger.info('Start CRM app at s2...')

                node = 's2'
                start_crm_app(node)

            if 'all' in nodes or 's3' in nodes:
                logger.info('Start CRM app at s3...')

                node = 's3'

                start_crm_app(node)

        elif command == 'shutdown':
            # Stop scenario and save changes
            #
            cmd = 'sudo vnx -f pfinal.xml --shutdown'
            if execute_commands:
                result = call(cmd, shell=True)
            logger.debug('%s -> %d' % (cmd, result))
            assert result == 0, 'Error (%d) executing command: %s' % (result, cmd)

        elif command == 'start':
            # Start scenario from a previous shutdown
            #
            cmd = 'sudo vnx -f pfinal.xml --start'
            if execute_commands:
                result = call(cmd, shell=True)
            logger.debug('%s -> %d' % (cmd, result))
            assert result == 0, 'Error (%d) executing command: %s' % (result, cmd)

        elif command == 'destroy':
            # Destroy scenario
            #
            cmd = 'sudo vnx -f pfinal.xml --destroy'
            if execute_commands:
                result = call(cmd, shell=True)
            logger.debug('%s -> %d' % (cmd, result))
            assert result == 0, 'Error (%d) executing command: %s' % (result, cmd)


if __name__ == "__main__":
    main()
