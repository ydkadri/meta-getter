#!/usr/bin/env python3

import os
import json
import subprocess

import click

from tika import parser
from pprint import pformat

def _parse_tika_output(fpath):
    parsed = parser.from_file(fpath)
    text = parsed['content'].strip()
    meta = {
        k.lower().replace('-', '_'): v for k, v in parsed['metadata'].items()
        if k.lower() in ('author', 'content-type', 'creator', 'application-name')
    }
    return text, meta

def _parse_stdout(stdout):
    lines = [line.strip() for line in stdout.decode().split('\n')]
    return json.loads(' '.join(lines))

def _parse_comprehend_output(output):
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
def check_pii(fpath):
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
    formatted_output = pformat(meta)
    click.echo(formatted_output)

if __name__ == '__main__':
    check_pii()

