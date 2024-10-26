from sqlalchemy import Column, String, UUID, DateTime, func, text
from database.databaseConnection import Base
from sqlalchemy.orm import relationship


class Attendance(Base):
    __tablename__ = 'attendance'

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text(
        "uuid_generate_v4()"), unique=True, index=True)
    memberID = Column(String, nullable=False)
    fullname = Column(String, nullable=False)
    date = Column(String, nullable=False,)
    status= Column(String, nullable=False)



   
