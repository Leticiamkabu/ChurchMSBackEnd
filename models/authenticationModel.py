from sqlalchemy import Column, String, UUID, DateTime, func, text
from database.databaseConnection import Base
from sqlalchemy.orm import relationship

# Function to generate a shortened UUID by truncating it to 8 characters


class User(Base):
    __tablename__ = 'Users'

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text(
        "uuid_generate_v4()"), unique=True, index=True)
    firstName = Column(String, nullable=False)
    lastName = Column(String, nullable=False)
    password= Column(String, nullable=False)
    email = Column(String, nullable=True, unique=True)
    phoneNumber = Column(String, nullable=False)
    lastLogedin= Column(String, nullable=True, default="NOT_SET")
    role = Column(String, nullable=True,default="UNIDENTIFIED")
    privileges = Column(String, nullable=True,default="UNIDENTIFIED")
    createdOn = Column(DateTime, nullable=True,
                        default=func.current_timestamp())
    updatedOn = Column(DateTime, nullable=True,
                        default=func.current_timestamp())



    # use it in the profile model
    # user = relationship("User", back_populates="profile")

class UserLoginTracker(Base):
    __tablename__ = 'UserActivities'

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text(
        "uuid_generate_v4()"), unique=True, index=True)
    firstName = Column(String, nullable=False)
    lastName = Column(String, nullable=False)
    status= Column(String, nullable=False)
    role = Column(String, nullable=True, unique=True)
    logInTime = Column(String, nullable=False)
    logOutTime= Column(String, nullable=False)
    userId = Column(String, nullable=False)
    date = Column(String, nullable=False)
    createdOn = Column(DateTime, nullable=False,
                        default=func.current_timestamp())
    updatedOn = Column(String, nullable=True,
                        default="NOT_SET")
