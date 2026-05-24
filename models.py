class ClothingItem:
    """
    Class ktera reprezentuje jeden kus obleceni v satniku
    """
    CATEGORIES = ["Hlava", "Triko/Kosile", "Mikina/Bunda", "Spodni dil", "Boty", "Doplnky"]
    SEASONS = ["Leto", "Zima", "Jaro/Podzim", "Jaro/Podzim/Zima", "Celorocni"]
    COLORS = ["Cerna", "Bila", "Seda", "Modra", "Cervena", "Zelena", "Zluta", "Hneda", "Bezova", "Ruzova"]

    def __init__(self, item_id, name, category, color, season, image_path=None, usage_count=0):
        self.item_id = item_id
        self.name = name
        self.category = category if category in self.CATEGORIES else "Ostatni"
        self.color = color if color in self.COLORS else "Cerna"
        self.season = season if season in self.SEASONS else "Celorocni"
        self.image_path = image_path
        self.usage_count = int(usage_count)

    def to_dict(self):
        return {
            "item_id": self.item_id,
            "name": self.name,
            "category": self.category,
            "color": self.color,
            "season": self.season,
            "image_path": self.image_path,
            "usage_count": self.usage_count
        }
    
    @staticmethod
    def from_dict(data):
        return ClothingItem(
            item_id=data["item_id"],
            name=data["name"],
            category=data["category"],
            color=data.get("color", "Cerna"),
            season=data["season"],
            image_path=data.get("image_path"),
            usage_count=data.get("usage_count", 0)
        )