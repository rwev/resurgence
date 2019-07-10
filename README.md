# resurgence
Restart a process when files are changed

## Inspiration 
File watchers are standard in many development workflows, but most utilities only handle
execution of short running processes (compilation, transpilation, formatting,
linting). But what if a project not only want to run a command and let it finish, but instead start a process and let it run until the next change?

This is where I was at when tinkering with [derivat](https://www.github.com/rwev/derivat), I wanted to see how code changes would affect the GUI (PyQT) interface. I couldn't use standard file watchers, because they either 1) would become unresponsive on first execution (application startup), never returning to to event loop and respond to more changes, 2) couldn't kill the previous process and thus would continuously spawn another application instance.

Resurgence is a product of this need - kill the previous process, if still
running, and execute the specified command again, using the updated application source.

## Requirements 
Python 2.6+
psutil

## Installation
```shell
$ pip install https://www.github.com/rwev/resurgence/archive/master.zip
```

## Usage
```shell
$ resurgence --help
resurgence.py [options]
Options:
  -h, --help            show this help message and exit
  -w, --cwd             Observe the current working directory
  -t REGEX_FILE_PATTERNS_TO_OBSERVE, --extensions=REGEX_FILE_PATTERNS_TO_OBSERVE
                        Comma-separated, spaceless list of file patterns to be
                        observed
  -d ADDITIONAL_SUBDIRECTORIES_TO_OBSERVE, --dirs=ADDITIONAL_SUBDIRECTORIES_TO_OBSERVE
                        Comma-separated, spaceless list of subdirectories
                        (below the working directory) to be observed
  -x COMMAND_TO_RUN_STR, --command=COMMAND_TO_RUN_STR
                        Command to run, restart on detected file changes, in
                        single quotes
  -i FILE_CHECK_INTERVAL_SECONDS, --interval=FILE_CHECK_INTERVAL_SECONDS
                        Interval in seconds between checks for file changes.
```

## Alternatives
- [when-changed](https://www.github.com/joh/when-changed), also a Python utility, 3rd party dependency watchdog, can't
  restart processes
- [entr](https://www.github.com/clibs/entr), C utility, offers -r option to restart process, usable in Unix pipes
