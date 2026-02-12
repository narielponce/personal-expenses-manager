from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"))
    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True) # New field

    tenant = relationship("Tenant")

    # Many-to-one relationship: a category has one parent
    parent = relationship(
        "Category",
        remote_side=[id], # 'id' column of the target (parent) side
        back_populates="children_categories", # Name of the back-populating relationship on the parent
        foreign_keys=[parent_id] # Explicitly specify the FK column
    )

    # One-to-many relationship: a category has many children
    children_categories = relationship( # Renamed to avoid confusion with children attribute in the model
        "Category",
        back_populates="parent", # Name of the back-populating relationship on the child
        cascade="all, delete-orphan", # Cascade operations (optional, but useful for hierarchy)
        foreign_keys=[parent_id] # Explicitly specify the FK column
    )
