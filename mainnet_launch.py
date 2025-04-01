def launch_mainnet():
    # Define the configuration for the mainnet
    mainnet_config = {
        'nodes': [
            {'host': '0.0.0.0', 'port': 6001},
            {'host': '0.0.0.0', 'port': 6002}
        ],
        'initial_balances': {
            'mainnet_node1_public_key': 10000,  # 10000 XKW
            'mainnet_node2_public_key': 10000   # 10000 XKW
        }
    }
    # Initialize the nodes and start the mainnet
    for node_config in mainnet_config['nodes']:
        node = Node(node_config['host'], node_config['port'])
        node.start()

    print("Mainnet launched successfully with nodes:", mainnet_config['nodes'])
