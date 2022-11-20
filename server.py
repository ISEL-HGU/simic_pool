import socket
import threading
import sys
import pickle
import subprocess
import os
import detreefy as dt
from gensim.models.doc2vec import Doc2Vec
from scipy import spatial
from nltk.tokenize import word_tokenize
import nltk
nltk.download('punkt')

suggestions = []
similarity_candidate = []

def detreefy_builder(static, change_vector:str, snap:str):
    global similarity_candidate
    global suggestions
    sugg, match_num = dt.detreefy(static, change_vector)
    snap_vec = d2v_model.infer_vector(tokenize(snap))
    if sugg is None:
        # TO DO: heuristics for finding similar change vectors
        # child -> sibling -> parent
        sys.exit()
    else:
        idx:int = 0
        builder = []
        print(str(match_num) + ' exact matches found' + '\n')
        for i in range(0, match_num):
            suggestion = sugg[i]
            builder.append(threading.Thread(target=suggestions_builder, args=(suggestion[0], suggestion[2], suggestion[3], suggestion[4])))
            print(idx, len(builder))
            builder[idx].start()
            idx = idx + 1
            if (i+1) % 30 == 0 or i == match_num - 1:
                for j in range(0, idx):
                    builder[j].join()
                idx = 0
                builder = []
                # for s in similarity_candidate:
                #     print(s)
                #     print('=====================================================')
                if len(similarity_candidate) >= 10:
                    sim = [cos_sim(s, snap_vec) for s in similarity_candidate]
                    val, index = min((val, index) for (index, val) in enumerate(sim))
                    suggestions.append(similarity_candidate[index])
                    print(len(suggestions),'\n',similarity_candidate[index])
                    similarity_candidate = []
        
                        
                    
            
def cos_sim(diff,snap_vec):
    vec = d2v_model.infer_vector(tokenize(diff))
    cos_distance = spatial.distance.cosine(vec, snap_vec)
    return cos_distance

def tokenize (code):
    lines = code.split('\n')[7:]
    code = ''
    for line in lines:
        code = code + line + '\n'
    token = word_tokenize(code.lower())
    through_token = [item for item in token if not '#' in item and not '!' in item and not '-' in item and not ':' in item and not '*' in item and not '\'' in item and not '=' in item
            and not '/' in item and not '\\' in item and not '.' in item and not ',' in item and not ';' in item and not '(' in item and not ')' in item and not '[' in item
            and not ']' in item and not '{' in item and not '}' in item and not '<' in item and not '>' in item and not '@' in item and not '$' in item and not '%' in item
            and not '^' in item and not '&' in item and not '~' in item and not '`' in item and not '|' in item and not '"' in item and not '?' in item and not '+' in item
            and not '``' in item and item.isnumeric() == False]
    non_flat = [item.split('_') for item in through_token]
    flat = [item for l in non_flat for item in l if item != '']
    return flat
            
def suggestions_builder(proj, pc, file, line):
    global similarity_candidate
    process = subprocess.Popen(['make', 'pp_run','proj='+proj, 'pc='+pc, 'file='+file, 'line='+line], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    code = ''
    for line in process.stdout:
        if str(line).startswith('b\''):
            line = str(line).replace('b\'','').replace('b\"','').replace('\\n\'','') + '\n'
        elif str(line).startswith('b\"'):
            line = str(line).replace('b\"','').replace('\\n\"','') + '\n'

        if line.startswith('SLF4J:'):
            continue
        elif line.startswith('null'): 
            similarity_candidate = []
            sys.exit()
        code = code + line
    similarity_candidate.append(code)
        
    sys.exit()

def processMessages(conn, addr, static):
    while True:
        try:
            data = conn.recv(5000)
            print(data)
            if not data: 
                conn.close()
            data = data.decode('utf-8')
            if data == 'GET':
                if len(suggestions) == 0:
                    conn.sendall(bytes('It is either we don\'t have enough snapshots or it is still processing. \nPlease try later...','utf-8'))
                else:
                    conn.sendall(bytes(suggestions[0], 'utf-8'))
                    suggestions.pop(0)
            else:
                tmp = data.split('!@#$%')
                change_vector = tmp[0]
                snap = tmp[1]
                print(change_vector)
                conn.sendall(bytes('Thank you for connecting', 'utf-8'))
                detreefier = threading.Thread(target=detreefy_builder, args=(static, str(change_vector),snap))
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



if len(sys.argv) != 3:
    print('Usage: python3 server.py <IP> <port>')
    sys.exit()
s = socket.socket()                      # Create a socket object
host = sys.argv[1]
#"127.0.0.1"            # Get local machine name

port = sys.argv[2]
#64555                             # Reserve a port for your service.
s = socket.socket()
s.bind((host, int(port)))                     # Bind to the port

s.listen(5)                              # Now wait for client connection.

d2v_model = Doc2Vec.load('./train/d2v.model')

with open('./pool.tree','rb') as file:
        unpickler = pickle.Unpickler(file)
        print(unpickler.__str__)
        static = unpickler.load()
        if __name__ == '__main__':
            main()