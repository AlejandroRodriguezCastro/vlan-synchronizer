from netmiko import ConnectHandler
import textfsm
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from model import Base,Vlan
import logging

PARSER: str = 'parser.fsm'

class VlanController():
    def __init__(self,target_cisco,username,password,port_ssh=22):
        self.logger_sw = logging.getLogger("SW") 
        try:
            self.connection = ConnectHandler(
                                                ip = target_cisco,
                                                port = port_ssh,
                                                username = username,
                                                password = password,
                                                device_type = "cisco_ios",
            )
            self.logger_sw.info("Connected to SW...")
        except Exception as error:
            self.logger_sw.critical("An unknown error occured: ",error)
            raise Exception("An unknown error occured: ",error)


    def _vlan_parser(self,parser_location,output):
        try:
            with open(parser_location) as parser_template:
                re_template = textfsm.TextFSM(parser_template)
                fsm_result = re_template.ParseText(output)            
            return fsm_result
        except Exception as error:
            self.logger_sw.critical(f"An unknown error occured while parsing: {error}.")
            raise Exception("An unknown error occured: ",error)

    def _vlan_in_target(self, vlan):
        for element in self.get_vlans():
            if str(vlan) in element:
                return True
        return False        

    def get_vlans(self):
        commands = ["show vlan brief"]
        try:
            output = self.connection.send_command(commands)
            vlan_dict = {"VLAN": [],"NAME": []}
            for vlan in self._vlan_parser(parser_location = PARSER,output = output):
                vlan_dict["VLAN"].append(vlan[0])
                vlan_dict["NAME"].append(vlan[1])
            self.logger_sw.info("Vlans adquired.")
            return vlan_dict
        except Exception as error:
            self.logger_sw.critical(f"An unknown error occured while getting vlanss: {error}.")
            raise Exception("An unknown error occured: ",error)
    
    def set_vlan(self, vlan, name=''):
        commands = [f"vlan {vlan}",f"name {name}"]
        try:
            if self._vlan_in_target(vlan):
                return False
            output = self.connection.send_config_set(commands)
            output += self.connection.save_config()
            self.logger_sw.info("Vlan configured.")
            return output
        except Exception as error:
            self.logger_sw.critical(f"An unknown error occured while configure vlan: {error}.")
            raise Exception("An unknown error occured: ",error)

    def delete_vlan(self, vlan):
        commands = [f"no vlan {vlan}"]
        try:
            if not self._vlan_in_target(vlan):
                return False
            output = self.connection.send_config_set(commands)
            output += self.connection.save_config()
            self.logger_sw.info("Vlan deleted.")
            return output
        except Exception as error:
            self.logger_sw.critical(f"An unknown error occured while deleting vlan: {error}.")
            raise Exception("An unknown error occured: ",error)        

    def update_vlan(self, vlan, name=''):
        commands = [f"vlan {vlan}",f"name {name}"]
        try:
            if not self._vlan_in_target(vlan):
                return False
            output = self.connection.send_config_set(commands)
            output += self.connection.save_config()
            self.logger_sw.info("Vlan updated.")
            return output
        except Exception as error:
            self.logger_sw.critical(f"An unknown error occured while updating vlan: {error}.")
            raise Exception("An unknown error occured: ",error)
        
    def disconnect(self):
        self.logger_sw.info("SW disconnected")
        self.connection.disconnect()

class DatabaseController():
    def __init__(self,db_link):
        try:
            self.engine = create_engine(db_link)
            Session = sessionmaker(self.engine)        
            self.session = Session()     
            Base.metadata.create_all(self.engine)
            self.logger_db = logging.getLogger("DB") 
            self.logger_db.info("Connected to DB...")
        except Exception as e:
            self.logger_db.critical("Can't connect to DB")
            raise Exception("An unknown error occured: ",e)

    def add_vlan(self, vlan, name, description):
        try:
            self.session.query(Vlan).filter(
                Vlan.vlan_id == vlan
            ).one()
            self.logger_db.warning(f"Vlan {vlan} already added.")
        except NoResultFound:
            self.session.add(Vlan(
                    vlan_id=vlan, 
                    name=name, 
                    description = description
                    ))
            self.session.commit()
            self.logger_db.info(f"Registry {vlan} added.")
        except Exception as error:
            self.logger_db.critical(f"An unknown error occured: {error}. Vlan {vlan}.")
            return -1

    def get_vlans(self):
        try:
            self.logger_db.info("DB query all on DB.")
            return self.session.query(Vlan)
        except Exception as error:
            self.logger_db.critical(f"An unknown error occured: {error}.")
            return -1

    def delete_vlan(self, vlan):
        try:
            self.session.query(Vlan).filter(
                Vlan.vlan_id == vlan
                ).delete()
            self.session.commit()
            self.logger_db.info(f"Registry {vlan} deleted.")
        except NoResultFound:
            self.logger_db.warning(f"Vlan {vlan} not found.")
            return False
        except Exception as error:
            self.logger_db.critical(f"An unknown error occured: {error}. Vlan {vlan}.")
            return -1

    def update_vlan(self, vlan, name="", description=""):
        try:
            self.session.query(Vlan).filter(
                Vlan.vlan_id == vlan
                ).update(
                    {Vlan.name: name, Vlan.description: description}
                )
            self.logger_db.info(f"Vlan {vlan} updated.")    
        except NoResultFound:
            self.logger_db.warning(f"Vlan {vlan} not found.")
            return False
        except Exception as error:
            self.logger_db.critical(f"An unknown error occured: {error}. Vlan {vlan}.")
            return -1