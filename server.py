import socket
import threading
import sys
import pickle
import detreefy as dt

suggestions = []
def suggestion_builder(static, change_vector):
    suggestions, match_num = dt.detreefy(static, change_vector)
    if suggestions is None:
        sys.exit()
    
    
def processMessages(conn, addr, static):
    while True:
        try:
            data = conn.recv(1024)
            if not data: 
                conn.close()
            change_vector = data.decode('utf-8')
            print(change_vector)
            conn.sendall(bytes('Thank you for connecting', 'utf-8'))
            detreefier = threading.Thread(target=suggestion_builder, args=(static, str(change_vector)))
            detreefier.start()
        except:
            conn.close()
            print("Connection closed by", addr)
            # Quit the thread.
            sys.exit()

def main():
        while True:
            # Wait for connections
            conn, addr = s.accept()
            print('Got connection from ', addr[0], '(', addr[1], ')')
            # Listen for messages on this connection
            listener = threading.Thread(target=processMessages, args=(conn, addr, static))
            listener.start()

s = socket.socket()                      # Create a socket object
host = "127.0.0.1"            # Get local machine name

port = 64555                             # Reserve a port for your service.
s = socket.socket()
s.bind((host, port))                     # Bind to the port

s.listen(5)                              # Now wait for client connection.

with open(sys.argv[1],'rb') as file:
        unpickler = pickle.Unpickler(file)
        print(unpickler.__str__)
        static = unpickler.load()
        if __name__ == '__main__':
            main()