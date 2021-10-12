import unittest
from controller import VlanController,DatabaseController
from model import Vlan

TEST_CISCO: str = "192.168.0.1"
USERNAME: str = "cisco"
PASSWORD: str = "cisco123456"
VLAN_ID: int = 10
VLAN_NAME: str = "Testing vlan 10"
VLAN_DESCRIPTION: str = "Suitable for testing"
VLAN_ID_2: int = 20
VLAN_NAME_2: str = "Testing vlan 20"
VLAN_DESCRIPTION_2: str = "Suitable for testing 2"
DB_LINK: str = "mariadb+mariadbconnector://user:password@localhost:3306/vlan_db"

class TestVlanController(unittest.TestCase):
    def setUp(self):
        self.target = VlanController(target_cisco=TEST_CISCO,username=USERNAME,password=PASSWORD)

    def test_get_vlans(self):
        self.assertIsInstance(self.target.get_vlans(), dict)
    
    def test_set_vlan(self, vlan=VLAN_ID, name=VLAN_NAME):
        msg = "[OK]"
        self.assertIn(msg,self.target.set_vlan(vlan=VLAN_ID, name=VLAN_NAME))

    def test_delete_vlan(self, vlan=VLAN_ID):
        msg = "[OK]"
        with self.subTest():
            self.assertIn(msg,self.target.delete_vlan(vlan=VLAN_ID))
        with self.subTest():
            self.assertFalse(self.target.delete_vlan(vlan=VLAN_ID))

    def test_update_vlan(self, vlan=VLAN_ID, name=VLAN_NAME):
        msg = "[OK]"
        with self.subTest():
            self.assertFalse(self.target.update_vlan(vlan=VLAN_ID, name=VLAN_NAME))
        with self.subTest():
            self.assertIn(msg,self.target.update_vlan(vlan=VLAN_ID, name=VLAN_NAME))

class TestDatabaseController(unittest.TestCase):
    def setUp(self):
        try:            
            self.target = DatabaseController(db_link=DB_LINK)            
        except Exception as e:
            raise "Can't connect to db, due "+e
    
    def prep_db(self):
        self.target.add_vlan(
            vlan = VLAN_ID,
            name = VLAN_NAME,
            description = VLAN_DESCRIPTION
            )
        self.target.add_vlan(
            vlan = VLAN_ID_2,
            name = VLAN_NAME_2,
            description = VLAN_DESCRIPTION_2
            )
    
    def test_get_vlans(self):
        expected_results = Vlan()
        expected_results.vlan_id = VLAN_ID
        
        results = self.target.get_vlans()
        for i in results:
            if i.vlan_id == 10:
                self.assertEqual(i.vlan_id, expected_results.vlan_id)

    def test_delete_vlan(self):
        self.prep_db()
        self.target.delete_vlan(vlan = VLAN_ID)
        expected_results = Vlan()
        expected_results.vlan_id = VLAN_ID_2

        result = self.target.get_vlans()
        for i in result:
            self.assertEqual(i.vlan_id,expected_results.vlan_id)

    def update_vlan(self):
        self.prep_db()
        self.target.update_vlan(
            vlan = VLAN_ID_2,
            name = "Test case",
            description = "Test case"
        )
        results = self.target.get_vlans()
        for i in results:
            self.assertEqual(i.name, "Test case")


if __name__ == "__main__":
    unittest.main()