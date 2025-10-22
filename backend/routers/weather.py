from fastapi import APIRouter, HTTPException, Depends, Query
from routers.auth import get_current_user
from services.weather import get_weather_by_location, get_weather, generate_farm_alerts

router = APIRouter()

@router.get("/weather")
def get_weather_for_user(current_user: dict = Depends(get_current_user)):
    """Get weather for user's registered location with farm alerts"""
    city = current_user.get("village")  # Using village as default city
    state = current_user.get("state")
    
    if not city:
        raise HTTPException(status_code=400, detail="Location not set for user")
    
    try:
        weather = get_weather_by_location(city, state)
        
        # Create farm data from user profile
        farm_data = {
            "soil_moisture": 50,  # Default value, could be from user profile
            "crop_type": current_user.get("primary_crops", ["generic"])[0] if current_user.get("primary_crops") else "generic",
            "farm_size": current_user.get("farm_size", "medium"),
            "recent_rainfall": 0  # Default value, could be from weather history
        }
        
        alerts = generate_farm_alerts(weather, farm_data)
        
        return {
            "location": {"city": city, "state": state},
            "weather": weather,
            "farm_alerts": alerts,
            "farm_data": farm_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/weather/current")
def get_weather_by_city(
    city: str = Query(..., min_length=2, max_length=100, description="City name for weather info"),
    state: str = Query(None, min_length=2, max_length=100, description="State name (optional)"),
    country: str = Query("IN", min_length=2, max_length=2, description="Country code (default: IN)"),
    soil_moisture: int = Query(50, ge=0, le=100, description="Soil moisture percentage (0-100)"),
    crop_type: str = Query("generic", min_length=2, max_length=50, description="Type of crop being grown")
):
    """Get weather for any specific location with farm alerts using real rainfall data"""
    try:
        weather = get_weather(city, state, country)
        
        # Create farm data from query parameters (rainfall data comes from weather API)
        farm_data = {
            "soil_moisture": soil_moisture,
            "crop_type": crop_type,
            "farm_size": "medium",  # Default value
            # recent_rainfall is now automatically calculated from weather API data
        }
        
        alerts = generate_farm_alerts(weather, farm_data)
        
        return {
            "location": {"city": city, "state": state, "country": country},
            "weather": weather,
            "farm_alerts": alerts
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
