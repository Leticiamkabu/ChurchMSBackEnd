from sqlalchemy import Column, String, UUID, DateTime, func, text
from database.databaseConnection import Base
from sqlalchemy.orm import relationship


class Member(Base):
    __tablename__ = 'members'

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text(
        "uuid_generate_v4()"), unique=True, index=True)
    memberID = Column(String, nullable=False)
    title = Column(String, nullable=False)
    firstName = Column(String, nullable=False)
    middleName = Column(String, nullable=False)
    lastName = Column(String, nullable=False)
    dateOfBirth = Column(String, nullable=False)
    age = Column(String, nullable=False)
    gender= Column(String, nullable=False)
    phoneNumber = Column(String, nullable=True, unique=True)
    email = Column(String, nullable=False)
    nationality= Column(String, nullable=True)
    homeTown= Column(String, nullable=True)
    homeAddress = Column(String, nullable=False)
    town = Column(String, nullable=False)
    workingStatus = Column(String, nullable=False)
    occupation = Column(String, nullable=False)
    educationalLevel = Column(String, nullable=False)
    highestEducation = Column(String, nullable=False)
    mothersName = Column(String, nullable=False)
    fathersName= Column(String, nullable=False)
    nextOfKin = Column(String, nullable=False)
    nextOfKinPhoneNumber = Column(String, nullable=False)
    maritalStatus = Column(String, nullable=False)
    spouseContact = Column(String, nullable=False)
    spouseName = Column(String, nullable=False)
    numberOfChildren = Column(String, nullable=False)
    memberType = Column(String, nullable=False)
    cell = Column(String, nullable=False)
    departmentName = Column(String, nullable=False)
    dateJoined = Column(String, nullable=False)
    classSelection = Column(String, nullable=False)
    spiritualGift = Column(String, nullable=False)
    position = Column(String, nullable=False)
    waterBaptised = Column(String, nullable=False)
    baptisedBy= Column(String, nullable=False)
    dateBaptised = Column(String, nullable=False)
    baptisedByTheHolySpirit = Column(String, nullable=False)
    memberStatus = Column(String, nullable=False)
    dateDeceased = Column(String, nullable=True)
    dateBuried = Column(String, nullable=True)
    confirmed = Column(String, nullable=False)
    dateConfirmed = Column(String, nullable=False)
    comment = Column(String, nullable=False)

    createdOn = Column(DateTime, nullable=True,
                        default=func.current_timestamp())
    updatedOn = Column(DateTime, nullable=True,
                        default=func.current_timestamp())




class MemberImage(Base):
    __tablename__ = 'member_image'

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text(
        "uuid_generate_v4()"), unique=True, index=True)
    fullName = Column(String,nullable=False)
    image = Column(String, nullable=True)  # Column to store binary image data
    imageFileName = Column(String, nullable=True)
    createdOn = Column(DateTime, nullable=True,
                        default=func.current_timestamp())
    updatedOn = Column(DateTime, nullable=True,
                        default=func.current_timestamp())


    # use it in the profile model
    # user = relationship("User", back_populates="profile")




    
