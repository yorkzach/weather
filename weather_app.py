import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel, QCheckBox, QListWidget, QListWidgetItem
from PyQt5.QtCore import Qt
import json
import os
from weather import build_weather_query, get_weather_data
import style

STORAGE_FILE = 'weather_cities.json'

class WeatherApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Weather App")
        self.setGeometry(100, 100, 400, 300)
        
        self.layout = QVBoxLayout()
        
        self.input_layout = QHBoxLayout()
        self.input_field = QLineEdit(self)
        self.input_field.setPlaceholderText("Enter city name")
        self.imperial_checkbox = QCheckBox("Imperial", self)
        self.fetch_button = QPushButton("Fetch Weather", self)
        
        self.input_layout.addWidget(self.input_field)
        self.input_layout.addWidget(self.imperial_checkbox)
        self.input_layout.addWidget(self.fetch_button)
        
        self.layout.addLayout(self.input_layout)
        
        self.weather_list = QListWidget(self)
        self.layout.addWidget(self.weather_list)
        
        self.clear_button = QPushButton("Clear Selected", self)
        self.layout.addWidget(self.clear_button)
        
        self.fetch_button.clicked.connect(self.fetch_weather)
        self.clear_button.clicked.connect(self.clear_selected_weather)
        
        self.setLayout(self.layout)
        
        self.cities = self.load_cities()
        self.update_weather_list()
    
    def load_cities(self):
        if os.path.exists(STORAGE_FILE):
            with open(STORAGE_FILE, 'r') as f:
                return json.load(f)
        return []
    
    def save_cities(self):
        with open(STORAGE_FILE, 'w') as f:
            json.dump(self.cities, f)
    
    def fetch_weather(self):
        city = self.input_field.text().split()
        imperial = self.imperial_checkbox.isChecked()
        if city:
            query_url = build_weather_query(city, imperial)
            weather_data = get_weather_data(query_url)
            self.add_city(weather_data, imperial)
    
    def add_city(self, weather_data, imperial):
        city_name = weather_data["name"]
        if any(city["name"] == city_name for city in self.cities):
            return
        
        city_info = {
            "name": city_name,
            "imperial": imperial,
            "weather_data": weather_data
        }
        self.cities.append(city_info)
        self.save_cities()
        self.update_weather_list()
    
    def update_weather_list(self):
        self.weather_list.clear()
        for city in self.cities:
            item_text = self.format_weather_info(city["weather_data"], city["imperial"])
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, city["name"])
            self.weather_list.addItem(item)
    
    def format_weather_info(self, weather_data, imperial=False):
        city = weather_data["name"]
        weather_id = weather_data["weather"][0]["id"]
        weather_description = weather_data["weather"][0]["description"]
        temperature = weather_data["main"]["temp"]
        units = 'F' if imperial else 'C'
        
        weather_symbol, color = self.select_weather_display_params(weather_id)
        
        return f"{weather_symbol} {city}: {weather_description.capitalize()} ({temperature}°{units})"
    
    def select_weather_display_params(self, weather_id):
        if weather_id in range(200, 300):
            return ("💥", style.RED)
        elif weather_id in range(300, 400):
            return ("💧", style.CYAN)
        elif weather_id in range(500, 600):
            return ("💦", style.BLUE)
        elif weather_id in range(600, 700):
            return ("⛄️", style.WHITE)
        elif weather_id in range(700, 800):
            return ("🌀", style.BLUE)
        elif weather_id in range(800, 801):
            return ("🔆", style.YELLOW)
        elif weather_id in range(801, 900):
            return ("💨", style.WHITE)
        else:
            return ("🌈", style.RESET)
    
    def clear_selected_weather(self):
        selected_items = self.weather_list.selectedItems()
        if not selected_items:
            return
        
        for item in selected_items:
            city_name = item.data(Qt.UserRole)
            self.cities = [city for city in self.cities if city["name"] != city_name]
        
        self.save_cities()
        self.update_weather_list()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WeatherApp()
    window.show()
    sys.exit(app.exec_())
