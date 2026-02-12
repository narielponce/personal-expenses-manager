from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from database import Base

class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    is_credit_card = Column(Boolean, default=False) # New field
    tenant_id = Column(Integer, ForeignKey("tenants.id"))

    tenant = relationship("Tenant")
