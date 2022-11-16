# simic_pool
## pool process for simic extension

This program is a server process that communicates with the jupyterlab extension Simic via TCP.

Run this program separately from jupyter lab

### Before running, please follow the below steps.

1. run the following shell file to clone the repositories.

  `zsh clone.sh`

  or

  `bash clone.sh` depending on your shell

2. download the pool.tree and d2v.model files from the following links.

https://drive.google.com/file/d/1lXitokvyUhdd0BObXdij7n_Idu5OJ5n1/view?usp=share_link

place this file at the project root

https://drive.google.com/file/d/1I_1hhyF5jnN7RQdBzemB0BOw_ywK2Hpq/view?usp=share_link

place this file at simic/train/


3. run

`make build`

for gradle module.

Then finally run

`python3 server.py`

IP and Port statically set for now

## Implementation

Simic in jupyterlab side is composed of FrontEnd and Server Extension (Backend).

Simic Pool is a separate application that TCP communicates with the Simic's Server Extension.

![Screen Shot 2022-11-16 at 5 26 31 PM](https://user-images.githubusercontent.com/83571012/202127805-471d0f80-9c90-4c4a-b1a9-742a5afb706e.png)

Simic Pool is designed to perform 2 main tasks.

### 1. Detreefy

Change Vector collected from 20 ML/DL projects are pickled as a tree data structure.

Meaning that if a vector is 102, each node represents one scalar, namely 1, 0, and 2 as below.
```
1 -- 0 -- 2
   |
    -1 -- 3
   |
    -2 -- 4
```
Simic Pool uses level order traversal for finding an exact match

If it fails to find the exact match, it looks for the closest child node -> sibling node -> parent node, depending on the vector size (not implemented yet)

### 2. Doc2Vec Cosine Similarity

If the found node contains multiple changes, the Simic Pool tokenizes the user input and the data found from the detreefication to compute similarity on a model trained with over 20000 source codes.
