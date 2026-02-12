from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime # Import datetime

class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String, index=True)
    amount = Column(Float, nullable=False)
    date = Column(Date, nullable=False)
    application_date = Column(Date, nullable=False, default=datetime.utcnow) # New field
    movement_type = Column(String, nullable=False) # 'income' or 'expense'
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=True)
    recipient_id = Column(Integer, ForeignKey("recipients.id"), nullable=True)
    is_installment = Column(Boolean, default=False)
    num_installments = Column(Integer, nullable=True)
    installment_amount = Column(Float, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    tenant_id = Column(Integer, ForeignKey("tenants.id"))

    owner = relationship("User")
    tenant = relationship("Tenant")
    category = relationship("Category")
    account = relationship("Account")
    recipient = relationship("Recipient")
