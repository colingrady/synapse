import synapse.common as s_common

import synapse.tests.files as s_t_files
import synapse.tests.utils as s_t_utils

import synapse.lib.autodoc as s_l_autodoc

import synapse.tools.autodoc as s_autodoc

class TestAutoDoc(s_t_utils.SynTest):

    async def test_tools_autodoc_docmodel(self):

        with self.getTestDir() as path:

            argv = ['--doc-model', '--savedir', path]

            outp = self.getTestOutp()
            self.eq(await s_autodoc.main(argv, outp=outp), 0)

            with s_common.genfile(path, 'datamodel_types.rst') as fd:
                buf = fd.read()

            s = buf.decode()
            self.isin('Base types are defined via Python classes.', s)
            self.isin('synapse.models.inet.Addr', s)
            self.isin('Regular types are derived from BaseTypes.', s)
            self.isin(r'inet\:server', s)

            # Enums for int
            self.isin('``pe:resource:type``', s)
            self.isin('=== ===============', s)
            self.isin('int valu           ', s)
            self.isin('1   RT_CURSOR      ', s)

            # enusm for str
            self.isin('``it:mitre:attack:status``', s)
            self.isin('+----------+', s)
            self.isin('+valu      +', s)
            self.isin('+==========+', s)
            self.isin('+deprecated+', s)

            self.isin('''This type implements the following interfaces:

 * ``inet:service:object``
 * ``phys:object``''', s)

            with s_common.genfile(path, 'datamodel_forms.rst') as fd:
                buf = fd.read()

            s = buf.decode()
            self.isin('Forms are derived from types, or base types. Forms represent node types in the graph.', s)
            self.isin(r'inet\:ipv4', s)
            self.notin(r'file\:bytes:.created', s)
            self.isin('Universal props are system level properties which may be present on every node.', s)
            self.isin('.created', s)
            self.notin('..created\n', s)
            self.isin('An example of ``inet:dns:a``\\:', s)

            # Ipv4 property
            self.isin('''* - ``:asn``
        - :ref:`dm-type-inet-asn`
        - The ASN to which the IPv4 address is currently assigned.''', s)

            # Readonly inet:form:password:md5 value
            self.isin('''* - ``:md5``
        - :ref:`dm-type-hash-md5`
        - The MD5 hash of the password.
        - Read Only: ``True``''', s)

            # Refs edges def
            self.isin('''      * - ``*``
        - ``-(refs)>``
        - ``*``
        - The source node contains a reference to the target node.''', s)

            async with self.getTestCore() as core:
                lurl = core.getLocalUrl()
                argv = ['--doc-model', '--savedir', path, '--cortex', lurl]
                outp = self.getTestOutp()
                self.eq(await s_autodoc.main(argv, outp=outp), 0)

                with s_common.genfile(path, 'datamodel_types.rst') as fd:
                    buf = fd.read()

                s = buf.decode()
                self.isin('Base types are defined via Python classes.', s)

    async def test_tools_autodoc_confdefs(self):

        with self.getTestDir() as path:

            argv = ['--savedir', path, '--doc-conf',
                    'synapse.tests.test_lib_stormsvc.StormvarServiceCell']

            outp = self.getTestOutp()
            self.eq(await s_autodoc.main(argv, outp=outp), 0)

            with s_common.genfile(path, 'conf_stormvarservicecell.rst') as fd:
                buf = fd.read()
            s = buf.decode()

            self.isin('auth\\:passwd', s)
            self.isin('Environment Variable\n    ``SYN_STORMVARSERVICECELL_AUTH_PASSWD``', s)
            self.isin('The object expects the following properties', s)
            self.notin('``--mirror``', s)
            self.notin('_log_conf', s)

            # truncate the current file
            with s_common.genfile(path, 'conf_stormvarservicecell.rst') as fd:
                fd.truncate()

            outp = self.getTestOutp()
            self.eq(await s_autodoc.main(argv, outp=outp), 0)
            with s_common.genfile(path, 'conf_stormvarservicecell.rst') as fd:
                buf = fd.read()
            s = buf.decode()

    async def test_tools_autodoc_stormsvc(self):

        with self.getTestDir() as path:

            argv = ['--savedir', path, '--doc-storm',
                    'synapse.tests.test_lib_stormsvc.StormvarServiceCell']

            outp = self.getTestOutp()
            self.eq(await s_autodoc.main(argv, outp=outp), 0)

            with s_common.genfile(path, 'stormsvc_stormvarservicecell.rst') as fd:
                buf = fd.read()
            s = buf.decode()

            self.isin('StormvarServiceCell Storm Service', s)
            self.isin('This documentation is generated for version 0.0.1 of the service.', s)
            self.isin('Storm Package\\: stormvar', s)

            self.isin('.. _stormcmd-stormvar-magic:\n', s)
            self.isin('magic\n-----', s)
            self.isin('Test stormvar support', s)
            self.isin('forms as input nodes', s)
            self.isin('``test:str``', s)
            self.isin('nodes in the graph', s)
            self.isin('``test:comp``', s)
            self.isin('nodedata with the following keys', s)
            self.isin('``foo`` on ``inet:ipv4``', s)

            self.isin('.. _stormmod-stormvar-apimod', s)
            self.isin('status()', s)
            self.notin('testmod', s)

    async def test_tools_autodoc_stormpkg(self):

        with self.getTestDir() as path:

            ymlpath = s_t_files.getAssetPath('stormpkg/testpkg.yaml')

            argv = ['--savedir', path, '--doc-stormpkg', ymlpath]

            outp = self.getTestOutp()
            self.eq(await s_autodoc.main(argv, outp=outp), 0)

            with s_common.genfile(path, 'stormpkg_testpkg.rst') as fd:
                buf = fd.read()
            s = buf.decode()

            self.isin('Storm Package\\: testpkg', s)
            self.isin('This documentation is generated for version 0.0.1 of the package.', s)

            self.isin('This package implements the following Storm Commands.', s)
            self.isin('.. _stormcmd-testpkg-testpkgcmd', s)

            self.isin('testpkgcmd does some stuff', s)
            self.isin('Help on foo opt', s)
            self.isin('Help on bar opt', s)

            self.isin('forms as input nodes', s)
            self.isin('``test:str``', s)
            self.isin('nodes in the graph', s)
            self.isin('``test:int``', s)
            self.isin('nodedata with the following keys', s)
            self.isin('``testnd`` on ``inet:ipv4``', s)

            # Tuplelized output
            self.isin('testpkg.baz', s)
            self.isin("Help on baz opt (default: ('-7days', 'now'))", s)

            self.isin('This package implements the following Storm Modules.', s)
            self.isin('.. _stormmod-testpkg-apimod', s)

            self.notin('testmod', s)

            self.isin('search(text, mintime=-30days)', s)
            self.isin('text (str): The text.', s)
            self.isin('Yields:', s)
            self.isin('The return type is ``node``.', s)

            self.isin('status()', s)

            self.isin('newp()', s)
            self.isin('.. warning::\n', s)
            self.isin('``newp`` has been deprecated and will be removed in version v2.300.4.', s)
            self.isin('Newp is no longer maintained. Use bar() instead.', s)
            self.isin('Some nonexistent function', s)

            # coverage for no apidefs
            rst = s_l_autodoc.RstHelp()
            await s_autodoc.processStormModules(rst, 'foo', [])
            self.eq('\nStorm Modules\n=============\n\nThis package does not export any Storm APIs.\n', rst.getRstText())

    async def test_tools_autodoc_stormtypes(self):
        with self.getTestDir() as path:

            argv = ['--savedir', path, '--doc-stormtypes']
            outp = self.getTestOutp()
            self.eq(await s_autodoc.main(argv, outp=outp), 0)

            with s_common.genfile(path, 'stormtypes_libs.rst') as fd:
                libbuf = fd.read()
            libtext = libbuf.decode()

            self.isin('.. _stormlibs-lib-print:\n\n$lib.print(mesg, \\*\\*kwargs)\n============================',
                      libtext)
            self.isin('Print a message to the runtime.', libtext)
            self.isin('\\*\\*kwargs (any): Keyword arguments to substitute into the mesg.', libtext)
            self.isin('.. _stormlibs-lib-time:\n\n*********\n$lib.time\n*********', libtext)
            self.isin('A Storm Library for interacting with timestamps.', libtext)

            with s_common.genfile(path, 'stormtypes_prims.rst') as fd:
                primbuf = fd.read()
            primstext = primbuf.decode()
            self.isin('.. _stormprims-auth-user-f527:\n\n**********\nauth\\:user\n**********', primstext)
            self.isin('iden\n====\n\nThe User iden.', primstext)
