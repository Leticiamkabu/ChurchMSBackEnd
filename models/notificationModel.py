from sqlalchemy import Column, String, UUID, DateTime, func, text
from database.databaseConnection import Base
from sqlalchemy.orm import relationship



class Notification(Base):
    __tablename__ = 'Notification'

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text(
        "uuid_generate_v4()"), unique=True, index=True)
    notificationType = Column(String, nullable=False)
    recipient = Column(String, nullable=False)
    message = Column(String, nullable=False)
    createdOn = Column(DateTime, nullable=True,
                        default=func.current_timestamp())
    updatedOn = Column(DateTime, nullable=True,
                        default=func.current_timestamp())


class ScheduledMessages(Base):
    __tablename__ = 'scheduled_Messages'

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text(
        "uuid_generate_v4()"), unique=True, index=True)
    senderId = Column(String, nullable=False)
    notificationType = Column(String, nullable=False)
    recipient = Column(String, nullable=False)
    message = Column(String, nullable=False)
    sendTime = Column(String, nullable=False)
    messageStatus = Column(String, nullable=False)
    createdOn = Column(DateTime, nullable=True,
                        default=func.current_timestamp())
    updatedOn = Column(DateTime, nullable=True,
                        default=func.current_timestamp())

