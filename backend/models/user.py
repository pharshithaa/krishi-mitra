from pydantic import BaseModel, EmailStr, constr, Field, field_validator
from typing import List
from enum import Enum

class FarmSize(str, Enum):
    SMALL = "small"
    MEDIUM = "medium" 
    LARGE = "large"

class UserCreate(BaseModel):
    # Basic Information
    email: EmailStr
    password: constr(min_length=8)  # enforce via validator for custom message
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

    # --- Validators with user-friendly error messages ---
    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        # At least 8 chars, include letters and numbers
        has_letter = any(c.isalpha() for c in v)
        has_digit = any(c.isdigit() for c in v)
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not has_letter or not has_digit:
            raise ValueError("Password must include both letters and numbers")
        return v

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, v: str) -> str:
        # Allow digits with optional + and spaces/hyphens removed
        digits = ''.join(ch for ch in v if ch.isdigit())
        if len(digits) < 10 or len(digits) > 15:
            raise ValueError("Phone number must have 10-15 digits")
        return v

    @field_validator("pincode")
    @classmethod
    def validate_pincode(cls, v: str) -> str:
        if not v.isdigit() or len(v) != 6:
            raise ValueError("Pincode must be exactly 6 digits")
        return v

    @field_validator("primary_crops")
    @classmethod
    def validate_primary_crops(cls, crops: List[str]) -> List[str]:
        cleaned = [c.strip() for c in crops if c and c.strip()]
        if not cleaned:
            raise ValueError("At least one crop must be provided")
        return cleaned
    
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
