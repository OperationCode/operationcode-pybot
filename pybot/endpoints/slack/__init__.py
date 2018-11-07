from . import events, actions, commands, messages


def create_endpoints(plugin):
    events.create_endpoints(plugin)
    actions.create_endpoints(plugin)
    commands.create_endpoints(plugin)
    messages.create_endpoints(plugin)
