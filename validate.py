import detreefy as dt
import os
from gensim.models.doc2vec import Doc2Vec
import pickle
import subprocess
from scipy import spatial
from nltk.tokenize import word_tokenize
import sys

def main():
    editscript = sys.argv[1]    
    matches, count = dt.detreefy(pool, editscript)
    if matches is None:
        print('No matches found')
    else:
        print('Found ' + str(count) + ' matches')
        while(1):
            ans = input('Do you want to continue? (y/p/n): ')
            if ans == 'p':
                i = 0
                for match in matches:
                    i = i+1
                    print('f{i}: {match}')
            elif ans == 'n':
                exit()
            while(1):
                ans = input('p for setting pivot, v for view source code, q for exit')
                if ans == 'v':
                    i = input('Enter the index of the file you want to view: ')
                    i = int(i)
                    proj = matches[i][0]
                    cpc = matches[i][1]
                    file = matches[i][3]
                    blame_line = matches[i][4]
                    code = suggestions_builder(proj, cpc, file, blame_line)
                    if code is None:
                        print('No code found on index ' + str(i))
                    else:
                        print(code)
                elif ans == 'q':
                    break
                elif ans == 'p':
                    i = input('Enter the index of the file you want to set as pivot: ')
                    i = int(i)
                    proj = matches[i][0]
                    cpc = matches[i][1]
                    file = matches[i][3]
                    blame_line = matches[i][4]
                    code = suggestions_builder(proj, cpc, file, blame_line)
                    if code is None:
                        print('No code found on index ' + str(i))
                    else:
                        print('selected pivot code is as follows:')
                        print(code)
                        pivot = code
                        print('computing cosine similarity...')
                        snap_vec = d2v_model.infer_vector(tokenize(pivot))
                        similarity_list = []
                        code_list = []
                        i = 0
                        j = 10
                        for match in matches:
                            i = i+1
                            proj = match[0]
                            cpc = match[1]
                            file = match[3]
                            blame_line = match[4]
                            code = suggestions_builder(proj, cpc, file, blame_line)
                            if code is None:
                                code_list.append('')
                                similarity_list.append(1)
                            else:
                                code_list.append(code)
                                similarity_list.append(1 - cos_sim(code, snap_vec))
                            if i == int(len(matches)/i)*j:
                                print('f {j}0% done')
                                j = j+10
                        copy = similarity_list.copy()
                        while(1):
                            ans = input('top? [num/q/r]')
                            if ans == 'q':
                                break
                            elif ans == 'r':
                                copy = similarity_list.copy()
                            else:
                                topk = int(ans)
                                copy.sort()
                                i = 0
                                for i in range(topk):
                                    print(copy[i])
                                    print(code_list[similarity_list.index(copy[i])])
                                copy = copy[ans:]

                                



def suggestions_builder(proj:str, cpc:str, file:str, blame_line:str) -> str or None:
    global similarity_candidate
    if len(blame_line) > 500:
        return None
    if blame_line[-1] == '\n':
        blame_line = blame_line[:-1]
    blame_line = blame_line.replace('"', 'ㅗ') # unsued delimeter since double quotation confuses the parser
    process = subprocess.Popen(['make', 'pp_run','proj='+proj, 'pc='+cpc, 'file='+file, 'line='+"\""+blame_line+"\""], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
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
            print('can\'t find the code')
            return None
        code = code + line
    # print(proj +'\t'+ pc+'\t'+ file +'\t'+ blame_line, code)
    # print(code)
        
    return code
    # print('suggestions_builder: ', len(similarity_candidate))

def cos_sim(diff:str,snap_vec):
    vec = d2v_model.infer_vector(tokenize(diff))
    cos_distance = spatial.distance.cosine(vec, snap_vec)
    return cos_distance

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

 



d2v_model = Doc2Vec.load('./train/d2v.model')
with open('./pool.tree','rb') as file:          # load the pool
        unpickler = pickle.Unpickler(file)      
        print(unpickler.__str__)
        pool = unpickler.load()
        if __name__ == '__main__':
            main()


