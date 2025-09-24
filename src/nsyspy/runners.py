import subprocess
import os
import datetime as dt
from .analysis import NsysSqlite

class Runner:
    def __init__(self, nsys_path: str = "nsys"):
        self._nsys_path = nsys_path

    def execute(self, command: list | str, verbose: bool = False):
        """
        Generic method to execute a nsys command.
        Use this if none of the convenience functions match your use-case.

        Parameters
        ----------
        command : list | str
            The command to execute. Any valid input that works with subprocess.run().

        verbose : bool
            Prints the command being executed if True. Defaults to False.
        """
        if isinstance(command, str):
            command = [command]
        c = [self._nsys_path]
        c.extend(command)
        if verbose:
            print(c)
        subprocess.run(c)

    def profile(self, target: list[str] | str, *profile_args, reportname: str | None = None, verbose: bool = False) -> str:
        """
        Convenience function to execute 'nsys profile'.

        Parameters
        ----------
        target : list[str] | str
            Target executable, along with additional command line arguments.

        reportname : str | None
            Output report name. Is passed to '--output'.
            Automatically generated with the current timestamp if left as None.

        verbose : bool
            See execute() for details.

        *profile_args
            Additional arguments to pass to nsys profile (these come before the target).

        Returns
        -------
        reportname : str
            The output report name. Useful if it was automatically generated.
        """
        if reportname is None:
            now = dt.datetime.now().timestamp()
            reportname = f"report_{int(now)}.nsys-rep"
        command = ["profile", f"--output={reportname}", *profile_args]
        command.extend(target)
        self.execute(command, verbose)
        if not os.path.exists(reportname):
            raise FileNotFoundError(f"Could not find {reportname}")
        return reportname

    def export(self, reportname: str, *export_args, verbose: bool = False) -> NsysSqlite:
        """
        Convenience function to execute 'nsys export'.
        Fixed to sqlite output formats (for now at least).

        Parameters
        ----------
        reportname : str
            Target report, along with additional command line arguments.
            Should just be the output from profile(), for example.

        verbose : bool
            See execute() for details.

        *export_args
            Additional arguments to pass to nsys export.

        Returns
        -------
        db : NsysSqlite
            Instance of NsysSqlite, which is the container for the generated database.
        """
        # Enforce sqlite
        command = ["export", "--type=sqlite", *export_args, reportname]
        outputname = os.path.splitext(reportname)[0] + ".sqlite"
        self.execute(command, verbose)
        if not os.path.exists(outputname):
            raise FileNotFoundError(f"Could not find {outputname}")
        return NsysSqlite(outputname)

