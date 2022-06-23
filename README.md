# nfd_cli.py
Requirements:

  - Python 3.10
  - py-algorand-sdk

Description:
This is my amatuerish attempt at replicating patrick.algo's go NFD lookup example in Python. This will take an input (ex. iscrectu.algo) and output the NFD AppID and the current owner's wallet address. 

Please be warned this is a work in progress and you should not run this if you do not understand what you are doing!


You can run by using the following command:
    
    python3 nfd_cli.py -n iscrectu.algo 

It will output something similar to following:

    nfdAppID: 766057725
    current owner: RSGDE....LRYKU
