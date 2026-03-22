"""Jia Tech MES CLI - Command entry point."""

import sys
from typing import Optional

import click
from rich.console import Console
from rich.table import Table

from jiatech_mes.cli.server import server_group
from jiatech_mes.cli.database import db_group
from jiatech_mes.cli.module import module_group

console = Console()


@click.group()
@click.version_option(version='1.0.0', prog_name='jiatech-mes')
def main():
    """Jia Tech MES - Manufacturing Execution System CLI."""
    pass


main.add_command(server_group, name='server')
main.add_command(db_group, name='db')
main.add_command(module_group, name='module')


if __name__ == '__main__':
    main()
