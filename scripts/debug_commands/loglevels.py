import logging
from typing import List

from scripts.debug_commands import Command
from scripts.debug_commands.utils import add_output_line_to_log

logger = logging.getLogger(__name__)


class SetLogLevel(Command):
    name = "set"
    description = "Set the logging level"
    aliases = ["update", "change"]
    usage = "<module> <level>"

    def callback(self, args: List[str]):
        if len(args) != 2:
            add_output_line_to_log("Specify the module & logging level")
            return
        level = args[1].casefold()
        if level in ["notset", "reset", "0", "r"]:
            logging.getLogger(args[0]).setLevel(logging.NOTSET)
            add_output_line_to_log(f"Set {args[0]} logging to notset")
        if level in ["debug", "10", "d"]:
            logging.getLogger(args[0]).setLevel(logging.DEBUG)
            add_output_line_to_log(f"Successfully set {args[0]} logging to debug")
        elif level in ["info", "20", "i"]:
            logging.getLogger(args[0]).setLevel(logging.INFO)
            add_output_line_to_log(f"Successfully set {args[0]} logging to info")
        elif level in ["warn", "warning", "30", "w", "default"]:
            logging.getLogger(args[0]).setLevel(logging.WARNING)
            add_output_line_to_log(
                f"Successfully set {args[0]} logging to warning (default)"
            )
        elif level in ["error", "40", "e"]:
            logging.getLogger(args[0]).setLevel(logging.ERROR)
            add_output_line_to_log(f"Successfully set {args[0]} logging to error")
        elif level in ["critical", "50", "c"]:
            logging.getLogger(args[0]).setLevel(logging.CRITICAL)
            add_output_line_to_log(f"Successfully set {args[0]} logging to critical")
        else:
            add_output_line_to_log(f"Unrecognised logging level '{level}'.")


class GetLogLevel(Command):
    name = "get"
    description = "Get the log level for a given module"
    usage = "<module>"

    def callback(self, args: List[str]):
        argcount = len(args)
        if argcount == 0:
            add_output_line_to_log("Specify a module.")
            return
        elif argcount > 1:
            add_output_line_to_log(f"Too many arguments. Expected 1, got {argcount}.")
            return
        del argcount
        module = args[0]
        add_output_line_to_log(
            f"Effective logging level for {module}: {logging.getLogger().getEffectiveLevel()}"
        )


class LogLevelCommand(Command):
    name = "logging"
    description = "Information about logging levels"
    aliases = ["log", "loglevel"]
    usage = "<module> <level>"

    sub_commands = [GetLogLevel(), SetLogLevel()]

    def callback(self, args: List[str]):
        add_output_line_to_log("Please specify a subcommand")
