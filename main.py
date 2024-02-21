def ignore_command(s):
    a=['alias', 'configuration', 'ip', 'sql', 'select', 'update', 'exec', 'del', 'truncate']
    return any(i in s for i in a)