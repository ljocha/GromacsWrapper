# Copyright (c) 2009 Oliver Beckstein <orbeckst@gmail.com>
# Released under the GNU Public License 3 (or higher, your choice)
# See the file COPYING for details.
""":mod:`gromacs.tools` -- Gromacs commands classes
================================================

The underlying idea of GromacsWrapper is to automatically generate Python
classes that run the actual GROMACS tools. These classes are written in such a
way that they can be called as if they were functions with parameters
resembling the GROMACS tools commandline arguments. This a two-step process
when :mod:`gromacs` is imported: First a tool class is generated for each
GROMACS tool (the :ref:`command-list`). Then an *instance* of each of these
classes is instantiated in placed into the top level :mod:`gromacs`
module. Thus, :class:`gromacs.grompp` is an instance of
:class:`gromacs.tools.Grompp`. Users typically only access the tool *instances*
at the top level of the module.

.. note::

   Because the tool instances are autogenerated on the fly and depend on the
   installed GROMACS release, there is no autogenerated documentation available
   for them. Use in Python ``help(gromacs.grompp)`` to get help.

The following documentation for the :mod:`gromacs.tools` module describes in
more detail how GROMACS tools are generated and managed and is primarily of
interest to developers.


Gromacs tool instantiation
--------------------------

A Gromacs command class produces an instance of a Gromacs tool command
(:class:`gromacs.core.GromacsCommand`), any argument or keyword argument
supplied will be used as default values for when the command is run.

Classes have the same name of the corresponding Gromacs tool with the first
letter capitalized and dot and dashes replaced by underscores to make it a
valid python identifier.

The list of tools to be loaded is configured with the ``tools`` and ``groups``
options of the ``~/.gromacswrapper.cfg`` file. Guesses are made if these
options are not provided; see :mod:`gromacs.config` for details.

In the following example we create two instances of the
:class:`gromacs.tools.Trjconv` command (which runs the Gromacs ``trjconv``
command)::

  from gromacs.tools import Trjconv

  trjconv = tools.Trjconv()
  trjconv_compact = tools.Trjconv(ur='compact', center=True, boxcenter='tric', pbc='mol',
                                  input=('protein','system'))

The first one, ``trjconv``, behaves as the standard commandline tool but the
second one, ``trjconv_compact``, will by default create a compact
representation of the input data by taking into account the shape of the unit
cell. Of course, the same effect can be obtained by providing the corresponding
arguments to ``trjconv`` but by naming the more specific command differently
one can easily build up a library of small tools that will solve a specific,
repeatedly encountered problem reliably. This is particularly helpful when doing
interactive work.


Aliased commands
----------------

GromacsWrapper has been around since ancient GROMACS 4.5.x and throughout the
history it has provided a way to run different versions of GROMACS commands
with the same Python script in a backwards compatible manner by *aliasing*
equivalent GROMACS tools to the same GromacsWrapper tool (using
:data:`NAMES5TO4`). Modern GROMACS (since 5.x and throughout 2016-2023) tools
are aliased to their Gromacs 4 tool names for backwards compatibility.

For example, in "classic" GROMACS we had the :command:`g_sas` command that
became :command:`gmx sasa` since GROMACS 5.x. In GromacsWrapper you can access
the same tool as :class:`gromacs.g_sas` or :class:`gromacs.sasa`.

.. warning::

   You should check that the different GROMACS versions of tools give
   equivalent answers for your problem. The aliasing just makes it easy for you
   to call the tool in the same manner. You are still responsible for
   validating your own results.

Sometimes GROMACS changes commands in an way that is fundamentally incompatible
and in this way there is not much that GromacsWrapper can do. The best you can
probably do in your own scripts is to use :class:`gromacs.release` (see docs
for :class:`gromacs.tools.Release`) to check in your own script which release
of GROMACS is running and then call different tools depending on what you
find. For example, GROMACS 2023 replaced :command:`gmx do_dssp` with
:command:`gmx dssp` which is not directly argument-compatible so GromacsWrapper
does *not* alias it. Therefore, scripts relying on :class:`gromacs.do_dssp`
will break unless you account for it explicitly with code similar to ::

  release_year = int(gromacs.release()[:4])
  if release_year >= 2023:
      gromacs.dssp(s=TPR, f=XTC, sel="Protein",
                   o="dssp.dat", pbc=True, hmode="dssp")
  else:
      gromacs.do_dssp(s=TPR, f=XTC, input=["Protein"]
                      ssdump="ssdump.dat", o="ss.xpm", sc="scount.xvg")

.. note::

   It is recommended to keep a single version of all tools for a project and
   record the version in the methods section of a publication.



Multi index
-----------

It is possible to extend the tool commands and patch in additional
functionality. For example, the :class:`GromacsCommandMultiIndex` class makes a
command accept multiple index files and concatenates them on the fly; the
behaviour mimics Gromacs' "multi-file" input that has not yet been enabled for
all tools.

.. autoclass:: GromacsCommandMultiIndex
.. autofunction:: merge_ndx


.. _virtual-gromacs-commands:

Virtual Gromacs commands
------------------------

The following "commands" do not exist as tools in the Gromacs package
but are added here because they are useful.

.. autoclass:: Release


Helpers
-------

These helper functions are necessary for collecting and setting up the
Gromacs tools. They are mostly of interest to developers.

.. autodata:: NAMES5TO4
.. autodata:: V4TOOLS
.. autofunction:: tool_factory
.. autofunction:: load_v4_tools
.. autofunction:: load_v5_tools
.. autofunction:: find_executables
.. autofunction:: make_valid_identifier
.. autoexception:: GromacsToolLoadingError

Gromacs tools
-------------

Each command class in the :ref:`command-list` below is used to create
a command instance in the top level :mod:`gromacs` module *if the
Gromacs tools can be found in the file system* (see
:mod:`gromacs.config`). For example, the class :class:`Grompp` is used
to create the command :class:`gromacs.grompp`.


Registry
~~~~~~~~

The :ref:`command-list` below reflects the Gromacs commands that were
available when the documentation was built and can vary from
installation to installation. All currently available Gromacs commands
are listed in the dictionary :data:`gromacs.tools.registry`, in
particular, ``gromacs.tools.registry.keys()`` lists the names.

.. data:: registry
   :annotation: = {'Grompp': <gromacs.tools.Grompp', 'Mdrun': <gromacs.tools.Mdrun', ...}

   :class:`dict` that contains all currently available Gromacs
   commands as well as the :ref:`virtual-gromacs-commands`. The
   :data:`registry` is generated when the :mod:`gromacs.tools` package
   is imported for the first time.


.. _command-list:

Command list
~~~~~~~~~~~~

The list below reflects the Gromacs commands that were available when
the documentation was built and can vary from installation to
installation. All currently available Gromacs commands are listed in
the dictionary :data:`gromacs.tools.registry`, which can be processed
at run time.

.. The following is autogenerated with sphinx.

"""
from __future__ import absolute_import

import six

import os.path
import tempfile
import subprocess
import atexit
import logging
import re

from . import config
from .core import GromacsCommand

logger = logging.getLogger("gromacs.tools")

#: List of tools coming with standard Gromacs 4.x.
V4TOOLS = (
    "g_cluster",
    "g_dyndom",
    "g_mdmat",
    "g_principal",
    "g_select",
    "g_wham",
    "mdrun",
    "do_dssp",
    "g_clustsize",
    "g_enemat",
    "g_membed",
    "g_protonate",
    "g_sgangle",
    "g_wheel",
    "mdrun_d",
    "editconf",
    "g_confrms",
    "g_energy",
    "g_mindist",
    "g_rama",
    "g_sham",
    "g_x2top",
    "mk_angndx",
    "eneconv",
    "g_covar",
    "g_filter",
    "g_morph",
    "g_rdf",
    "g_sigeps",
    "genbox",
    "pdb2gmx",
    "g_anadock",
    "g_current",
    "g_gyrate",
    "g_msd",
    "g_sorient",
    "genconf",
    "g_anaeig",
    "g_density",
    "g_h2order",
    "g_nmeig",
    "g_rms",
    "g_spatial",
    "genion",
    "tpbconv",
    "g_analyze",
    "g_densmap",
    "g_hbond",
    "g_nmens",
    "g_rmsdist",
    "g_spol",
    "genrestr",
    "trjcat",
    "g_angle",
    "g_dielectric",
    "g_helix",
    "g_nmtraj",
    "g_rmsf",
    "g_tcaf",
    "gmxcheck",
    "trjconv",
    "g_bar",
    "g_dih",
    "g_helixorient",
    "g_order",
    "g_rotacf",
    "g_traj",
    "gmxdump",
    "trjorder",
    "g_bond",
    "g_dipoles",
    "g_kinetics",
    "g_pme_error",
    "g_rotmat",
    "g_tune_pme",
    "grompp",
    "g_bundle",
    "g_disre",
    "g_lie",
    "g_polystat",
    "g_saltbr",
    "g_vanhove",
    "make_edi",
    "xpm2ps",
    "g_chi",
    "g_dist",
    "g_luck",
    "g_potential",
    "g_sas",
    "g_velacc",
    "make_ndx",
)


#: dict of names in Gromacs 5 that correspond to an equivalent tool in
#: in Gromacs 4. The names are literal Gromacs names.
NAMES5TO4 = {
    # same name in both versions
    "grompp": "grompp",
    "eneconv": "eneconv",
    "editconf": "editconf",
    "pdb2gmx": "pdb2gmx",
    "trjcat": "trjcat",
    "trjconv": "trjconv",
    "trjorder": "trjorder",
    "xpm2ps": "xpm2ps",
    "mdrun": "mdrun",
    "make_ndx": "make_ndx",
    "make_edi": "make_edi",
    "genrestr": "genrestr",
    "genion": "genion",
    "genconf": "genconf",
    "do_dssp": "do_dssp",  # removed in GMX 2023, replaced with native `gmx dssp`
    # changed names
    "convert-tpr": "tpbconv",
    "dump": "gmxdump",
    "check": "gmxcheck",
    "solvate": "genbox",
    "distance": "g_dist",
    "sasa": "g_sas",
    "gangle": "g_sgangle",
}


class GromacsToolLoadingError(Exception):
    """Raised when no Gromacs tool could be found."""


class GromacsCommandMultiIndex(GromacsCommand):
    """Command class that accept multiple index files.

    It works combining multiple index files into a single temporary one so
    that tools that do not (yet) support multi index files as input can be
    used as if they did.

    It creates a new file only if multiple index files are supplied.
    """

    def __init__(self, **kwargs):
        kwargs = self._fake_multi_ndx(**kwargs)
        super(GromacsCommandMultiIndex, self).__init__(**kwargs)

    def run(self, *args, **kwargs):
        kwargs = self._fake_multi_ndx(**kwargs)
        return super(GromacsCommandMultiIndex, self).run(*args, **kwargs)

    def _fake_multi_ndx(self, **kwargs):
        ndx = kwargs.get("n")
        if (
            not (ndx is None or isinstance(ndx, six.string_types))
            and len(ndx) > 1
            and "s" in kwargs
        ):
            ndx.append(kwargs.get("s"))
            kwargs["n"] = merge_ndx(*ndx)
        return kwargs


def tool_factory(clsname, name, driver, base=GromacsCommand):
    """Factory for GromacsCommand derived types."""
    clsdict = {
        "command_name": name,
        "driver": driver,
        "__doc__": property(base._get_gmx_docs),
    }
    return type(clsname, (base,), clsdict)


def make_valid_identifier(name):
    """Turns tool names into valid identifiers.

    :param name: tool name
    :return: valid identifier
    """
    return name.replace("-", "_").capitalize()


def find_executables(path):
    """Find executables in a path.

    Searches executables in a directory excluding some know commands
    unusable with GromacsWrapper.

    :param path: dirname to search for
    :return: list of executables
    """
    execs = []
    for exe in os.listdir(path):
        fullexe = os.path.join(path, exe)
        if (
            os.access(fullexe, os.X_OK)
            and not os.path.isdir(fullexe)
            and exe
            not in [
                "GMXRC",
                "GMXRC.bash",
                "GMXRC.csh",
                "GMXRC.zsh",
                "demux.pl",
                "xplor2gmx.pl",
            ]
        ):
            execs.append(exe)
    return execs


def load_v5_tools():
    """Load Gromacs 2023/.../2016/5.x tools automatically using some heuristic.

    Tries to load tools (1) using the driver from configured groups (2) and
    falls back to automatic detection from ``GMXBIN`` (3) then to rough guesses.

    In all cases the command ``gmx help`` is run to get all tools available.

    :return: dict mapping tool names to GromacsCommand classes
    """
    logger.debug("Loading 2023/.../2016/5.x tools...")

    drivers = config.get_tool_names()

    if len(drivers) == 0 and "GMXBIN" in os.environ:
        drivers = find_executables(os.environ["GMXBIN"])

    if len(drivers) == 0 or len(drivers) > 4:
        drivers = ["gmx", "gmx_d", "gmx_mpi", "gmx_mpi_d"]

    append = config.cfg.getboolean("Gromacs", "append_suffix", fallback=True)

    tools = {}
    for driver in drivers:
        suffix = driver.partition("_")[2]
        try:
            out = subprocess.check_output([driver, "-quiet", "help", "commands"])
            for line in out.splitlines()[5:-1]:
                line = str(
                    line.decode("ascii")
                )  # Python 3: byte string -> str, Python 2: normal string

                if len(line) > 4:
                    if (line[4] != " ") and (" " in line[4:]):
                        name = line[4 : line.index(" ", 4)]
                        fancy = make_valid_identifier(name)
                        if suffix and append:
                            fancy = "{0!s}_{1!s}".format(fancy, suffix)
                        tools[fancy] = tool_factory(fancy, name, driver)
        except (subprocess.CalledProcessError, OSError):
            pass

    if not tools:
        errmsg = "Failed to load 2023/.../2016/5.x tools (tried drivers: {})".format(
            drivers
        )
        logger.debug(errmsg)
        raise GromacsToolLoadingError(errmsg)
    logger.debug("Loaded {0} v5 tools successfully!".format(len(tools)))
    return tools


def load_v4_tools():
    """Load Gromacs 4.x tools automatically using some heuristic.

    Tries to load tools (1) in configured tool groups (2) and fails back  to
    automatic detection from ``GMXBIN`` (3) then to a prefilled list.

    Also load any extra tool configured in ``~/.gromacswrapper.cfg``

    :return: dict mapping tool names to GromacsCommand classes
    """
    logger.debug("Loading v4 tools...")

    names = config.get_tool_names()

    if len(names) == 0 and "GMXBIN" in os.environ:
        names = find_executables(os.environ["GMXBIN"])

    if len(names) == 0 or len(names) > len(V4TOOLS) * 4:
        names = list(V4TOOLS)

    names.extend(config.get_extra_tool_names())

    tools = {}
    for name in names:
        fancy = make_valid_identifier(name)
        tools[fancy] = tool_factory(fancy, name, None)

    if not tools:
        errmsg = "Failed to load v4 tools"
        logger.debug(errmsg)
        raise GromacsToolLoadingError(errmsg)
    logger.debug("Loaded {0} v4 tools successfully!".format(len(tools)))
    return tools


def merge_ndx(*args):
    """Takes one or more index files and optionally one structure file and
    returns a path for a new merged index file.

    :param args: index files and zero or one structure file
    :return: path for the new merged index file
    """
    ndxs = []
    struct = None
    for fname in args:
        if fname.endswith(".ndx"):
            ndxs.append(fname)
        else:
            if struct is not None:
                raise ValueError("only one structure file supported")
            struct = fname

    fd, multi_ndx = tempfile.mkstemp(suffix=".ndx", prefix="multi_")
    os.close(fd)
    atexit.register(os.unlink, multi_ndx)

    if struct:
        make_ndx = registry["Make_ndx"](f=struct, n=ndxs, o=multi_ndx)
    else:
        make_ndx = registry["Make_ndx"](n=ndxs, o=multi_ndx)

    _, _, _ = make_ndx(input=["q"], stdout=False, stderr=False)
    return multi_ndx


# Load tools
if config.MAJOR_RELEASE in (
    "5",
    "2016",
    "2018",
    "2019",
    "2020",
    "2021",
    "2022",
    "2023",
):
    logger.debug(
        "Trying to load configured Gromacs major release {0}".format(
            config.MAJOR_RELEASE
        )
    )
    registry = load_v5_tools()
elif config.MAJOR_RELEASE == "4":
    logger.debug(
        "Trying to load configured Gromacs major release {0}".format(
            config.MAJOR_RELEASE
        )
    )
    registry = load_v4_tools()
else:
    logger.debug("No major release configured: trying 2023/.../2016/5.x -> 4.x")
    try:
        registry = load_v5_tools()
    except GromacsToolLoadingError:
        try:
            registry = load_v4_tools()
        except GromacsToolLoadingError:
            errmsg = "Autoloading was unable to load any Gromacs tool"
            logger.critical(errmsg)
            raise GromacsToolLoadingError(errmsg)

# Aliases command names to run unmodified GromacsWrapper scripts on a machine
# with only 5.x
# update with temporary directory
for fancy, cmd in list(registry.items()):
    for c5, c4 in six.iteritems(NAMES5TO4):
        # have to check each one, since it's possible there are suffixes
        # like for double precision; cmd.command_name is Gromacs name
        # (e.g. 'convert-tpr') so we need to be careful in the processing below.
        name = cmd.command_name
        if name.startswith(c5):
            if c4 == c5:
                break
            else:
                # maintain suffix (note: need to split with fancy because Gromacs
                # names (c5) may contain '-' etc)
                name = c4 + fancy.split(make_valid_identifier(c5))[1]
                registry[make_valid_identifier(name)] = registry[fancy]
                break
    else:
        # the common case of just adding the 'g_'
        registry["G_{0!s}".format(fancy.lower())] = registry[fancy]


# Patching up commands that may be useful to accept multiple index files
for name4, name5 in [("G_mindist", "Mindist"), ("G_dist", "Distance")]:
    if name4 in registry:
        cmd = registry[name4]
        registry[name4] = tool_factory(
            name4, cmd.command_name, cmd.driver, GromacsCommandMultiIndex
        )
        if name5 in registry:
            registry[name5] = registry[name4]


# create a release "virtual command" (issue #161)
class Release(object):
    """Release string of the currently loaded Gromacs version.

    :return:   str,
        Release string such as "2018.2" or "4.6.5" or ``None``
        if Gromacs can not be found.

    .. Note::

       The release string is obtained from the output of ``gmx grompp
       -version``, specifically the line starting with ``Gromacs
       version:``. If this changes then this function will break.

    .. rubric:: Example

    This command allows user code to work around known issues with
    old/new versions of Gromacs::

      if gromacs.release.startswith("4"):
        # do something for classic Gromacs
      else:
        # do it the modern way

    (Note that calling ``gromacs.release()`` will simply return the
    release string, which is equivalent to
    ``str(gromacs.release)``. For convenience, the :meth:`startswith`
    method exists, which directly works with the release string.)


    .. versionadded:: 0.8.0

    """

    gromacs_version = re.compile(
        "^G[rR][oO][mM][aA][cC][sS] version:" "\s*(VERSION)?\s*(?P<version>.+)$"
    )

    def __init__(self):
        self.release = None
        try:
            grompp = registry["Grompp"]()
            rc, out, err = grompp(version=True, stdout=False, stderr=False)
            output_lines = out.splitlines() + err.splitlines()
        except KeyError:
            output_lines = []

        for line in output_lines:
            line = line.strip()
            m = self.gromacs_version.match(line)
            if m:
                self.release = m.group("version")
                break

    def __call__(self):
        if self.release is None:
            logger.warning("gromacs.release(): cannot determine Gromacs release")

        return self.release

    def startswith(self, *args, **kwargs):
        """gromacs.release.startswith(prefix[, start[, end]]) -> bool

        Return ``True`` if the Gromacs release string starts with the
        specified `prefix`, ``False`` otherwise.  With optional
        `start`, test the string beginning at that position.  With
        optional `end`, stop comparing the release string at that
        position.  `prefix` can also be a tuple of strings to try, for
        example ::

          gromacs.release.startswith(('2016', '2018', '2019'))

        """
        return self.release.startswith(*args, **kwargs)

    def __str__(self):
        return self.release or "unknown"


# Append class doc for each command
for name in six.iterkeys(registry):
    __doc__ += ".. class:: {0!s}\n    :noindex:\n".format(name)

registry["Release"] = Release

# Finally add command classes to module's scope
globals().update(registry)
__all__ = ["GromacsCommandMultiIndex", "merge_ndx"]
__all__.extend(list(registry.keys()))
