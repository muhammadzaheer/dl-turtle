import socket
from handler import Handler

#initialize a TCP server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serving_address = ('localhost', 4784)
server.bind(serving_address)

#fire up server
server.listen(1)

while True:
  print 'waiting for client app'
  #await connection
  connection, client_address = server.accept()
  handler = Handler(connection)
  
  try:
    #show client address
    print 'connection from', client_address
    #start conversation
    
    while True:
      req = connection.recv(65536)
      print req, 'requested'
      
      #pass request to handler
      #if req == 'stop':
      #  handler.stop()
      if req[0:1] == '{':
        #checkout model from here
        handler.create_model(req) 
        print 'model recieved'
      else:
        handler.handle_request(req)
  finally:
    #close connection when client is no more there
    connection.close()
    print 'connection closed'
