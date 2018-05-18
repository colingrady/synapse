import sys
import json
import pprint
import argparse
import logging

import synapse.common as s_common
import synapse.telepath as s_telepath

import synapse.lib.output as s_output
import synapse.lib.msgpack as s_msgpack

logger = logging.getLogger(__name__)

def main(argv, outp=s_output.stdout):

    pars = argparse.ArgumentParser(prog='cryo.cat', description='display data items from a cryo cell')
    pars.add_argument('cryotank', help='The telepath URL for the remote cryotank.')
    pars.add_argument('--offset', default=0, type=int, help='Begin at offset index')
    pars.add_argument('--size', default=10, type=int, help='How many items to display')
    # TODO: synapse.tools.cryo.list <cryocell>
    #pars.add_argument('--list', default=False, action='store_true', help='List tanks in the remote cell and return')
    group = pars.add_mutually_exclusive_group()
    group.add_argument('--jsonl', action='store_true', help='Input/Output items in jsonl format')
    group.add_argument('--msgpack', action='store_true', help='Input/Output items in msgpack format')
    pars.add_argument('--verbose', '-v', default=False, action='store_true', help='Verbose output')
    pars.add_argument('--ingest', '-i', default=False, action='store_true',
                      help='Reverses direction: feeds cryotank from stdin in msgpack or jsonl format')
    pars.add_argument('--omit-offset', default=False, action='store_true',
                      help="Don't output offsets of objects. This is recommended to be used when jsonl/msgpack"
                           " output is used.")

    opts = pars.parse_args(argv)

    if opts.verbose:
        logger.setLevel(logging.INFO)

    if opts.ingest and not opts.jsonl and not opts.msgpack:
        logger.error('Must specify exactly one of --jsonl or --msgpack if --ingest is specified')
        return 1

    logger.info(f'connecting to: {opts.cryotank}')

    with s_telepath.openurl(opts.cryotank) as tank:

        try:

            typename = tank.getCellType()
            if typename != 'cryotank':
                outp.printf('error: remote object is a: {typename}')
                return 1

        except Exception as e:
            outp.printf('error: remote object is *not* a cell!')
            return 1

        if opts.ingest:

            if opts.msgpack:
                items = list(s_msgpack.iterfd(sys.stdin.buffer))
                tank.puts(items)
                return

            items = [json.loads(l) for l in sys.stdin]
            tank.puts(items)
            return 0

        for item in tank.slice(opts.offset, opts.size):

            if opts.omit_offset:
                item = item[1]

            if opts.jsonl:
                outp.printf(json.dumps(item, sort_keys=True))

            elif opts.msgpack:
                sys.stdout.buffer.write(s_msgpack.en(item))

            else:
                outp.printf(pprint.pformat(item))

if __name__ == '__main__':  # pragma: no cover
    logging.basicConfig()
    sys.exit(main(sys.argv[1:]))
