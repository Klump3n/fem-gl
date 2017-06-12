#!/usr/bin/env python3

import cmd
import json
import argparse
import requests


def grab_CLA():
    """
    Return the command line arguments.
    """

    parser = argparse.ArgumentParser()
    parser.add_argument('--host', type=str, required=False,
                        help='Host to connect to.')
    parser.add_argument('--port', type=int, required=False,
                        help='Port of host.')
    parsed_args = parser.parse_args()
    return parsed_args


class TestCMD(cmd.Cmd):
    """
    Send commands to the server.
    """

    def __init__(self, args):
        cmd.Cmd.__init__(self)
        self.prompt = '>> '
        self.intro = 'Welcome to fem-gl command line interface version 1.'
        self.headers = {'user-agent': 'fem-gl/1--alpha'}
        self.host = args.host
        self.port = args.port

    def post_prototype(self, api_call, data=None):
        """
        Prototype for sending a post request with error handling and so on.
        """

        try:
            url = 'http://{}:{}/{}'.format(self.host, self.port, api_call)
            response = requests.post(
                url=url,
                json=data,
                timeout=3.5,
                headers=self.headers
            )

            response.raise_for_status()
        except BaseException as e:
            return '{}'.format(e)

        return response.json()

    def do_hi(self, line):
        """
        Provoke a request by the server.
        """
        api_call = 'request_something'
        data = {'argument': 'noooo'}
        answer = self.post_prototype(api_call=api_call, data=data)
        print(answer)
        print(json.loads(answer)['answer'])

    def do_append(self, line):
        api_call = 'append_to_stack'
        data = ''
        answer = self.post_prototype(api_call=api_call, data=data)
        print(answer)

    def do_pop(self, line):
        api_call = 'pop_from_stack'
        data = ''
        answer = self.post_prototype(api_call=api_call, data=data)
        print(answer)

    def do_exit(self, line):
        """
        Exit the CLI.
        """
        print('Bye.')
        return -1

    def do_quit(self, line):
        """
        Exit alias.
        """
        return(self.do_exit(line))


if __name__ == '__main__':
    """
    Start.
    """
    ARGS = grab_CLA()
    CLI = TestCMD(args=ARGS)
    CLI.cmdloop()

