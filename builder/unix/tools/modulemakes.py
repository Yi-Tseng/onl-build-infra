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
#
#
###############################################################################
import sys
import os
import argparse
import pprint
import datetime

ap = argparse.ArgumentParser(description="Modulemake");

ap.add_argument("--root",
                help="Root of the module directory. Also the location of the generated makefile.",
                default=".")

ap.add_argument("--name",
                help="Name of the module. Used in the comments.",
                required=True)

ap.add_argument("--makefile",
                help="Name of the generated file makefile. Default is <name>.mk",
                default=None)


ops = ap.parse_args();

if ops.makefile is None:
    ops.makefile = ops.name + ".mk"

#
# Find all files named 'make.mk', '_make.mk', or '__make.mk'
#
patterns = [ 'make.mk', '_make.mk', '__make.mk' ]
found = {}
for p in patterns:
    found[p] = []

for root, dirs, files in os.walk(ops.root):
    for file_ in files:
        if file_ in patterns:
            found[file_].append(dict(root=root,file=file_))

#
# Generate the output file
#
s = """
###############################################################################
#
# Inclusive Makefile for the %(MODULE)s module.
#
# Autogenerated %(TIMESTAMP)s
#
###############################################################################
%(MODULE)s_BASEDIR := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
""" % dict(MODULE=ops.name,TIMESTAMP=datetime.datetime.now())

#
# include files in the makefile in the same order listed in patterns
#
for p in patterns:
    for f in found[p]:
        root = os.path.abspath(f['root'])
        root = root.replace(os.path.abspath(ops.root)+"/", "$(%s_BASEDIR)" % (ops.name))
        root = root.replace(os.path.abspath(ops.root), "$(%s_BASEDIR)" % (ops.name))
        name = f['file']
        s += "include %s/%s\n" % (root, name)

s += "\n"

#
# Write makefile
#
open("%s/%s" % (os.path.abspath(ops.root), ops.makefile), "w").write(s)

