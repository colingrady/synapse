import sys
import asyncio
import logging
import argparse

import synapse.exc as s_exc
import synapse.common as s_common
import synapse.telepath as s_telepath

import synapse.lib.cli as s_cli
import synapse.lib.node as s_node
import synapse.lib.time as s_time
import synapse.lib.output as s_output

logger = logging.getLogger(__name__)

ERROR_COLOR = '#ff0066'
WARNING_COLOR = '#f4e842'
NODEEDIT_COLOR = "lightblue"

welcome = '''
Welcome to the Storm interpreter!

Local interpreter (non-storm) commands may be executed with a ! prefix:
    Use !quit to exit.
    Use !help to see local interpreter commands.
'''
class QuitCmd(s_cli.CmdQuit):
    '''
    Quit the current command line interpreter.

    Example:

        !quit
    '''
    _cmd_name = '!quit'

class HelpCmd(s_cli.CmdHelp):
    '''
    List interpreter extended commands and display help output.

    Example:

        !help foocmd

    '''
    _cmd_name = '!help'

class StormCli(s_cli.Cli):

    histfile = 'storm_history'

    async def __anit__(self, item, outp=s_output.stdout, opts=None):

        await s_cli.Cli.__anit__(self, item, outp=outp)

        self.indented = False
        self.cmdprompt = 'storm> '

        self.stormopts = {'repr': True}
        self.hidetags = False
        self.hideprops = False

        self.printf(welcome)

    def initCmdClasses(self):
        self.addCmdClass(QuitCmd)
        self.addCmdClass(HelpCmd)

    def printf(self, mesg, addnl=True, color=None):
        if self.indented:
            s_cli.Cli.printf(self, '')
            self.indented = False
        return s_cli.Cli.printf(self, mesg, addnl=addnl, color=color)

    async def runCmdLine(self, line):

        if line[0] == '!':
            return await s_cli.Cli.runCmdLine(self, line)

        async for mesg in self.item.storm(line, opts=self.stormopts):

            if mesg[0] == 'node':

                node = mesg[1]
                formname, formvalu = s_node.reprNdef(node)

                self.printf(f'{formname}={formvalu}')

                if not self.hideprops:

                    for name in sorted(s_node.props(node).keys()):

                        valu = s_node.reprProp(node, name)

                        if name[0] != '.':
                            name = ':' + name

                        self.printf(f'        {name} = {valu}')

                if not self.hidetags:

                    for tag in sorted(s_node.tagsnice(node)):

                        valu = s_node.reprTag(node, tag)
                        tprops = s_node.reprTagProps(node, tag)
                        printed = False
                        if valu:
                            self.printf(f'        #{tag} = {valu}')
                            printed = True

                        if tprops:
                            for prop, pval in tprops:
                                self.printf(f'        #{tag}:{prop} = {pval}')
                            printed = True

                        if not printed:
                            self.printf(f'        #{tag}')

            elif mesg[0] == 'node:edits':
                edit = mesg[1]
                count = sum(len(e[2]) for e in edit.get('edits', ()))
                s_cli.Cli.printf(self, '.' * count, addnl=False, color=NODEEDIT_COLOR)
                self.indented = True

            elif mesg[0] == 'fini':
                took = mesg[1].get('took')
                took = max(took, 1)
                count = mesg[1].get('count')
                pers = float(count) / float(took / 1000)
                self.printf('complete. %d nodes in %d ms (%d/sec).' % (count, took, pers))

            elif mesg[0] == 'print':
                self.printf(mesg[1].get('mesg'))

            elif mesg[0] == 'warn':
                info = mesg[1]
                warn = info.pop('mesg', '')
                xtra = ', '.join([f'{k}={v}' for k, v in info.items()])
                if xtra:
                    warn = ' '.join([warn, xtra])
                self.printf(f'WARNING: {warn}', color=WARNING_COLOR)

            elif mesg[0] == 'err':
                err = mesg[1]
                if err[0] == 'BadSyntax':
                    pos = err[1].get('at', None)
                    text = err[1].get('text', None)
                    tlen = len(text)
                    mesg = err[1].get('mesg', None)
                    if pos is not None and text is not None and mesg is not None:
                        text = text.replace('\n', ' ')
                        # Handle too-long text
                        if tlen > 60:
                            text = text[max(0, pos - 30):pos + 30]
                            if pos < tlen - 30:
                                text += '...'
                            if pos > 30:
                                text = '...' + text
                                pos = 33

                        self.printf(text)
                        self.printf(f'{" "*pos}^')
                        self.printf(f'Syntax Error: {mesg}', color=ERROR_COLOR)
                        return

                text = err[1].get('mesg', err[0])
                self.printf(f'ERROR: {text}', color=ERROR_COLOR)

def getArgParser():
    pars = argparse.ArgumentParser(prog='synapse.tools.storm')
    pars.add_argument('cortex', help='A telepath URL for the Cortex')
    return pars

async def main(argv):  # pragma: no cover
    pars = getArgParser()
    opts = pars.parse_args(argv)

    path = s_common.getSynPath('telepath.yaml')
    telefini = await s_telepath.loadTeleEnv(path)

    async with await s_telepath.openurl(opts.cortex) as proxy:
        proxy.onfini(telefini)
        async with await StormCli.anit(proxy, opts=opts) as cli:
            cli.colorsenabled = True
            await cli.addSignalHandlers()
            await cli.runCmdLoop()

if __name__ == '__main__': # pragma: no cover
    sys.exit(asyncio.run(main(sys.argv[1:])))