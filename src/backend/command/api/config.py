import click
from flask import Blueprint
from swagger.utils.tools import swagger_resource_path_to_resource_id
from utils import Config

bp = Blueprint('config', __name__, url_prefix='/command/config')


def path_type(ctx, param, value):
    import os
    return os.path.expanduser(value)


def resource_id_type(value):
    return swagger_resource_path_to_resource_id(value)


# commands
@bp.cli.command("generate", short_help="Run a development server.")
@click.option(
    "--swagger-path", '-s',
    type=click.Path(file_okay=False, dir_okay=True, readable=True, resolve_path=True),
    default=Config.SWAGGER_PATH,
    required=not Config.SWAGGER_PATH,
    callback=Config.validate_and_setup_swagger_path,
    expose_value=False,
    help="The local path of azure-rest-api-specs repo. Official repo is https://github.com/Azure/azure-rest-api-specs"
)
@click.option(
    "--config-path",
    required=True,
    type=click.Path(writable=True, resolve_path=True),
    callback=path_type,
    help="Path to an existing configuration path."
)
@click.option(
    "--module",
    required=True,
    help="Name of the module to generate."
)
@click.option(
    "--resource-id", "--resource",
    required=True,
    type=resource_id_type,
    help="Path or ID of the resource to generate."
)
@click.option(
    "--version",
    required=True,
    help="Version of the configuration to generate."
)
def generate_config(config_path, module, resource_id, version):
    from command.model.configuration import CMDResource, CMDConfiguration
    from swagger.controller.command_generator import CommandGenerator
    from utils.constants import PlaneEnum

    generator = CommandGenerator(module_name=f"{PlaneEnum.Mgmt}/{module}")
    cmd_resource = CMDResource({"id": resource_id, "version": version})
    resources = generator.load_resources([cmd_resource])
    command_group = generator.create_draft_command_group(resources[resource_id])

    model = CMDConfiguration({"resources": [cmd_resource], "command_group": command_group})
    with open(config_path, "w") as fp:
        fp.write(model.to_xml())
    return "Done."
