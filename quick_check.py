
import json
import subprocess

import click

from tika import parser

def _parse_stdout(stdout):
    lines = [line.strip() for line in stdout.decode().split('\n')]
    return json.loads(' '.join(lines))

@click.command()
@click.option(
    '--fpath',
    '-f',
    type=click.Path(exists=True),
    help='File path to analyze'
)
def check_pii(fpath):
    # read document with tika and clean it ready for load
    parsed = parser.from_file(fpath)
    text = parsed['content'].strip()
    meta = {
        k: v for k, v in parsed['metadata'].items()
        if k.lower() in ('author', 'content-type', 'creator', 'application-name')
    }
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
    meta['entities'] = entities
    import pprint
    pprint.pprint(meta)


if __name__ == '__main__':
    check_pii()

