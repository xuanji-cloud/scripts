#!/usr/bin/env python
import click
from commands import cmd_image_upload


@click.group
@click.pass_context
def cli(ctx):
    """Gamebox Management Tool"""
    ctx.ensure_object(dict)


cli.add_command(cmd_image_upload)

if __name__ == '__main__':
    cli(obj={})
