#!/usr/bin/env python3

"""DoorPi Setup"""

import pathlib
import sys

import setuptools.command.install

BASE_PATH = pathlib.Path(__file__).resolve().parent
ETC = "/etc" if sys.prefix == "/usr" else "etc"


class InstallHook(setuptools.command.install.install):
    """Hook for ``install`` command that processes template files (*.in)"""
    def run(self):
        datapath = BASE_PATH / "data"
        package = self.distribution.metadata.name.lower()
        substkeys = {
            "package": package,
            "project": self.distribution.metadata.name,
            "prefix": self.prefix,
            "cfgdir": pathlib.Path(
                self.prefix if sys.prefix == "/usr" else "", "etc", package
            ),
        }
        for file in datapath.iterdir():
            if file.suffix != ".in":
                continue
            content = file.read_text()
            for key, val in substkeys.items():
                content = content.replace(f"!!{key}!!", val)
            file.with_suffix("").write_text(content)
        super().run()


setuptools.setup(
    cmdclass={"install": InstallHook},
    data_files=[
        # init script and systemd service
        (f"{ETC}/init.d", ["data/doorpi.sh"]),
        ("lib/systemd/system", ["data/doorpi.service", "data/doorpi.socket"]),
    ],
)
