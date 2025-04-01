def deploy_testnet():
    # Define the configuration for the testnet
    testnet_config = {
        'nodes': [
            {'host': 'localhost', 'port': 5001},
            {'host': 'localhost', 'port': 5002}
        ],
        'initial_balances': {
            'node1_public_key': 1000,  # 1000 XKW
            'node2_public_key': 1000   # 1000 XKW
        }
    }
    # Initialize the nodes and start the testnet
    for node_config in testnet_config['nodes']:
        node = Node(node_config['host'], node_config['port'])
        node.start()

    print("Testnet deployed successfully with nodes:", testnet_config['nodes'])
