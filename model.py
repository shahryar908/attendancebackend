from pydantic import BaseModel,EmailStr,Field


class signupreq(BaseModel):
   name:str
   email:EmailStr
   password:str=Field(...,min_lenght=6)
   role:str=Field(...,pattern="^(student|teacher)$")

class userlogin(BaseModel):
   email:EmailStr
   password:str=Field(...,min_length=6)

class userloginres(BaseModel):
   _id:str
   name:str
   email:EmailStr
   role:str

class CreateClassRequest(BaseModel):
   className:str

class AddStudentRequest(BaseModel):
   studentId:str

class attendancestartReq(BaseModel):
   classId:str