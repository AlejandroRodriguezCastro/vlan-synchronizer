from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String


Base = declarative_base()

class Vlan(Base):
    __tablename__ = 'vlans'

    id = Column(Integer(), primary_key=True)
    vlan_id = Column(Integer(), unique=True)
    name = Column(String(20), nullable=True)
    description = Column(String(50), nullable=True)