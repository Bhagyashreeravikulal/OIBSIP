import tkinter as tk
from tkinter import messagebox
import requests
from PIL import Image, ImageTk
import io
import geocoder
import datetime

# ------------------- CONFIGURATION ------------------- #

API_KEY = "YOUR_API_KEY"
BASE_URL = "https://api.openweathermap.org/data/2.5/"

# ------------------- MAIN APPLICATION CLASS ------------------- #

class WeatherApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Weather Application")
        self.root.geometry("600x620")
        self.root.resizable(False, False)

        self.unit = "metric"   # Default: Celsius

        self.create_widgets()

    # ------------------- UI DESIGN ------------------- #

    def create_widgets(self):

        self.title_label = tk.Label(
            self.root,
            text="Weather Application",
            font=("Arial", 20, "bold")
        )
        self.title_label.pack(pady=15)

        self.city_entry = tk.Entry(
            self.root,
            width=30,
            font=("Arial", 12)
        )
        self.city_entry.pack(pady=10)

        self.search_button = tk.Button(
            self.root,
            text="Get Weather",
            command=self.get_weather
        )
        self.search_button.pack(pady=5)

        self.location_button = tk.Button(
            self.root,
            text="Use Current Location",
            command=self.get_location_weather
        )
        self.location_button.pack(pady=5)

        self.unit_button = tk.Button(
            self.root,
            text="Toggle °C / °F",
            command=self.toggle_unit
        )
        self.unit_button.pack(pady=5)

        self.forecast_button = tk.Button(
            self.root,
            text="5-Day Forecast",
            command=self.get_forecast
        )
        self.forecast_button.pack(pady=5)

        self.icon_label = tk.Label(self.root)
        self.icon_label.pack(pady=10)

        self.result_label = tk.Label(
            self.root,
            text="",
            font=("Arial", 12),
            justify="left"
        )
        self.result_label.pack(pady=10)

    # ------------------- API REQUEST FUNCTION ------------------- #

    def fetch_weather_data(self, endpoint, parameters):
        try:
            response = requests.get(BASE_URL + endpoint, params=parameters)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            messagebox.showerror("API Error", str(e))
            return None

    # ------------------- CURRENT WEATHER ------------------- #

    def get_weather(self):
        city = self.city_entry.get()

        if not city:
            messagebox.showwarning("Input Error", "Please enter a city name.")
            return

        parameters = {
            "q": city,
            "appid": API_KEY,
            "units": self.unit
        }

        data = self.fetch_weather_data("weather", parameters)

        if data:
            self.display_weather(data)

    # ------------------- GPS LOCATION WEATHER ------------------- #

    def get_location_weather(self):
        g = geocoder.ip('me')

        if g.ok:
            latitude, longitude = g.latlng

            parameters = {
                "lat": latitude,
                "lon": longitude,
                "appid": API_KEY,
                "units": self.unit
            }

            data = self.fetch_weather_data("weather", parameters)

            if data:
                self.display_weather(data)
        else:
            messagebox.showerror("Location Error", "Unable to detect location.")

    # ------------------- DISPLAY WEATHER ------------------- #

    def display_weather(self, data):
        try:
            city = data["name"]
            temperature = data["main"]["temp"]
            humidity = data["main"]["humidity"]
            description = data["weather"][0]["description"]
            wind_speed = data["wind"]["speed"]
            icon_code = data["weather"][0]["icon"]

            unit_symbol = "°C" if self.unit == "metric" else "°F"

            weather_info = (
                f"City: {city}\n"
                f"Temperature: {temperature}{unit_symbol}\n"
                f"Humidity: {humidity}%\n"
                f"Condition: {description}\n"
                f"Wind Speed: {wind_speed} m/s\n"
                f"Updated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )

            self.result_label.config(text=weather_info)
            self.display_icon(icon_code)

        except KeyError:
            messagebox.showerror("Data Error", "Error processing weather data.")

    # ------------------- WEATHER ICON DISPLAY ------------------- #

    def display_icon(self, icon_code):
        icon_url = f"http://openweathermap.org/img/wn/{icon_code}@2x.png"

        try:
            response = requests.get(icon_url)
            image_bytes = response.content
            image = Image.open(io.BytesIO(image_bytes))
            photo = ImageTk.PhotoImage(image)

            self.icon_label.config(image=photo)
            self.icon_label.image = photo
        except:
            pass

    # ------------------- 5 DAY FORECAST ------------------- #

    def get_forecast(self):
        city = self.city_entry.get()

        if not city:
            messagebox.showwarning("Input Error", "Enter city first.")
            return

        parameters = {
            "q": city,
            "appid": API_KEY,
            "units": self.unit
        }

        data = self.fetch_weather_data("forecast", parameters)

        if data:
            forecast_text = "\n5-Day Forecast:\n\n"

            for item in data["list"][::8][:5]:
                date = item["dt_txt"].split()[0]
                temp = item["main"]["temp"]
                desc = item["weather"][0]["description"]

                forecast_text += f"{date} - {temp}° - {desc}\n"

            self.result_label.config(text=forecast_text)

    # ------------------- UNIT TOGGLE ------------------- #

    def toggle_unit(self):
        self.unit = "imperial" if self.unit == "metric" else "metric"

        unit_name = "Fahrenheit" if self.unit == "imperial" else "Celsius"

        messagebox.showinfo("Unit Changed", f"Now using {unit_name}")

# ------------------- MAIN PROGRAM ------------------- #

if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherApp(root)
    root.mainloop()
