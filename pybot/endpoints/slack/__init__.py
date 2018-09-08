from . import events, actions, commands


def create_endpoints(plugin):
    events.create_endpoints(plugin)
    actions.create_endpoints(plugin)
    commands.create_endpoints(plugin)