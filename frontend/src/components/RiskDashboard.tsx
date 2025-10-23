
import React, { useEffect, useMemo, useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Thermometer, Droplets, Wind, AlertTriangle, CloudRain } from "lucide-react";
import { Area, AreaChart, ResponsiveContainer, XAxis, YAxis, Tooltip, CartesianGrid } from "recharts";

interface RiskDashboardProps {
  location: string;
}

const weatherData = [
  { day: "Mon", temperature: 32, humidity: 65, rainfall: 0 },
  { day: "Tue", temperature: 30, humidity: 68, rainfall: 0 },
  { day: "Wed", temperature: 31, humidity: 70, rainfall: 5 },
  { day: "Thu", temperature: 29, humidity: 75, rainfall: 15 },
  { day: "Fri", temperature: 28, humidity: 80, rainfall: 8 },
  { day: "Sat", temperature: 30, humidity: 72, rainfall: 0 },
  { day: "Sun", temperature: 33, humidity: 60, rainfall: 0 },
];

// Default fallback crops if user profile missing
const defaultCrops = ["Rice", "Wheat", "Tomato"];

const getRiskColor = (level: number) => {
  if (level < 30) return "bg-green-500";
  if (level < 60) return "bg-yellow-500";
  return "bg-red-500";
};

const WeatherCard: React.FC<{ title: string; value: string; icon: React.ReactNode; className?: string }> = ({ 
  title, value, icon, className 
}) => (
  <Card className={className}>
    <CardContent className="flex items-center p-4">
      <div className="mr-4 text-gray-500">{icon}</div>
      <div>
        <p className="text-sm font-medium text-gray-500">{title}</p>
        <p className="text-2xl font-bold">{value}</p>
      </div>
    </CardContent>
  </Card>
);

const RiskDashboard: React.FC<RiskDashboardProps> = ({ location }) => {
  const API_BASE = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8000";
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [weather, setWeather] = useState<{
    temperature?: number;
    humidity?: number;
    wind_speed?: number;
    rain_1h?: number;
    description?: string;
  } | null>(null);
  const [alerts, setAlerts] = useState<{
    irrigation?: string;
    pest_alert?: string;
    general_tips?: string;
    harvest_tips?: string;
    fertilizer_tips?: string;
    crop_health?: string;
  } | null>(null);
  const [userCrops, setUserCrops] = useState<string[]>([]);

  const { city, state } = useMemo(() => {
    const parts = (location || "").split(",").map((p) => p.trim()).filter(Boolean);
    return { city: parts[0] || "Bengaluru", state: parts[1] };
  }, [location]);

  useEffect(() => {
    const fetchWeather = async () => {
      setLoading(true);
      setError(null);
      try {
        const url = new URL(`${API_BASE}/weather/weather/current`);
        url.searchParams.set("city", city);
        if (state) url.searchParams.set("state", state);
        url.searchParams.set("country", "IN");
        const token = localStorage.getItem("access_token");
        const res = await fetch(url.toString(), {
          headers: {
            Accept: "application/json",
            ...(token ? { Authorization: `Bearer ${token}` } : {}),
          },
        });
        const data = await res.json();
        if (!res.ok) {
          throw new Error(data?.detail || "Failed to fetch weather");
        }
        setWeather(data.weather || null);
        setAlerts(data.farm_alerts || null);
      } catch (e: any) {
        setError(e?.message || "Failed to fetch weather");
      } finally {
        setLoading(false);
      }
    };
    fetchWeather();
  }, [API_BASE, city, state]);

  // Fetch user profile to get primary_crops from backend (MongoDB)
  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const token = localStorage.getItem("access_token");
        if (!token) return;
        const res = await fetch(`${API_BASE}/auth/user/me`, {
          headers: { Accept: "application/json", Authorization: `Bearer ${token}` },
        });
        const data = await res.json();
        if (res.ok && Array.isArray(data?.primary_crops)) {
          setUserCrops(data.primary_crops);
        }
      } catch (e) {
        // ignore profile errors here; UI will fallback
      }
    };
    fetchProfile();
  }, [API_BASE]);

  // Derive crops to display based on user profile; compute a simple risk from weather
  const crops = useMemo(() => {
    const names = (userCrops && userCrops.length > 0) ? userCrops : defaultCrops;
    const temp = weather?.temperature ?? 25;
    const humidity = weather?.humidity ?? 60;
    const rain = weather?.rain_1h ?? 0;
    // Simple heuristic to generate a 0-100 risk value
    const baseRisk = Math.min(100, Math.max(0, (humidity - 40) + (temp > 32 ? (temp - 32) * 2 : 0) + (rain > 5 ? 20 : 0)));
    return names.map((name) => ({
      name,
      riskLevel: Math.round(baseRisk),
      threats: [
        { name: "Weather-related stress", probability: baseRisk > 60 ? "High" : baseRisk > 30 ? "Medium" : "Low", due: `${Math.round(temp)}°C / ${Math.round(humidity)}%` },
      ],
    }));
  }, [userCrops, weather]);

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Current Weather</CardTitle>
            <CardDescription>
              Today's weather conditions in {location}
            </CardDescription>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="text-sm text-gray-500">Loading weather…</div>
            ) : error ? (
              <div className="text-sm text-red-600">{error}</div>
            ) : (
              <div className="grid grid-cols-2 gap-4">
                <WeatherCard 
                  title="Temperature" 
                  value={weather?.temperature !== undefined ? `${Math.round(weather.temperature)}°C` : "-"} 
                  icon={<Thermometer className="w-6 h-6" />} 
                  className="bg-orange-50"
                />
                <WeatherCard 
                  title="Humidity" 
                  value={weather?.humidity !== undefined ? `${Math.round(weather.humidity)}%` : "-"} 
                  icon={<Droplets className="w-6 h-6" />} 
                  className="bg-blue-50"
                />
                <WeatherCard 
                  title="Wind Speed" 
                  value={weather?.wind_speed !== undefined ? `${Math.round(weather.wind_speed)} km/h` : "-"} 
                  icon={<Wind className="w-6 h-6" />} 
                  className="bg-gray-50"
                />
                <WeatherCard 
                  title="Rainfall (1h)" 
                  value={weather?.rain_1h !== undefined ? `${weather.rain_1h} mm` : "0 mm"} 
                  icon={<CloudRain className="w-6 h-6" />} 
                  className="bg-teal-50"
                />
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Weather Forecast</CardTitle>
            <CardDescription>7-day weather prediction</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={200}>
              <AreaChart data={weatherData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                <defs>
                  <linearGradient id="temperatureGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#F59E0B" stopOpacity={0.8}/>
                    <stop offset="95%" stopColor="#F59E0B" stopOpacity={0}/>
                  </linearGradient>
                  <linearGradient id="humidityGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.8}/>
                    <stop offset="95%" stopColor="#3B82F6" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <XAxis dataKey="day" />
                <YAxis />
                <CartesianGrid strokeDasharray="3 3" />
                <Tooltip />
                <Area 
                  type="monotone" 
                  dataKey="temperature" 
                  stroke="#F59E0B" 
                  fillOpacity={1} 
                  fill="url(#temperatureGradient)" 
                />
                <Area 
                  type="monotone" 
                  dataKey="humidity" 
                  stroke="#3B82F6" 
                  fillOpacity={1} 
                  fill="url(#humidityGradient)" 
                />
              </AreaChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Crop Risk Assessment</CardTitle>
          <CardDescription>
            Current risk levels for crops in your area
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-6">
            {crops.map((crop) => (
              <div key={crop.name}>
                <div className="flex justify-between items-center mb-2">
                  <h3 className="font-medium">{crop.name}</h3>
                  <span className="text-sm font-medium">
                    Risk Level: {crop.riskLevel}%
                  </span>
                </div>
                <Progress 
                  value={crop.riskLevel} 
                  className={`h-2 ${getRiskColor(crop.riskLevel)}`} 
                />
                
                <div className="mt-4 bg-gray-50 p-3 rounded-md">
                  <div className="flex items-start gap-2">
                    <AlertTriangle className="w-5 h-5 text-amber-500 mt-0.5" />
                    <div>
                      <h4 className="font-medium text-sm">Potential Threats:</h4>
                      <ul className="mt-1 space-y-1">
                        {crop.threats.map((threat, idx) => (
                          <li key={idx} className="text-sm flex justify-between">
                            <span>{threat.name}</span>
                            <span className="text-gray-500 text-xs">
                              {threat.probability} ({threat.due})
                            </span>
                          </li>
                        ))}
                      </ul>
                      {alerts && (
                        <div className="mt-3">
                          <h4 className="font-medium text-sm">Farm Alerts:</h4>
                          <ul className="mt-1 space-y-1 text-sm text-gray-700">
                            {alerts.irrigation && <li>• {alerts.irrigation}</li>}
                            {alerts.pest_alert && <li>• {alerts.pest_alert}</li>}
                            {alerts.harvest_tips && <li>• {alerts.harvest_tips}</li>}
                            {alerts.fertilizer_tips && <li>• {alerts.fertilizer_tips}</li>}
                            {alerts.general_tips && <li>• {alerts.general_tips}</li>}
                            {alerts.crop_health && <li>• {alerts.crop_health}</li>}
                          </ul>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default RiskDashboard;
