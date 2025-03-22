def main():
    import sys
    from importlib import import_module
    commands = {
        "graph_cache": {
            "launch": ("IPAnalysisTool.caching.graph_cache", "main"),
            "description": "Cache the graph data"
        },
        "time_series_analysis": {
            "launch": ("IPAnalysisTool.time_series_analysis", "main"),
            "description": "Gather data into a CSV file"
        },
        "hBackbone": {
            "launch": ("IPAnalysisTool.hBackbone", "main"),
            "description": "Find the hBackbone of a network"
        },
        "k_core": {
            "launch": ("IPAnalysisTool.k_core", "main"),
            "description": "Find the k-core of a network"
        }
    }

    if len(sys.argv) < 2 or sys.argv[1] not in commands:
        print("Welcome to IPAnalysisTool!\nAvailable commands:\n" +
              '\n'.join([f'{command}: {commands[command]["description"]}' for command in commands.keys()]) +
              f'\nUsage: {sys.argv[0]} <command> <args>' +
              '\nIf you need help with any command, use the -h or --help flag after the command name.')
        sys.exit(1)

    command = sys.argv[1]
    module_path, function_name = commands[command]["launch"]

    # Import the module dynamically and call the specified function
    module = import_module(module_path)
    function = getattr(module, function_name)
    function(sys.argv[2:])
if __name__ == "__main__":
    main()