from sqlalchemy import Column, String, UUID, DateTime, func, text
from database.databaseConnection import Base
from sqlalchemy.orm import relationship



class FirstTimers(Base):
    __tablename__ = 'FirstTimers'

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text(
        "uuid_generate_v4()"), unique=True, index=True)
    name = Column(String, nullable=False)
    popularName = Column(String, nullable=False)
    phoneNumber = Column(String, nullable=False)
    whatsAppNumber = Column(String, nullable=False)
    houseLocation = Column(String, nullable=False)
    purposeOfComing = Column(String, nullable=False)
    contactHours = Column(String, nullable=False)
    specialPrayerOrCounseling = Column(String, nullable=False)
    counselor = Column(String, nullable=False)
    date = Column(String, nullable=False)
    status = Column(String, nullable=False)
    createdOn = Column(DateTime, nullable=True,
                        default=func.current_timestamp())
    updatedOn = Column(DateTime, nullable=True,
                        default=func.current_timestamp())


class ScheduledMessages(Base):
    __tablename__ = 'scheduled_Messages'

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text(
        "uuid_generate_v4()"), unique=True, index=True)
    notificationType = Column(String, nullable=False)
    recipient = Column(String, nullable=False)
    message = Column(String, nullable=False)
    sendTime = Column(String, nullable=False)
    messageStatus = Column(String, nullable=False)
    createdOn = Column(DateTime, nullable=True,
                        default=func.current_timestamp())
    updatedOn = Column(DateTime, nullable=True,
                        default=func.current_timestamp())


