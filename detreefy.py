from dataProcess.DataProcessor import DataProcessor

def traverse_tree(static, parsed_script):
    found_node = None

    for root in static.trees:
        if parsed_script[0] == root.name:
            if len(root.children) == 0 or len(parsed_script) == 1:
                return root
            else:
                found_node = traverse_tree_recur(root,parsed_script)
                break
    
    return found_node

def traverse_tree_recur(root,parsed_script):
    children = root.children
    if len(children) > 0:
        for node in children:
            if parsed_script[node.depth] == node.name:
                if len(parsed_script) == node.depth+1:
                    return node
                return traverse_tree_recur(node,parsed_script)
            
        return None

def detreefy(static:any, edit_script: str):
     #When API rquest comes
    parsed_script = edit_script.split('|')
    if '' in parsed_script:
        parsed_script.remove('')
    node = traverse_tree(static,parsed_script)

    #Search Results
    matches = []
    if node is None or len(node.repo) == 0:
        print('exact match not found!')
        return None
    else:
        print(str(len(node.repo)) + ' exact matches found' + '\n')
        for i in range (0,len(node.repo)):
            print(node.repo[i] + '\t' + node.cpc[i] + '\t' + node.pc[i] + '\t' + node.file_path[i] + '\t' + node.blamed_line[i] + '\n')
            matches.append([node.repo[i], node.cpc[i], node.pc[i], node.file_path[i], node.blamed_line[i]])
        return matches, len(node.repo)