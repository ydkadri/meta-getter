#!/usr/bin/env python3

'''
A CLIck wrapper for Apache Tika and AWS Comprehend to identify PII in
a provided filepath
'''

import os
import json
import subprocess

from pprint import pformat
from tika import parser

import click


def _parse_tika_output(fpath):
    '''Use the Python Tika from_file parser and restructure the output
    '''
    parsed = parser.from_file(fpath)
    text = parsed['content'].strip()
    meta = {
        k.lower().replace('-', '_'): v for k, v in parsed['metadata'].items()
        if k.lower() in ('author', 'content-type', 'creator', 'application-name')
    }
    return text, meta

def _parse_stdout(stdout):
    '''Parse the stdout output of subprocess.run
    '''
    lines = [line.strip() for line in stdout.decode().split('\n')]
    return json.loads(' '.join(lines))

def _parse_comprehend_output(output):
    '''Parse the output of AWS comprehend, removing the PII containing field
    '''
    entities = {}
    for entity in output['Entities']:
        entity_type = entity['Type']
        # etiher append or create the meta item minus the PII text
        if entity_type in entities:
            entities[entity_type].append(
                {k: v for k, v in entity.items() if k != 'Text'}
            )
        else:
            entities[entity_type] = [
                {k: v for k, v in entity.items() if k != 'Text'}
            ]
    return entities

@click.command()
@click.argument(
    'fpath',
    type=click.Path(exists=True),
)
@click.option(
    '--pretty',
    '-p',
    is_flag=True
)
def check_pii(fpath, pretty):
    '''Check a given filepath for PII using AWS comprehend
    '''
    fdir, fname = os.path.split(os.path.realpath(fpath))
    text, meta = _parse_tika_output(fpath)
    # AWS comprehend entity detection
    cmd = [
        'aws', 'comprehend',
        'detect-entities',
        '--text', text,
        '--language-code', 'en'
    ]
    process = subprocess.run(cmd, stdout=subprocess.PIPE, check=True)
    output = _parse_stdout(process.stdout)
    # clean output for loading
    meta['filename'] = fname
    meta['file_dir'] = fdir
    meta['entities'] = _parse_comprehend_output(output)
    if pretty:
        formatted_output = pformat(meta)
        click.echo(formatted_output)
    else:
        click.echo(meta)

if __name__ == '__main__':
    check_pii()
