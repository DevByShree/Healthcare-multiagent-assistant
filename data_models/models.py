import re  # Finding a unique pattern form data ex : shree@1805@gmail.com for regular expression is used 
from pydantic import BaseModel, Field, field_validator # Field i use for applying rules and takin input Base Model means it tells that how we want the data actually from input like we costimize also our data 
# Field means it is ready made rules simple purpose greaterthan(gt),(lt),min_len,max_len etc. but what if we want name?? for findind here fild validor is used 
# Field validator is ofr setting the customize rules like 
class DateTimeModel(BaseModel):
    date:str=Field(description= "Properly formatted date ",pattern =r'^\d{2}-\d{2}-\d{4} \d{2}:\d{2}$') # Date 2 digit month 2 year 4 hour 2 minute 2

    @field_validator("date")
    def check_format_date(cls, v):
        if not re.match(r'^\d{2}-\d{2}-\d{4} \d{2}:\d{2}$',v):
            raise ValueError("The Date should be in format 'DD-MM-YYYY HH:MM'")
        return v

class DateModel(BaseModel):
    date: str = Field(description="Properly formatted data",pattern=r'^\d{2}-\d{2}-\d{4}$')

    @field_validator("date")
    def check_format_date(cls,v):
        if not re.match(r'^\d{2}-\d{2}-\d{4}$',v):
            raise ValueError("The Date must be in Format 'DD-MM-YYYY'")
        return v

class IdentificationNumberModel(BaseModel):
    id: int = Field(description="Identification number (7 or 8 digits long)")

    @field_validator("id")
    def check_format_id(cls,v):
        if not re.match(r'^\d{7,8}$',str(v)):
            raise ValueError("The ID Number should be a 7 or 8 digits long")
        return v






