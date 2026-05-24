import random
from storage import StorageManager
from models import ClothingItem

class WardrobeManager:
    def __init__(self):
        self.storage = StorageManager()
        self.items = self.storage.load_wardrobe()

    def add_clothing_item(self, name, category, color, season, image_path):
        new_id = max([item.item_id for item in self.items], default=0) + 1
        new_item = ClothingItem(
            item_id=new_id,
            name=name,
            category=category,
            color=color,
            season=season,
            image_path=image_path,
            usage_count=0
        )
        self.items.append(new_item)
        self.storage.save_wardrobe(self.items)
        return new_item
    
    def remove_item(self, item_id):
        self.items = [item for item in self.items if item.item_id != item_id]
        return self.storage.save_wardrobe(self.items)
    
    def get_items_by_season(self, season):
        valid_items = []
        for item in self.items:
            if item.season == "Celorocni" or item.season == season:
                valid_items.append(item)
            elif item.season == "Jaro/Podzim/Zima" and season in ["Jaro/Podzim", "Zima"]:
                valid_items.append(item)
        return valid_items
    
    def generate_outfit(self, weather_season):
        relevant_items = self.get_items_by_season(weather_season)
        outfit = {}

        if weather_season == "Leto":
            category_order = ["Hlava", "Triko/Kosile", "Spodni dil", "Boty", "Doplnky"]
        else:
            category_order = ["Hlava", "Triko/Kosile", "Mikina/Bunda", "Spodni dil", "Boty", "Doplnky"]

        selected_colors = []

        for category in category_order:
            category_options = [item for item in relevant_items if item.category == category]

            if not category_options:
                outfit[category] = None
                continue

            color_filtered = []
            for item in category_options:
                if all(self.are_colors_compatible(item.color, c) for c in selected_colors):
                    color_filtered.append(item)

            if not color_filtered:
                color_filtered = category_options

            max_usage = max(item.usage_count for item in color_filtered)
            weights = [(max_usage + 1) - item.usage_count for item in color_filtered]
            
            chosen_item = random.choices(color_filtered, weights=weights, k=1)[0]
            outfit[category] = chosen_item
            
            if chosen_item.color:
                selected_colors.append(chosen_item.color)

        return outfit
    
    def are_colors_compatible(self, color1, color2):
        if not color1 or not color2 or color1 == "Nespecifikováno" or color2 == "Nespecifikováno":
            return True
        neutrals = ["Cerna", "Bila", "Seda", "Bezova"]
        if color1 in neutrals or color2 in neutrals:
            return True
        forbidden = [
            {"Cervena", "Zelena"},
            {"Cervena", "Ruzova"},
            {"Modra", "Hneda"},
            {"Zluta", "Zelena"}
        ]
        return {color1, color2} not in forbidden
    
    def record_usage(self, item_id):
        for item in self.items:
            if item.item_id == item_id:
                item.usage_count += 1
                break
        self.storage.save_wardrobe(self.items)

    def get_most_worn(self):
        if not self.items: return None
        return max(self.items, key=lambda x: x.usage_count)