#!/usr/bin/env python3

import argparse
import json
import os
import shutil
import subprocess
import sys
import urllib.parse

import nbformat
import requests

# Simplified representation of a Dockerfile
class Dockerfile(object):
    def __init__(self, mode):
        self.base_image = 'nb2dashboard'
        self.env = {}
        self.labels = {}
        self.mode = mode
        self.files = []
        self.build_commands = []

    # Set notebook file
    def set_notebook(self, filename):
        self.notebook = filename
        self.add_file(filename)

    # Set an environment variable
    def set_env(self, key, value):
        self.env[key] = value

    # Set a docker image label
    def set_label(self, key, value):
        self.labels[key] = value

    # Add a file to the build
    def add_file(self, filename):
        self.files.append(filename)

    # Add an extra RUN command to the build
    def add_build_command(self, command):
        self.build_commands.append(command)

    # Text of the Dockerfile
    def __str__(self):
        lines = ['FROM ' + self.base_image, '']
        if self.env:
            s = ' '.join('{}="{}"'.format(k, v) for k, v in self.env.items())
            lines.append('ENV ' + s)
        if self.labels:
            s = ' '.join('{}="{}"'.format(k, v) for k, v in self.labels.items())
            lines.append('LABEL ' + s)
        if self.files:
            s = ' '.join('"{}"'.format(filename) for filename in self.files)
            lines.append('ADD {} /home/jovyan/'.format(s))
        for command in self.build_commands:
            lines.append('RUN ' + command)
        lines.append('')
        lines.append('CMD ["{}", "/home/jovyan/{}"]'.format(self.mode, self.notebook))
        lines.append('')
        return "\n".join(lines)


# Stage and build a docker image dashboard from a notebook
class NB2Dashboard(object):
    def __init__(self, name, mode):
        self.name = name
        self.build_dir = 'nb2dashboard-' + name
        self.make_build_dir()
        self.mode = mode
        self.dockerfile = Dockerfile(mode)

    # Create build directory (docker context)
    def make_build_dir(self):
        if os.path.exists(self.build_dir):
            shutil.rmtree(self.build_dir)
        os.makedirs(self.build_dir)

    # Modify notebook for suitability with dashboard mode
    def groom_notebook(self):
        output = os.path.join(self.build_dir, self.notebook_filename)
        nbformat.write(self.notebook, open(output, 'w'))
        self.dockerfile.set_notebook(self.notebook_filename)

    # Use local notebook file
    def notebook_from_file(self, filename):
        self.notebook_filename = os.path.basename(filename)
        self.notebook = nbformat.read(open(filename), as_version=4)

    # Fetch notebook from remote URL
    def notebook_from_url(self, url):
        raise RuntimeError('not implemented yet')

    # Fetch notebook from an nbgallery instance
    def notebook_from_nbgallery(self, url):
        raise RuntimeError('not implemented yet')

    # Set metadata from nbgallery section of notebook metadata
    def metadata_from_nbgallery(self):
        pass # TODO

    # Set metadata from command-line args
    def metadata_from_args(self, args):
        pass # TODO

    # Write Dockerfile to build dir
    def save_dockerfile(self):
        output = os.path.join(self.build_dir, 'Dockerfile')
        open(output, 'w').write(str(self.dockerfile))

    # Prep all files and save to build dir
    def stage(self, args):
        if args.file:
            self.notebook_from_file(args.file)
        elif args.url:
            self.notebook_from_url(args.url)
        elif args.nbgallery:
            self.notebook_from_nbgallery(args.nbgallery)
        self.metadata_from_nbgallery()
        self.metadata_from_args(args)
        self.groom_notebook()
        self.save_dockerfile()

    # Build the docker image
    def build(self):
        command = 'sudo docker build -t nb2dashboard-{} {}'.format(self.name, self.build_dir)
        print(command)
        status, output = subprocess.getstatusoutput(command)
        if status != 0:
            print('docker build failed:')
            print(output)


# Main
if __name__ == '__main__':
    modes = ['voila', 'nbparameterise']
    parser = argparse.ArgumentParser(description='Build dashboard image from notebook')
    parser.add_argument('--name', help='image name suffix', required=True)
    parser.add_argument('--file', help='build from notebook file')
    parser.add_argument('--url', help='build from notebook URL')
    parser.add_argument('--nbgallery', help='build from nbgallery URL')
    parser.add_argument('--mode', help='dashboard mode', default='voila', choices=modes)
    parser.add_argument('--build', help='build the image', default=False, action='store_true')
    args = parser.parse_args(sys.argv[1:])

    if not (args.file or args.url or args.nbgallery):
        raise RuntimeError('--file, --url, or --nbgallery must be specified')

    nb2dashboard = NB2Dashboard(args.name, args.mode)
    nb2dashboard.stage(args)
    if args.build:
        nb2dashboard.build()
