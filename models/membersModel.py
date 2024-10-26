from sqlalchemy import Column, String, UUID, DateTime, func, text
from database.databaseConnection import Base
from sqlalchemy.orm import relationship


class Member(Base):
    __tablename__ = 'members'

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text(
        "uuid_generate_v4()"), unique=True, index=True)
    firstname = Column(String, nullable=False)
    lastname = Column(String, nullable=False)
    othername = Column(String, nullable=False)
    age= Column(String, nullable=False)
    email = Column(String, nullable=True, unique=True)
    phoneNumber = Column(String, nullable=False)
    dateOfBirth= Column(String, nullable=True)
    houseAddress= Column(String, nullable=True,default="UNIDENTIFIED")
    created_on = Column(DateTime, nullable=True,
                        default=func.current_timestamp())



    # use it in the profile model
    # user = relationship("User", back_populates="profile")

