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
            s = ', '.join('"{}"'.format(filename) for filename in self.files)
            lines.append('ADD [{}, "/home/jovyan/"]'.format(s))
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
        self.metadata = {}

    # Create build directory (docker context)
    def make_build_dir(self):
        if os.path.exists(self.build_dir):
            shutil.rmtree(self.build_dir)
        os.makedirs(self.build_dir)

    # Remove ipydeps package installation and run during build instead
    def groom_ipydeps(self):
        for i in range(len(self.notebook.cells)):
            cell = self.notebook.cells[i]
            if cell.cell_type == 'code' and 'ipydeps' in cell.source:
                output = os.path.join(self.build_dir, 'ipydeps_build.py')
                with open(output, 'w') as f:
                    f.write(cell.source)
                self.dockerfile.add_file('ipydeps_build.py')
                self.dockerfile.add_build_command('python3 ipydeps_build.py')
                del self.notebook.cells[i]
                break

    # Move 'parameters'-tagged cells to top (papermill compatibility)
    def groom_parameters(self):
        first_code_cell = None
        parameters_cell = None
        for i in range(len(self.notebook.cells)):
            cell = self.notebook.cells[i]
            tags = cell.get('metadata', {}).get('tags', {})
            if cell.cell_type != 'code':
                continue
            if first_code_cell is None:
                first_code_cell = i
            if 'parameters' in tags:
                parameters_cell = i
                break
        if parameters_cell is not None:
            cell = self.notebook.cells[parameters_cell]
            del self.notebook.cells[parameters_cell]
            self.notebook.cells.insert(first_code_cell, cell)

    # Remove cells tagged with 'nb2dashboard/ignore'
    def groom_ignored(self):
        keepers = []
        for cell in self.notebook.cells:
            tags = cell.get('metadata', {}).get('tags', {})
            if 'nb2dashboard/ignore' not in tags:
                keepers.append(cell)
        self.notebook.cells = keepers

    # Modify notebook for suitability with dashboard mode
    def groom_notebook(self):
        # Run grooming functions
        self.groom_ignored()
        self.groom_ipydeps()
        if self.mode == 'nbparameterise':
            self.groom_parameters()

        # Save notebook
        output = os.path.join(self.build_dir, self.notebook_filename)
        with open(output, 'w') as f:
            nbformat.write(self.notebook, f)
        self.dockerfile.set_notebook(self.notebook_filename)

    # Use local notebook file
    def notebook_from_file(self, filename):
        self.notebook_filename = os.path.basename(filename)
        with open(filename) as f:
            self.notebook = nbformat.read(f, as_version=4)

    # Fetch notebook from remote URL
    def notebook_from_url(self, url):
        r = requests.get(url, headers={'Accept': 'application/json'})
        if r.status_code != 200:
            raise RuntimeError('{} {}'.format(r.status_code, r.reason))
        self.notebook = nbformat.reads(r.text, as_version=4)
        u = urllib.parse.urlparse(url)
        self.notebook_filename = u.path.split('/')[-1]
        self.metadata['url'] = url
        return r

    # Fetch notebook from an nbgallery instance
    def notebook_from_nbgallery(self, url):
        r = self.notebook_from_url(url + '/download')
        self.notebook_filename = r.headers['Content-Disposition'].split('"')[1]
        self.metadata['url'] = url

    # Set metadata from nbgallery section of notebook metadata
    def metadata_from_nbgallery_section(self):
        gallery = self.notebook.get('metadata', {}).get('gallery', {})
        if 'uuid' in gallery:
            self.metadata['uuid'] = gallery['uuid']
        if 'git_commit_id' in gallery:
            self.metadata['git_commit_id'] = gallery['git_commit_id']

    # Set metadata from command-line args
    def metadata_from_args(self, args):
        for key in ['maintainer', 'title', 'description']:
            if hasattr(args, key) and getattr(args, key):
                self.metadata[key] = getattr(args, key)

    # Gather metadata about the notebook
    def gather_metadata(self, args):
        self.metadata_from_nbgallery_section()
        self.metadata_from_args(args)
        print('Metadata:')
        for k, v in self.metadata.items():
            print(k, v)
        print()

    # Incorporate metadata into docker image
    def process_metadata(self):
        labels = {
            'url': 'notebook',
            'maintainer': 'maintainer',
            'title': 'title',
            'description': 'description'
        }
        envs = {
            'uuid': 'NBGALLERY_UUID',
            'git_commit_id': 'NBGALLERY_GIT_COMMIT_ID'
        }
        for key, label in labels.items():
            if key in self.metadata:
                self.dockerfile.set_label(label, self.metadata[key])
        for key, name in envs.items():
            if key in self.metadata:
                self.dockerfile.set_env(name, self.metadata[key])

    # Write Dockerfile to build dir
    def save_dockerfile(self):
        output = os.path.join(self.build_dir, 'Dockerfile')
        with open(output, 'w') as f:
            f.write(str(self.dockerfile))

    # Prep all files and save to build dir
    def stage(self, args):
        if args.file:
            self.notebook_from_file(args.file)
        elif args.url:
            self.notebook_from_url(args.url)
        elif args.nbgallery:
            self.notebook_from_nbgallery(args.nbgallery)
        self.gather_metadata(args)
        self.process_metadata()
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
    parser.add_argument('--maintainer', help='image maintainer')
    parser.add_argument('--title', help='notebook title')
    parser.add_argument('--description', help='notebook description')
    parser.add_argument('--build', help='build the image', default=False, action='store_true')
    args = parser.parse_args(sys.argv[1:])

    if not (args.file or args.url or args.nbgallery):
        raise RuntimeError('--file, --url, or --nbgallery must be specified')

    nb2dashboard = NB2Dashboard(args.name, args.mode)
    nb2dashboard.stage(args)
    if args.build:
        nb2dashboard.build()
