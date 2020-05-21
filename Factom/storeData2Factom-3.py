#! /usr/bin/env python
# -*- coding: utf-8 -*-

from time import sleep

from factom import Factomd, FactomWalletd
from factom.exceptions import FactomAPIError

def wait_for_entry(entryhash):
    """
    Wait for an entry to be recorded on-chain.
    
    This can be detected by making sure that the entry hash is not present
    in the list of pending entries.
    
    :param str entryhash: the hash of the entry to wait for
    :returns: None
    """

    while True:
        r_pending_entries = factomd.pending_entries()
        if any(entry["entryhash"] == entryhash for entry in r_pending_entries):
#           print('sleeping  entryhash: ', entryhash)
            sleep(1)
        else:
#            sleep(1)
            break

# Wallets, remember to import the FCT address and generate the EC address.
FCT_ADDR = 'FA2jK2HcLnRdS94dEcU27rF3meoJfpUcZPSinpb7AwQvPRY6RL1Q'
EC_ADDR = 'EC1yXtGdZSyYD4yVLhuwSJqfGV4Gph2cSth8QuWCWJ3VQxydYy8c'

if __name__ == "__main__":
    # Default params
    walletd = FactomWalletd()
    
    # You can also specify fct and ec addresses, change host, or specify RPC credentials, for example:
    factomd = Factomd(host='http://localhost:8088',
                      fct_address=FCT_ADDR,
                      ec_address=EC_ADDR)

#                      ec_address=EC_ADDR,
#                      username='rpc_username',
#                      password='rpc_password')
                        
    # Check balance on wallets
    fct_balance = factomd.factoid_balance(FCT_ADDR)
    ec_balance = factomd.entry_credit_balance(EC_ADDR)
    print(f'\n Factoshi (FCT*10^(⁻8)) balance: {fct_balance["balance"]}')
    print(f'Entry Credit (EC) balance: {ec_balance["balance"]}\n')
    
    # Check entry credit rate
    ec_rate = factomd.entry_credit_rate()
    
    # Print result
    print(f'Entry credit rate is: {ec_rate["rate"]} Factoshis')
    
    # Purchase some entry credits with our imported FCT wallet if our EC balance is less than 20.
    if ec_balance['balance'] < 20:
        print('Balance is less than 20 Entry Credits, purchasing 50 more.')
        fct_to_ec = walletd.fct_to_ec(factomd, 50000, fct_address=FCT_ADDR, ec_address=EC_ADDR)
        
        # Print result
        print(fct_to_ec)
    
    # Wait a little
    print(f'Sleeping for 5 seconds..\n')
    sleep(5)

    
    # Check updated balances
    fct_balance = factomd.factoid_balance(FCT_ADDR)
    ec_balance = factomd.entry_credit_balance(EC_ADDR)
    print(f'Factoshi (FCT*10^(⁻8)) balance: {fct_balance["balance"]}')
    print(f'Entry Credit (EC) balance: {ec_balance["balance"]}\n')
    
    # Initiate some variables
    new_chain = None
    chain_id = None
    entry_hash = None
   

    # Chain Name
    chain_content = input("作成するChainのcontent (string) : ")
    user_input    = input("ext ids (list 複数の単語): ")
    chain_ext_ids = user_input.split()

    print('chain content: ', chain_content)
    print('chain ext_ids: ', chain_ext_ids)
    print(type(chain_ext_ids), 'CONVERTED!')

    read_file = input("readするfile name: ")
    print (read_file)


    
    # Create new chain!
    # The cost of creating a new chain is 10 ECs.
    try:
        new_chain = walletd.new_chain(factomd=factomd,
                                      ext_ids= chain_ext_ids,
                                      content= chain_content,
                                      ec_address=EC_ADDR)
                                        
        # Store chain ID and entry hash
        chain_id = new_chain['chainid']
        entry_hash = new_chain['entryhash']
        
        # Print result
        print(f'#### New chain created with chain ID: {chain_id} and entry hash: {entry_hash}')
        
        print('      Waiting for the newly created chain to appear on the blockchain')
        # Wait for the new chain to appear on the blockchain
        wait_for_entry(entryhash=entry_hash)
        
    except FactomAPIError as e:
        print(f'{e.data}.\n')
        # If chain already exists retrieve the chainid.
        chain_id = e.data.split()[1]


    # read file & add an entry
    try:
        myfile = open(read_file)
                
    except OSError as e:
        print(e)

    else:
        try:
            for count, line in enumerate(myfile):
                linelist = line.split(',')

# ここでcontentを編集
                elm_date = linelist[0]
                elm_time = linelist[1]
                elm_temperature = linelist[2]  # temperature のみ

                print('\n')
                print(f'"read a record " {count}: {linelist}')
   
                '''
                entry content は　'entry_content': 'entry_count: 2 date: 2019/10/01 time: 11:02 temperature: 83.9'
                             　　すなわち 'entry_count: ' + str(count) + ' date: ' + elm_date + ' time: ' + elm_time + ' temperature: ' + elm_temperature
                で書き込む。空白に注意。

                      factomd.read_chain(chain_id=chain_id)　ー＞　chain_data
                で読み込み、
                  for content_list_item in chain_data:
                　　　。。。
                    if content_innerlist[0] == 'entry_count:'
                でentryのみ拾い上げる    
                '''

                entry_content = 'entry_count: '+ str(count) + ' date: ' + elm_date + ' time: ' + elm_time + ' temperature: ' + elm_temperature 
                print('entry content: ', entry_content)
                
                # ext_idsも編集可能
                entry_ext_ids = ['Time', 'series', 'entry' ]      
                print('entry ext_ids: ', entry_ext_ids)

                # Create a new entry in the chain created above using the chainid
                new_entry = None
                try:    
                    print(f'#### Creating a new entry to the chain with chain ID: {chain_id}.')
                    new_entry = walletd.new_entry(factomd=factomd,
                                      chain_id=chain_id,
                                      ext_ids= entry_ext_ids,
                                      content= entry_content,
                                      ec_address=EC_ADDR)
                    # Print result
                    print(f'{new_entry}')
                    
                except FactomAPIError as e:
                    print(e.data)

                # wait
                print('      Waiting for the newly created entry to appear on the blockchain')
                entry_hash2 = new_entry['entryhash']
                wait_for_entry(entryhash=entry_hash2)

                # Read the whole chain including the entries
                sleep(10)        # additional sleep
                
                chain_data = None
                try:
                    print('\n')
                    print(f'#### Reading the whole chain:')
                    chain_data = factomd.read_chain(chain_id=chain_id)
        
                    # Print result
                    print(chain_data)
        
                except FactomAPIError as e:    
                    print(e.data)
       

        # file read error
        except Exception as e:
            print(e)

    finally:
        myfile.close()

# どのくらい　追加で待てば良いか？
#i    counter=0           
#    while counter<10:
#        sleep(5)
#        counter += 1
#        sleeping_time= 5 * counter
#        print('sleeping: ', sleeping_time)
#        chain_data = factomd.read_chain(chain_id=chain_id)
#        print(chain_data)




