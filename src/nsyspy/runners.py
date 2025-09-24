import subprocess
import os
import datetime as dt
from .analysis import NsysSqlite

class Runner:
    def __init__(self, nsys_path: str = "nsys"):
        self._nsys_path = nsys_path

    def execute(self, command: list | str, verbose: bool = False):
        if isinstance(command, str):
            command = [command]
        c = [self._nsys_path]
        c.extend(command)
        if verbose:
            print(c)
        subprocess.run(c)

    def profile(self, target: str, *args, outputname: str | None = None, verbose: bool = False) -> str:
        if outputname is None:
            now = dt.datetime.now().timestamp()
            outputname = f"report_{int(now)}.nsys-rep"
        command = ["profile", f"--output={outputname}", *args, target]
        self.execute(command, verbose)
        if not os.path.exists(outputname):
            raise FileNotFoundError(f"Could not find {outputname}")
        return outputname

    def export(self, target: str, *args, verbose: bool = False) -> str:
        # Enforce sqlite
        command = ["export", "--type=sqlite", *args, target]
        outputname = os.path.splitext(target)[0] + ".sqlite"
        self.execute(command, verbose)
        if not os.path.exists(outputname):
            raise FileNotFoundError(f"Could not find {outputname}")
        return NsysSqlite(outputname)

