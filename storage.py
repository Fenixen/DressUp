import json
import os
from models import ClothingItem

class StorageManager:
    """
    zajistuje ukladani a nacteni dat satniku v jsonu
    """
    def __init__(self, filename="wardrobe.json"):
        self.filename = filename

    def save_wardrobe(self, items):
        """
        ulozi seznam objektu clothingItem do souboru
        """
        data = [item.to_dict() for item in items]
        try:
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Chyba pri ukladani: {e}")
            return False
    
    def load_wardrobe(self):
        """
        nacte data ze souboru a vrati seznam objektu
        """
        if not os.path.exists(self.filename):
            return []
        
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return [ClothingItem.from_dict(item) for item in data]
        except Exception as e:
            print(f"Chyba pri nacitani: {e}")
            return []
        
    def save_settings(self, settings_data):
        try:
            with open("settings.json", 'w', encoding='UTF-8') as f:
                json.dump(settings_data, f, indent=4)
            return True
        except Exception as e:
            print(f"Chyba pri ukladani : {e}")
            return False
        
    def load_settings(self):
        if not os.path.exists("settings.json"):
            return {"winter_max": 10, "summer_min": 20}
        
        try:
            with open("settings.json", 'r', encoding='UTF-8') as f:
                return json.load(f)
        except Exception:
            return {"winter_max": 10, "summer_min": 20}