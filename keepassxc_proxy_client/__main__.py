import sys
import json
from os import path
import base64
import argparse
import configparser
from keepassxc_proxy_client import protocol
#import protocol

def command_create(args):
    connection = protocol.Connection()
    connection.connect()
    connection.associate()

    if not connection.test_associate():
        print("For some reason the newly created association is invalid, this should not be happening")
        sys.exit(1)

    name, public_key = connection.dump_associate()
    key = base64.b64encode(public_key).decode('utf-8')
    print(f"# Add the following to {args.config} ")
    print(f"[connection]")
    print(f"    name = {name}")
    print(f"    key = {key}")

def command_get(args):
    full_path = path.expanduser(args.config) 
    config = configparser.ConfigParser()
    config.read(full_path)

    connection = protocol.Connection()
    connection.connect()
    connection.load_associate(
        config['connection']['name'],
        base64.b64decode(config['connection']['key'])
    )

    if not connection.test_associate():
        print("The loaded association is invalid", file=sys.stderr)
        sys.exit(1)

    logins = connection.get_logins(args.url)
    if not logins:
        print("No logins found for the given URL", file=sys.stderr)
        sys.exit(1)

    end = '' if args.n else '\n'

    if args.user:
        print(logins[0]['login'], end=end)
    else:
        print(logins[0]['password'], end=end)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", type=str, default='~/.keepassxc-client', help="Config file to read")

    subparsers = parser.add_subparsers(required=True)
    subparser = subparsers.add_parser('create', help='Create a new association')
    subparser.set_defaults(func=command_create)

    subparser = subparsers.add_parser('get', help='Create a new association')
    subparser.set_defaults(func=command_get)
    subparser.add_argument('url')
    subparser.add_argument('-n', action='store_true', help='do not output the trailing newline')
    subparser.add_argument('-u', '--user', action='store_true', help='Print the user/login instead of the password')
    args = parser.parse_args()
    args.func(args)
