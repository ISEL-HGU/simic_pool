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
