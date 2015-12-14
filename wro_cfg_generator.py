#!/usr/bin/python
import os
import sys
import argparse
import yaml
import re

verbose = False

def main(argv):
    parser = argparse.ArgumentParser(prog=__file__)
    parser.add_argument('--app', help='root file to process (default: ./Application.js)', default="Application.js")
    parser.add_argument('--map', help='mapping of classes to directories, eg --map IPticket:/x/y/', action='append', default=[])
    parser.add_argument('--workspace', help='project resources directory (default: ".")', default=".")
    parser.add_argument('--verbose', help='run in verbose mode', action='store_true')
    args = parser.parse_args()

    global verbose
    verbose = args.verbose

    # default maps
    path_map = {"Ext": None,
                "Common": None,
                "Deft": None}
    path_map.update(dict([tuple(i.split(":")) for i in args.map]))

    if verbose:
        print >> sys.stderr, "Path maps:" + `path_map`


    ordered_dependencies = resolve_dependencies(args.app, path_map)

    workspace = os.path.expanduser(args.workspace)

    print "\n".join(["<js>" + i[len(workspace):] + "</js>" for i in ordered_dependencies])

def resolve_dependencies(file, path_map, resolved=[], unresolved=[]):
    if file not in resolved:
        if verbose:
            print  >> sys.stderr, "Processing %s"%file
        if file in unresolved:
            raise Exception("Cyclic dependency for " + file)
        unresolved.append(file)
        deps = find_dependencies(file)
        for d in deps:
            f = convert_class_to_path(d, path_map)
            if f:
                resolve_dependencies(f,
                    path_map,
                    resolved,
                    unresolved)
        unresolved.remove(file)
        resolved.append(file)
    return resolved

def find_dependencies(file):
    file_contents = open(file).read()
    deps = find_json_array(file_contents, "requires")
    deps = deps + find_json_value(file_contents, "model")
    deps = deps + find_json_value(file_contents, "controller")
    deps = deps + find_json_value(file_contents, "extend")
    if verbose:
        print  >> sys.stderr, "Dependencies of %s are %s"%(file, deps)
    return deps

def find_json_array(jscontents, key):
    match = re.search(r"%s\s*:\s*(\[[^\]]*\])"%key, jscontents)
    if match == None:
        return []
    (requires,) = match.groups()
    #yaml does not process tabs properly
    requires = requires.replace("\t", " ")
    return yaml.load(requires)

def find_json_value(jscontents, key):
    match = re.search(r"%s\s*:\s*([^,\}]*)"%key, jscontents)
    if match == None:
        return []
    (requires,) = match.groups()
    return [yaml.load(requires)]


def convert_class_to_path(cls, path_map):
    dpos = cls.rfind(".")
    while dpos != -1:
        dir = cls[dpos:].replace(".", "/")
        pkg = cls[:dpos]
        if pkg in path_map:
            if not path_map[pkg]:
                if verbose:
                    print  >> sys.stderr, "Class %s is ignored"%(cls)
                return None
            f = os.path.expanduser(path_map[pkg].rstrip("/") + dir + ".js")
            if verbose:
                print  >> sys.stderr, "Class %s is mapped to location %s"%(cls, f)
            return f
        dpos = cls.rfind(".", 0, dpos)
    raise Exception("Could not find a path for this class (missing --map maybe?): " + cls)

if __name__ == "__main__":
    main(sys.argv[1:])
