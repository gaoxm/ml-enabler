import click
from ml_enabler.commands import fetch_predictions

@click.group()
@click.option('--endpoint', default='http://localhost:8501/v1/models/looking_glass:predict')
@click.pass_context
def main_group(ctx, endpoint):
    ctx.obj = {}
    ctx.obj['endpoint'] = endpoint

main_group.add_command(fetch_predictions.fetch)