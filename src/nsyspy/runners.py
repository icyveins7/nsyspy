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

    def profile(self, target: list[str] | str, *profile_args, reportname: str | None = None, verbose: bool = False) -> str:
        if reportname is None:
            now = dt.datetime.now().timestamp()
            reportname = f"report_{int(now)}.nsys-rep"
        command = ["profile", f"--output={reportname}", *profile_args]
        command.extend(target)
        self.execute(command, verbose)
        if not os.path.exists(reportname):
            raise FileNotFoundError(f"Could not find {reportname}")
        return reportname

    def export(self, target: str, *args, verbose: bool = False) -> NsysSqlite:
        # Enforce sqlite
        command = ["export", "--type=sqlite", *args, target]
        outputname = os.path.splitext(target)[0] + ".sqlite"
        self.execute(command, verbose)
        if not os.path.exists(outputname):
            raise FileNotFoundError(f"Could not find {outputname}")
        return NsysSqlite(outputname)

