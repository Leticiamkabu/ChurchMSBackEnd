from sqlalchemy import Column, String, UUID, DateTime, func, text
from database.databaseConnection import Base
from sqlalchemy.orm import relationship

# Function to generate a shortened UUID by truncating it to 8 characters
def generate_short_uuid():
    return str(uuid.uuid4())[:8]

class User(Base):
    __tablename__ = 'Users'

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text(
        "uuid_generate_v4()"), unique=True, index=True)
    firstname = Column(String, nullable=False)
    lastname = Column(String, nullable=False)
    password= Column(String, nullable=False)
    email = Column(String, nullable=True, unique=True)
    phoneNumber = Column(String, nullable=False)
    lastLogedin= Column(String, nullable=True, default="NOT_SET")
    role = Column(String, nullable=True,default="UNIDENTIFIED")
    privileges = Column(String, nullable=True,default="UNIDENTIFIED")
    created_on = Column(DateTime, nullable=True,
                        default=func.current_timestamp())



    # use it in the profile model
    # user = relationship("User", back_populates="profile")

