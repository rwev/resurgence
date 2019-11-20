""" 
RESURGENCE.PY

Python script for restarting a process on file changes.

Author: rwev (https://github.com/rwev)
"""

from __future__ import print_function

import os
import re
import subprocess
import sys
import time
from optparse import OptionParser

import psutil


def string_list_callback(option, opt, value, parser):
    setattr(parser.values, option.dest, value.split(","))


parser = OptionParser()

parser.add_option(
    "-w",
    "--cwd",
    action="store_true",
    dest="do_observe_current_directory",
    default=False,
    help="Observe the current working directory",
)
parser.add_option(
    "-t",
    "--extensions",
    dest="regex_file_patterns_to_observe",
    type="string",
    default=[],
    action="callback",
    callback=string_list_callback,
    help="Comma-separated, spaceless list of file patterns to be observed",
)
parser.add_option(
    "-d",
    "--dirs",
    dest="additional_subdirectories_to_observe",
    type="string",
    default=[],
    action="callback",
    callback=string_list_callback,
    help="Comma-separated, spaceless list of subdirectories (below the working directory) to be observed",
)
parser.add_option(
    "-x",
    "--command",
    dest="command_to_run_str",
    type="string",
    default="",
    help="Command to run, restart on detected file changes, in single quotes",
)
parser.add_option(
    "-i",
    "--interval",
    dest="file_check_interval_seconds",
    type="float",
    default=1,
    help="Interval in seconds between checks for file changes.",
)


def get_observed_relative_filepaths_for_directory(relative_dir, regex_whitelist, include_subdirs=False):
    # returns list of relative paths to files to be observed
    relative_filepaths = []
    if include_subdirs:
        for root, dirs, files in os.walk(relative_dir, topdown=True):
            for filename in files:
                if run_filters(filename, regex_whitelist):
                    relative_filepaths.append(os.path.join(root, filename))
    else:
        files = get_files_in_directory(relative_dir)
        for filename in files:
            if run_filters(filename, regex_whitelist):
                relative_filepaths.append(os.path.join(relative_dir, filename))
    return relative_filepaths


def get_files_in_directory(dir):
    return [f for f in os.listdir(dir) if os.path.isfile(os.path.join(dir, f))]


def run_filters(name, filters):
    for regex in filters:
        if re.search(regex, name):
            return True
    return False


def get_last_edited_filepath_and_time(relative_filepaths):
    last_modification_time = 0
    for filepath in relative_filepaths:
        modification_time = os.stat(filepath).st_mtime
        if modification_time > last_modification_time:
            last_modification_time = modification_time
            last_edited_filepath = filepath
    return last_edited_filepath, last_modification_time


def kill_proc_tree(pid, including_parent=True):
    print("\tKilling process tree for parent with ID %d..." % pid)
    parent = psutil.Process(pid)
    # recursive option includes child, grandchildren (further generations)
    children = parent.children(recursive=True)
    for child in children:
        child.kill()
        print("\t\tKilled child process with ID %d." % child.pid)

    gone, still_alive = psutil.wait_procs(children, timeout=5)
    if including_parent:
        parent.kill()
        parent.wait(5)
        print("\t\tKilled parent process with ID %d." % parent.pid)


def print_stdout(process):
    stdout = process.stdout
    if stdout != None:
        print(stdout)


def main():
    (options, args) = parser.parse_args(sys.argv)

    # ARGUMENT CHECKS #

    # must monitor at least one directory
    if (not options.do_observe_current_directory) and (
            not len(options.additional_subdirectories_to_observe)
    ):
        print(
            "At least one directory must be observed: use argument(s) '-w' and / or '-d'."
        )
        sys.exit(0)
    # must specify command
    if not options.command_to_run_str:
        print("Must specify command to execute with '-x' argument.")
        sys.exit(0)
    # must specify at least one file pattern to match
    if not len(options.regex_file_patterns_to_observe):
        print(
            "Must specify command at least one regex pattern matching files to be watched."
        )
        sys.exit(0)

    # only allows the use of blacklist OR whitelist (recommend change)
    regex_whitelist = []
    for regex_rule in options.regex_file_patterns_to_observe:
        if regex_rule.startswith("*"):
            regex_rule = regex_rule[1:]
        regex_whitelist.append("%s$" % regex_rule)

    # PROCESS ARGUMENTS #

    command = options.command_to_run_str
    wait = options.file_check_interval_seconds

    filepaths_to_watch = []
    if options.do_observe_current_directory:
        filepaths_to_watch.extend(
            get_observed_relative_filepaths_for_directory(".", regex_whitelist, include_subdirs=False)
        )
    for dir in options.additional_subdirectories_to_observe:
        filepaths_to_watch.extend(
            get_observed_relative_filepaths_for_directory(dir, regex_whitelist, include_subdirs=True)
        )

    print("Watching files:")
    for filepath in filepaths_to_watch:
        print("\t%s" % filepath)

    # PROCESS AND OBSERVATION LOOP #
    # The current maximum file modified time under the watched directory
    last_edited_filepath, last_modification_time = get_last_edited_filepath_and_time(
        filepaths_to_watch
    )
    # shell=False => do not spawn shell process first. Results in fewer processes to kill.
    process = subprocess.Popen(command, shell=True)

    while True:
        temp_last_edited_filepath, temp_last_modification_time = get_last_edited_filepath_and_time(
            filepaths_to_watch
        )
        print_stdout(process)
        if temp_last_modification_time > last_modification_time:
            last_modification_time = temp_last_modification_time
            print("%s modified. Restarting..." % temp_last_edited_filepath)
            try:
                kill_proc_tree(process.pid)
            except Exception as e:
                print(
                    "\tUnable to kill process with ID %d. (Exception: %s"
                    % (process.pid, e)
                )
                pass
            process = subprocess.Popen(command, shell=True)
            print("New process started with ID %d." % process.pid)
        time.sleep(wait)


if __name__ == "__main__":
    main()
