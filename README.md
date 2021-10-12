# Vlan Synchronizer

## About
Small tool that sync the VLAN’s on any given machine with database table. It should be able to sync vlans from Cisco switch.    
We need to have 1 table called VLANS with the below columns:  
 1. ID
 2. NAME  
 3. DESCRIPTION  
  
The application should sync any given Cisco switch VLANS with this table. Below some of the use cases  
  
 1. if new record added to database a new VLAN should be created on the router  
 2. If new VLAN added on the router it should be added to the table  
 3. Same as above for the UPDATE/DELTE
 4. Create VLAN  
  
  
Things we care about:
 
 - [ ] 1- Code quilty  
 - [ ] 2- Unit Testing  
 - [ ] 3- Application design  
 - [ ] 4- Using ORM  
 - [ ] 5- Using database migration framework  
 - [ ] 6- Object Oriented  
 - [ ] 7- Logging  


## How to use

 1. Change DB connection params in `main.py` file.
 2. Change network element target param in `main.py` file.
 3. Use `sync_sw_to_db()` for switch sync to db or `sync_db_to_sw()` for db sync to switch.
 4. Run code `python main.py`

## Test

 1. Change params in `test.py` in test.py file.
 2. Run code `python unittet test.py`

## Requierements

python-dotenv
sqlalchemy
netmiko
unittest
textfsm

### Install python libraries

`pip install requierements.txt`