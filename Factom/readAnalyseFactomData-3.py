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
        print ('\n')

    # Wait a little
    print(f'Sleeping for 5 seconds..\n')
    sleep(5)

   
    # Check updated balances
    fct_balance = factomd.factoid_balance(FCT_ADDR)
    ec_balance = factomd.entry_credit_balance(EC_ADDR)
    print(f'Factoshi (FCT*10^(⁻8)) balance: {fct_balance["balance"]}')
    print(f'Entry Credit (EC) balance: {ec_balance["balance"]}\n')
   

    # Initiate some variables
    chain_id =  input("読み込むFactomのchain_id (string) : ")
    entry_hash = None
        
    # 加温 20℃以上    
    upperlimit = 90.0   # Feranheit          
    lowerlimit = 70.0

    try:
        print(f'#### Reading the whole chain:')
        chain_data = factomd.read_chain(chain_id=chain_id)

        # Print result
        print(chain_data)

    except FactomAPIError as e:
        print(e.data)

    # Construct column DB
    counter_list  = []
    temperature_list = []

    print('\n')
    print ('#### Constructing column DB.')
    for content_list_item in chain_data:
        print ('list item: ',  content_list_item)
        content_innerlist = content_list_item['content'].split()
        print ('inner list: ', content_innerlist)

        # entry[0] ='entry_count:'
        # chain[0] !=
        if content_innerlist[0] == 'entry_count:' :
            print('count: ', content_innerlist[1])
            print('high temp: ',  content_innerlist[7], '\n')
            counter_list.append(content_innerlist[1])
            temperature_list.append(content_innerlist[7])
        else:
            break

    print ('\n')
    print('counter list:', counter_list)
    print('temperature list: ', temperature_list)
    print ('\n')

    # Check the value is with the limits
    temperature_max = max(temperature_list)
    temperature_min = min(temperature_list)
    
    if float(temperature_max) <= upperlimit:
        if float(temperature_min) >= lowerlimit:
            print ('####################################################################')
            print ('  Your cargo was maintained within the temperature limits.')
#            print ('      upper limit: ', 4 degree(F), lower limit -2 degree(F)')
            print ('      upper limit: ', upperlimit, ' degree(F), lower limit: ', lowerlimit, ' degree(F)')
            print ('####################################################################')
        else:
            print ('######################################################################')
            print ('Your cargo has some troubles. Exceeded the lowerlimit: ', lowerlimit )
    else:
        print ('######################################################################')
        print ('Your cargo has some troubles. exceeded upper limit: ', upperlimit)

