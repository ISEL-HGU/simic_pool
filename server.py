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
import time
import nltk
print(' ___  ____  __  __  ____  ___    ____  _____  _____  __   \n' +
        '/ __)(_  _)(  \/  )(_  _)/ __)  (  _ \(  _  )(  _  )(  )  \n' +
    '\__ \ _)(_  )    (  _)(_( (__    )___/ )(_)(  )(_)(  )(__ \n' +
    '(___/(____)(_/\/\_)(____)\___)  (__)  (_____)(_____)(____)\n')
print("\nChecking for necessary packages....")
nltk.download('punkt')

suggestions = []
similarity_candidate = []
match_num = 0
match_cnt = 0
mutex = 0 # if no process is running -> 0/ if process is already running -> 1/ if new process has to start -> 2
dirty_bit = 0 # if process was canceled or overridden by new post request becomes 1
lock = threading.Lock()

'''
This function creates threads for each exact matches in the pool.
@:param static: the static binary tree of data structure(pool), change vector:target editscript to look for, snap: the snapshot of the code
'''
def detreefy_builder(static:dt, change_vector:str, snap:str):
    global similarity_candidate
    global suggestions
    global match_num
    global match_cnt
    global mutex
    global lock
    

    sugg, match_num = dt.detreefy(static, change_vector)
    match_cnt = 0
    snap_vec = d2v_model.infer_vector(tokenize(snap))
    if sugg is None:
        # TO DO: heuristics for finding similar change vectors
        # child -> sibling -> parent
        print('There is no exact match in the pool')
        lock.release()
        match_cnt = -1
        mutex = 0
        sys.exit()
    else:
        idx:int = 0
        builder = []
        print(str(match_num) + ' exact matches for the given change vector found' + '\n')
        for i in range(0, match_num):
            suggestion = sugg[i]
            if len(suggestion[4]) > 300:
                continue
            match_cnt = i
            builder.append(threading.Thread(target=suggestions_builder, args=(suggestion[0], suggestion[2], suggestion[3], suggestion[4])))
            # print(idx, len(builder))
            builder[idx].start()
            idx = idx + 1
            
            if (i+1) % 10 == 0 or i == match_num - 1:
                print(f'Looking at {i+1}th match.....')
                for j in range(0, idx):
                    builder[j].join()
                if mutex == 2:
                    mutex = 1
                    print('\nexiting the current detreefication threads')
                    similarity_candidate = []
                    suggestions = []
                    lock.release()
                    sys.exit()
                print(f'Collected {len(similarity_candidate)} candidates.....')
                idx = 0
                builder = []
                # print(i, match_num, len(similarity_candidate))
                if len(similarity_candidate) >= 10 or i == match_num - 1:
                    print(f'Calculating imilarity for {len(similarity_candidate)} candidates.....')
                    sim = [cos_sim(s, snap_vec) for s in similarity_candidate]
                    val, index = min((val, index) for (index, val) in enumerate(sim))
                    print(f'The most similar change we found out of {len(similarity_candidate)} candidates is \n\n {similarity_candidate[index]}')
                    suggestions.append(similarity_candidate[index])
                    # print(len(suggestions),'\n',similarity_candidate[index])
                    similarity_candidate = []
                    print('Clearing candidates and continuing to search for more exact candidates from the rest of exact matches')
            # mutex_handler()
    match_cnt = -1
    mutex = 0
    print('match finding finished')
    lock.release()
        
def mutex_handler ():
    global mutex
    global suggestions
    global similarity_candidate
    if mutex == 2:
        time.sleep(3)
        suggestions = []
        similarity_candidate = []
        mutex = 1
        print('Starting a new process')
        sys.exit()                    
                    
            
def cos_sim(diff:str,snap_vec):
    vec = d2v_model.infer_vector(tokenize(diff))
    cos_distance = spatial.distance.cosine(vec, snap_vec)
    return cos_distance

'''
@:param code: a source code in string
@:return: flat:a list of tokens that can be used for embeddings
'''
def tokenize (code:str):
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
            
def suggestions_builder(proj:str, pc:str, file:str, blame_line:str):
    global similarity_candidate
    if len(blame_line) > 500:
        sys.exit()
    if blame_line[-1] == '\n':
        blame_line = blame_line[:-1]
    blame_line = blame_line.replace('"', 'ㅗ') # unsued delimeter since double quotation confuses the parser
    process = subprocess.Popen(['make', 'pp_run','proj='+proj, 'pc='+pc, 'file='+file, 'line='+"\""+blame_line+"\""], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    code = ''
    
    for line in process.stdout:
        if str(line).startswith('b\''):
            line = str(line).replace('b\'','').replace('b\"','').replace('\\n\'','') + '\n'
        elif str(line).startswith('b\"'):
            line = str(line).replace('b\"','').replace('\\n\"','') + '\n'
        
        if line.startswith('SLF4J:'):
            continue
        elif 'error: unable to get target hunk' in line or '[pp_run]' in line or 'git: changes are all deleted null' in line or '.ipynb' in line or 'error: unable to get target hunk' in line:
        #     # similarity_candidate = []
            # print(line)
            sys.exit()
        code = code + line
    # print(proj +'\t'+ pc+'\t'+ file +'\t'+ blame_line, code)
    # print(code)
        
    similarity_candidate.append(code)
    # print('suggestions_builder: ', len(similarity_candidate))
        
    sys.exit()

def processMessages(conn, addr, static:dt):
    global match_cnt
    global mutex
    global dirty_bit
    global lock
    while True:
        try:
            data = conn.recv(5000)
            # print(data)
            if not data: 
                conn.close()
            data = data.decode('utf-8')
            if data == 'GET':
                if len(suggestions) == 0 and dirty_bit == 0:
                    if len(similarity_candidate) == 0:
                        conn.sendall(bytes('We do not have enough snapshots\nPlease try taking more snapshots...','utf-8'))
                    elif match_cnt == -1:
                        conn.sendall(bytes('We could not find more relavant changes..\n Try with other snapshots...','utf-8'))
                    else:
                        conn.sendall(bytes(f'We are looking for semantically relavant change...\n We are processing {match_cnt}th file out of {match_num}matches\nTry in a bit.','utf-8'))
                elif dirty_bit == 1:
                    conn.sendall(bytes('Requst being processed.\n Looking for new suggestions for your latest snapshot....','utf-8'))
                    dirty_bit = 0
                else:
                    conn.sendall(bytes(suggestions[0], 'utf-8'))
                    suggestions.pop(0)
            else:
                tmp = data.split('!@#$%')
                change_vector = tmp[0]
                snap = tmp[1]
                if mutex == 1:
                    mutex = 2
                    print('New request detected, waiting for the previous process to exit')
                    print('overriding new request...')
                elif mutex == 0:
                    mutex = 1
                lock.acquire()
                print(f'Recieved Change Vector: {change_vector}')
                conn.sendall(bytes('Thank you for connecting', 'utf-8'))
                detreefier = threading.Thread(target=detreefy_builder, args=(static, str(change_vector),snap))
                detreefier.start()
        except:
            conn.close()
            # print("Connection closed by", addr)
            # Quit the thread.
            sys.exit()

def main():
        while True:
            # Wait for connections
            conn, addr = s.accept()
            # print('Got connection from ', addr[0], '(', addr[1], ')')
            # Listen for messages on this connection
            listener = threading.Thread(target=processMessages, args=(conn, addr, static))
            listener.start()



if len(sys.argv) != 3:
    print('Usage: python3 server.py <IP> <port>')
    sys.exit()

s = socket.socket()                             # Create a socket object
host = sys.argv[1]                              # Get local machine name
#"127.0.0.1"            

port = int(sys.argv[2])                              # Reserve a port for your service.
#64555                             
s = socket.socket()

try:
    print('\nChecking the port number and host IP address...')
    s.bind((host, port))                       # Bind to the port
except:
    print('Bind failed. Error : ' + str(sys.exc_info()))
    sys.exit()

s.listen(5)                                     # Now wait for client connection.

d2v_model = Doc2Vec.load('./train/d2v.model')   # load the Doc2Vec model
print("\nLoading the pool...")
with open('./pool.tree','rb') as file:          # load the pool
        unpickler = pickle.Unpickler(file)      
        print(unpickler.__str__)
        static = unpickler.load()
        if __name__ == '__main__':
            print('\n\nReady for service!')
            main()

