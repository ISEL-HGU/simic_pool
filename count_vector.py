import anytree
import pickle

def main():
    pool = None
    count = {}
    with open('./pool.tree','rb') as file:          # load the pool
        unpickler = pickle.Unpickler(file) 
        pool = unpickler.load()
    for root in pool.trees:
        levels = [[node.repo for node in children] for children in anytree.ZigZagGroupIter(root)]
        for level in levels:
            for repo in level:
                cache = set()            
                for r in repo:
                    if r not in count.keys() and r != []:
                        count[r] = 1
                    elif r != [] and r not in cache:
                        count[r] += 1
                    cache.add(r)
    print(count)

if __name__ == '__main__':
    main()


