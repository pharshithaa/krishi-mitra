from pydantic import BaseModel, EmailStr, constr, Field
from typing import List
from enum import Enum

class FarmSize(str, Enum):
    SMALL = "small"
    MEDIUM = "medium" 
    LARGE = "large"

class UserCreate(BaseModel):
    # Basic Information
    email: EmailStr
    password: constr(min_length=6)
    full_name: str = Field(..., min_length=2, max_length=100)
    phone_number: str = Field(..., min_length=10, max_length=15)
    
    # Location Information
    state: str = Field(..., min_length=2, max_length=50)
    district: str = Field(..., min_length=2, max_length=50)
    village: str = Field(..., min_length=2, max_length=100)
    pincode: str = Field(..., min_length=6, max_length=6)
    
    # Farming Information
    farm_size: FarmSize
    primary_crops: List[str] = Field(..., min_items=1, max_items=10)
    
class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    message: str
    email: EmailStr
    full_name: str

class UserInfoResponse(BaseModel):
    email: EmailStr
    full_name: str
    phone_number: str
    primary_crops: List[str]
    farm_size: str
