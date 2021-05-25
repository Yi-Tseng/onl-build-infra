#!/usr/bin/python3
################################################################
#
#        Copyright 2013, Big Switch Networks, Inc.
#
# Licensed under the Eclipse Public License, Version 1.0 (the
# "License"); you may not use this file except in compliance
# with the License. You may obtain a copy of the License at
#
#        http://www.eclipse.org/legal/epl-v10.html
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the License for the specific
# language governing permissions and limitations under the
# License.
#
################################################################

###############################################################################
#
# Module Manifest Generator.
#
#
###############################################################################
import sys
import os
import datetime
import re

class ManifestBase(object):
    """ Base class for all module manifest generators. """

    #
    # Provided by the derives classes.
    #
    # Target filename
    target = None
    # Description of file
    desc = None
    # Block comment start, if applicable
    commentStart=""
    # Block comment end, if applicable
    commentStop=""

    def __init__(self):
        # Autogeneration timestamp.
        self.now = datetime.datetime.now()
        # regexp used to recognize module definitions
        self.moduleRE = re.compile(r'\s*MODULE\s*:=\s*(?P<modname>.*)')

    def generate(self, rootdir="."):

        os.chdir(rootdir)

        s = ""
        s += self.commentStart
        s += """
##############################################################################
#
# %(DESCRIPTION)s
#
# Autogenerated %(TIMESTAMP)s
#
##############################################################################
""" % dict(DESCRIPTION=self.desc, TIMESTAMP=self.now)

        s += self.commentStop
        s += self.initsection()
        self.modules = {}
        for root, dirs, files in os.walk('.'):
            for file_ in files:
                if file_ == "Makefile":
                    fname = "%s/%s" % (root, file_)
                    for line in open(fname, 'r'):
                        m = self.moduleRE.match(line)
                        if m:
                            if root.startswith("./"):
                                root = root.replace("./", "")
                            self.modules[m.group('modname')] = root

        for modname, root in sorted(self.modules.items()):
            s += self.module(modname, root)

        s += self.denitsection()
        s += "\n"

        if self.target == "-" or self.target == "stdout":
            sys.stdout.write(s)
        else:
            open(self.target, "w").write(s);


    def module(self, modname, root):
        return ""
    def initsection(self):
        return ""
    def denitsection(self):
        return ""


class MakeManifest(ManifestBase):
    """Generates the Manifest.mk file used by the Builder."""
    target = "Manifest.mk"
    desc = "Builder Module Manifest."

    def initsection(self):
        return "BASEDIR := $(dir $(lastword $(MAKEFILE_LIST)))\n"

    def module(self, modname, root):
        return "%s_BASEDIR := $(BASEDIR)%s\n" % (modname, root)

    def denitsection(self):
        return "\n\nALL_MODULES := $(ALL_MODULES) %s" % (
            " ".join(sorted(self.modules.keys())))

class EnvManifest(ManifestBase):
    """Generates the Manifest.sh file containing environment location variables."""
    target = "Manifest.sh"
    desc = "Module Directory Location Variable Manifest."

    def module(self, modname, root):
        return "%s=`dirname $BASH_SOURCE`/%s/module\n" % (modname.upper(), root)


class DoxManifest(ManifestBase):
    """Generates the Manifest.doxy input file."""
    target = "Manifest.doxy"
    desc = "Doxygen Input Manifest."

    def initsection(self):
        return "INPUT = "

    def module(self, modname, root):
        # Only modules with a doxyfile are included.
        if os.path.exists("%s/%s.doxy" % (root, modname)):
            return "%s/module/inc " % (root)
        else:
            return ""


if __name__ == "__main__":

    classes = dict(make=MakeManifest,
                   env=EnvManifest,
                   dox=DoxManifest,)

    if len(sys.argv) == 1:
        print("Module Manifest Tool", file=sys.stderr)
        print(sys.stderr, "usage: %s [%s|all]" % (
            sys.argv[0], "|".join(classes.keys())), file=sys.stderr)
        for n in classes.keys():
            print("%-10s%s" % (n, classes[n].__doc__), file=sys.stderr)
        print(sys.stderr, "%-10s%s" % (
            "all", "Generate all files."), file=sys.stderr)

        sys.exit(1)


    targets = sys.argv[1:]
    if "all" in targets:
        targets = classes.keys()

    for name in targets:
        if name in classes:
            x = classes[name]()
            x.generate()
        else:
            raise Exception("%s is not a valid generation option." % name)






