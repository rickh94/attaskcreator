#!/usr/bin/env python3
import argparse
import configparser
import os
from subprocess import run
from shutil import copy2
from sys import exit

here = os.getcwd()
config_path = '/etc/attaskcreator/'

def make_config_file():
    config = configparser.ConfigParser()
    config['Airtable']['Database ID'] = input("Enter Airtable database ID: ")
    config['Airtable']['api key'] = input("Enter Airtable API key: ")
    config['Email']['User'] = input("Enter email user: ")
    config['Email']['Password'] = input("Enter email password: ")
    config['Email']['Imap URL'] = input("Enter imap server url: ")
    config['Email']['Smtp URL'] = input("Enter smtp server url: ")
    config['Email']['Error Email'] = input("Enter email for error messages: ")
    config['Tasks Table']['Name'] = input(
    "Enter the name of the tasks table: "
    )
    config['Tasks Table']['link field'] = input(
            "Enter field in tasks table that links to a people table: "
            )
    config['Tasks Table']['text field'] = input(
            "Enter field for insertion of parsed text (in tasks table): "
            )
    config['Tasks Table']['notes field'] = input(
            "Enter field for insertion of full email body (blank for none): "
            )
    config['People Table']['name'] = input(
            "Enter the name of the people table: "
            )
    config['People Table']['email field'] = input(
            "Enter the name of the email field in the people table: "
            )
    config['Parse']['trigger phrase'] = input(
            "Enter the phrase that will trigger text insertion: "
            )
    config['Parse']['termination character'] = input(
            "Enter the character that will signal the end of text insertion: "
            )

    with open(os.path.join(config_path, 'attaskcreator.conf'), "w") as f:
        config.write(f)

def main():
    parser = argparse.ArgumentParser(prog='install.py',
            description='Installation script for attaskcreator'
            )

    parser.add_argument("-p", "--install-prefix", 
            help="Specify alternate installation prefix"
            )

    parser.add_argument("-s", "--install-units",
            action='store_true',
            help="Install systemd service and timer"
            )

    parser.add_argument("-c", "--config-file",
            help="Specify a configuration file"
            )

    parser.add_argument("--make-config",
            action='store_true',
            help="Interactively generate config file"
            )

    args = parser.parse_args()

    try:
        os.mkdir(config_path)
    except FileExistsError:
        pass
    except PermissionError:
        print("Cannot complete install without root privileges. Please rerun",
                "as root")
        exit(1)

    if args.make_config:
        make_config_file()

    install_cmd = ['python3', 'setup.py', 'install']

    if args.install_prefix:
        install_cmd.append('--prefix')
        install_cmd.append(args.install_prefix)

    # install
    run(install_cmd)


    # copy example config file
    copy2(
            os.path.join(here, 'extras', 'example.conf'),
            config_path
            )

    if args.config_file:
        copy2(args.config_file, '/etc/attaskcreator/attaskcreator.conf')
    

    if args.install_units:
        copy2(
                os.path.join(here, 'extras', 'attaskcreator.service'),
                '/etc/systemd/system/'
                )
        copy2(
                os.path.join(here, 'extras', 'attaskcreator.timer'),
                '/etc/systemd/system/'
                )
        run(['systemctl', 'start', 'attaskcreator.timer'])
        run(['systemctl', 'enable', 'attaskcreator.timer'])



if __name__ == "__main__":
    main()
