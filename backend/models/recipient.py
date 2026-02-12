from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Recipient(Base):
    __tablename__ = "recipients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"))

    tenant = relationship("Tenant")
