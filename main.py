from controller import VlanController, DatabaseController
import logging
from datetime import date


TEST_CISCO: str = "192.168.0.1"
USERNAME: str = "cisco"
PASSWORD: str = "cisco123456"
VLAN_ID: int = 40
VLAN_NAME: str = "Testing vlan"
DB_LINK: str = "mariadb+mariadbconnector://user:password@localhost:3306/vlan_db"

def sync_db_to_sw():    
    db = DatabaseController(db_link=DB_LINK)
    sw = VlanController(target_cisco=TEST_CISCO,username=USERNAME,password=PASSWORD)

    vlans_sw = sw.get_vlans()
    vlans_db = db.get_vlans()

    vlan_db_backup = []

    for vlan_db in vlans_db:
        try:
            index = vlans_sw["VLAN"].index(str(vlan_db.vlan_id))
        except ValueError:
            index = -1

        if index == -1:
            sw.set_vlan(
                vlan = vlan_db.vlan_id,
                name = vlan_db.name
            )
        elif vlans_sw["NAME"][index] != vlan_db.name:
            sw.update_vlan(
                vlan = vlan_db.vlan_id,
                name = vlan_db.name
            )

        vlan_db_backup.append(str(vlan_db.vlan_id))

    for vlan_sw in vlans_sw["VLAN"]:
        if vlan_sw not in vlan_db_backup:
            sw.delete_vlan(vlan = int(vlan_sw))

    
def sync_sw_to_db():
    db = DatabaseController(db_link=DB_LINK)
    sw = VlanController(target_cisco=TEST_CISCO,username=USERNAME,password=PASSWORD)
    
    vlans_sw = sw.get_vlans()
    vlans_db = db.get_vlans()

    vlan_db_backup = []
    
    for vlan_db in vlans_db:
        try:    
            index = vlans_sw["VLAN"].index(str(vlan_db.vlan_id))
        except ValueError:
            index = -1

        if index == -1:
            db.delete_vlan(
                vlan = vlan_db.vlan_id
                )
        elif vlans_sw["NAME"][index] != vlan_db.name:
            db.update_vlan(
                vlan = vlan_db.vlan_id,
                name = vlans_sw["NAME"][index],
                description = "Updated from cisco"
            )
        vlan_db_backup.append(str(vlan_db.vlan_id))

    for vlan_sw,name_sw in zip(vlans_sw["VLAN"],vlans_sw["NAME"]):
        if vlan_sw not in vlan_db_backup:
            db.add_vlan(
                vlan = vlan_sw,
                name = name_sw,
                description = "Added from cisco"
            )

if __name__ == '__main__':

    today = date.today()
    logging.basicConfig(
        level=logging.INFO, 
        format='%(asctime)s::%(levelname)s::%(name)s::%(message)s', 
        filename=f'logs/{today.strftime("%m-%d-%Y")}.log', 
        encoding='utf-8'
        )

    try:
        #sync_db_to_sw()
        sync_sw_to_db()
        logging.info("Sync success")
    except:
        logging.critical("Sync fails")
        raise "Sync error"