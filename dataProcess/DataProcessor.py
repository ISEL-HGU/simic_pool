
from anytree import AnyNode


class DataProcessor:
    def __init__(self):
        self.trees = []

    def process_line(self, vector, record):

        vector_list = vector.split('|')
        if '' in vector_list:
            vector_list.remove('')
        # print(vector_list[0], record)
        root_exist = False

        for root in self.trees:  
            if vector_list[0] == root.name:
                root_exist = True
                root_found = root
                break
        
        if root_exist is True:
            if len(vector_list) == 1:
                root_found.repo.append(record[0])
                root_found.cpc.append(record[1])
                root_found.pc.append(record[2])
                root_found.file_path.append(record[3])
                root_found.blamed_line(record[4])
                return
            self.position_node(vector_list,record, root_found ,1)

        else:
            self.make_new_tree(vector_list,record)


    def make_new_tree(self, vector_list: list, record: list):
        if len(vector_list) == 1:
            new_node = AnyNode(name=vector_list[0], repo=[record[0]] ,cpc=[record[1]], pc=[record[2]], file_path=[record[3]], blamed_line=[record[4]],  depth=0, parent=None)
        else:
            new_node = AnyNode(name=vector_list[0], repo=[] ,cpc=[], pc=[], file_path=[], blamed_line=[],  depth=0, parent=None)
            self.position_node(vector_list, record, new_node, 1)
        self.trees.append(new_node)
                     

    def position_node(self, vector_list: list, record: list, parent_node: AnyNode, idx: int):
        found = False
        if len(vector_list) == idx:
            parent_node.repo.append(record[0])
            parent_node.cpc.append(record[1])
            parent_node.pc.append(record[2])
            parent_node.file_path.append(record[3])
            parent_node.blamed_line(record[4])
            return

        for child in parent_node.children:          
            if vector_list[idx] == child.name:
                found = True
                self.position_node(vector_list, record, child, idx+1)
                return

        if not found:
            if len(vector_list)-1 == idx:
                new_node = AnyNode(name=vector_list[idx], repo=[record[0]] ,cpc=[record[1]], pc=[record[2]], file_path=[record[3]], blamed_line=[record[4]],  depth=idx, parent=parent_node)
            else:
                new_node = AnyNode(name=vector_list[idx], repo=[] ,cpc=[], pc=[], file_path=[], blamed_line=[],  depth=idx, parent=parent_node)
                # if(idx < len(vector_list)-1):
                self.position_node(vector_list, record, new_node, idx+1)
