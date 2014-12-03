__author__ = 'obscure'
'''
    try:
        OFServer = socketserver.TCPServer((IP, OFPORT), MyTCPHandler)
    except IOError:
        print('Cannot start OFServer on ', OFPORT)
        exit(-1)
    print ('Listening on ', IP, DPORT)

    pc = DataClassifier.PktClassifier
    try:
        dataServer = socketserver.TCPServer((IP, DPORT), pc)
    except IOError:
        print('Cannot start DataServer on', DPORT)
        dataServer.server_close()
        exit(-1)
    #Create the OFMsgClassifier
    try:
        classifier = OFMsgClassifier()
        #OFServer.serve_forever(classifier)
    except IOError:
        print('Could not serve forever on ', OFPORT)
        #OFServer.server_close()
        dataServer.server_close()
    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    try:
        dataServer.serve_forever(pc)
    except IOError:
        print('Could not serve forever on ', DPORT)
        #OFServer.server_close()
        dataServer.server_close()
    #Send scores to controller: Open a client and send?
'''
