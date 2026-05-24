import os
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from ttkbootstrap.scrolled import ScrolledFrame
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
from wardrobe_manager import WardrobeManager
from weather_api import WeatherService
from models import ClothingItem

class DressUpApp(tb.Window):
    def __init__(self):
        super().__init__(themename = "litera")
        self.title("DressUp")
        self.geometry("1400x900")

        try:
            icon_img = Image.open("favicon.png") 
            icon_photo = ImageTk.PhotoImage(icon_img)
            self.iconphoto(False, icon_photo)
        except Exception:
            pass

        self.manager = WardrobeManager()
        self.weather_service = WeatherService(api_key="cf4014d03cf599badf0e55a05cca8c10")
        self.setup_ui()

    def setup_ui(self):
        self.main_container = tb.Frame(self)
        self.main_container.pack(fill=BOTH, expand=YES)

        self.sidebar = tb.Frame(self.main_container, bootstyle="light", width=200)
        self.sidebar.pack(side=LEFT, fill=Y)
        self.create_sidebar_buttons()

        self.content_area = tb.Frame(self.main_container)
        self.content_area.pack(side=RIGHT, fill=BOTH, expand=YES, padx=20, pady=20)
        self.show_dashboard()

    def show_outfit_gen(self):
        self.clear_content()
        top_bar = tb.Frame(self.content_area)
        top_bar.pack(fill=X, pady=10)
        
        tb.Label(top_bar, text="Kde se dnes nacházíš?", font=("Helvetica", 14)).pack(side=LEFT, padx=5)
        self.city_entry = tb.Entry(top_bar, width=20)
        self.city_entry.insert(0, "Praha")
        self.city_entry.pack(side=LEFT, padx=10)
        
        gen_btn = tb.Button(top_bar, text="Navrhni Outfit", bootstyle="primary", command=self.generate_and_display)
        gen_btn.pack(side=LEFT, padx=5)

        self.weather_info_label = tb.Label(self.content_area, text="", font=("Helvetica", 12, "italic"))
        self.weather_info_label.pack(pady=10)

        self.outfit_display_area = tb.Frame(self.content_area)
        self.outfit_display_area.pack(fill=BOTH, expand=YES, pady=20)

    def generate_and_display(self):
        city = self.city_entry.get()
        if not city:
            messagebox.showwarning("Chyba", "Zadej prosím název města.")
            return

        user_settings = self.manager.storage.load_settings()
        w_data = self.weather_service.get_weather(city, user_settings)
        if not w_data["success"]:
            messagebox.showerror("Chyba API", f"Nepodařilo se načíst počasí: {w_data['error']}")
            return

        self.weather_info_label.config(
            text=f"V městě {city} je {w_data['temp']}°C ({w_data['condition']}). Doporučená sezóna: {w_data['season_type']}"
        )

        outfit = self.manager.generate_outfit(w_data["season_type"])
        
        for widget in self.outfit_display_area.winfo_children():
            widget.destroy()
            
        self.image_references = []
        
        for category, item in outfit.items():
            column_frame = tb.Frame(self.outfit_display_area)
            column_frame.pack(side=LEFT, fill=BOTH, expand=YES, padx=5, pady=10)
            
            tb.Label(column_frame, text=category, font=("Helvetica", 10, "bold"), bootstyle="primary").pack()
            
            if item:
                card = self.create_item_card(column_frame, item)
                card.pack(fill=BOTH, expand=YES)
            else:
                tb.Label(column_frame, text="Chybí v šatníku!", bootstyle="danger").pack(pady=20)
        
        confirm_btn = tb.Button(self.outfit_display_area, text="Tento outfit dnes nosím", 
                                bootstyle="success", 
                                command=lambda o=outfit: self.confirm_outfit_usage(o))
        confirm_btn.pack(pady=20)

    def confirm_outfit_usage(self, outfit):
        for item in outfit.values():
            if item:
                self.manager.record_usage(item.item_id)
        messagebox.showinfo("Super!", "Statistiky byly aktualizovány. Sluší ti to!")
        self.show_dashboard()

    def create_sidebar_buttons(self):
        title_label = tb.Label(self.sidebar, text="DressUp", font=("Helvetica", 18, "bold"), bootstyle="primary")
        title_label.pack(pady=30, padx=20)

        buttons = [
            ("Prehled", self.show_dashboard),
            ("Muj Satnik", self.show_wardrobe),
            ("Outfit Builder", self.show_outfit_gen),
            ("Pridat kousek", self.show_add_form),
            ("Nastaveni", self.show_settings)
        ]

        for text, command in buttons:
            btn = tb.Button(self.sidebar, text=text, command=command, bootstyle="link", cursor="hand2")
            btn.pack(fill=X, padx=10, pady=5)

    def clear_content(self):
        for widget in self.content_area.winfo_children():
            widget.destroy()

    def show_dashboard(self):
        self.clear_content()
        header = tb.Frame(self.content_area)
        header.pack(fill=X, pady=(0, 20))
        tb.Label(header, text="Vítej v DressUp", font=("Helvetica", 28, "bold")).pack(side=LEFT)
        
        stats_frame = tb.Frame(self.content_area)
        stats_frame.pack(fill=X, pady=10)
        
        total_card = tb.Frame(stats_frame, bootstyle="primary")
        total_card.pack(side=LEFT, padx=10, fill=BOTH, expand=YES)
        tb.Label(total_card, text=str(len(self.manager.items)), font=("Helvetica", 24, "bold"), bootstyle="inverse-primary").pack()
        tb.Label(total_card, text="Kousků v šatníku", bootstyle="inverse-primary").pack()
        
        most_worn = self.manager.get_most_worn()
        mw_card = tb.Frame(stats_frame, bootstyle="success")
        mw_card.pack(side=LEFT, padx=10, fill=BOTH, expand=YES)
        
        mw_name = most_worn.name if most_worn and most_worn.usage_count > 0 else "Zatím nic"
        tb.Label(mw_card, text=mw_name, font=("Helvetica", 14, "bold"), bootstyle="inverse-success").pack()
        tb.Label(mw_card, text="Nejčastěji nošeno", bootstyle="inverse-success").pack()

        weather_box = tb.LabelFrame(self.content_area, text="Aktuální počasí (Brno)")
        weather_box.pack(fill=X, pady=20)
        
        user_settings = self.manager.storage.load_settings()
        w_data = self.weather_service.get_weather("Brno", user_settings)
        if w_data["success"]:
            tb.Label(weather_box, text=f"{w_data['temp']}°C", font=("Helvetica", 32, "bold")).pack(side=LEFT, padx=20)
            tb.Label(weather_box, text=f"Dnes je {w_data['condition']}.\nIdeální čas na {w_data['season_type']} outfit!", font=("Helvetica", 12)).pack(side=LEFT)
        else:
            tb.Label(weather_box, text="Počasí se nepodařilo načíst").pack()

        tb.Button(self.content_area, text="Navrhnout dnešní outfit", bootstyle="primary", command=self.show_outfit_gen).pack(pady=20)
        
    def show_wardrobe(self):
        self.clear_content()
        header_frame = tb.Frame(self.content_area)
        header_frame.pack(fill=X, pady=(0, 20))
        
        tb.Label(header_frame, text="Můj Šatník", font=("Helvetica", 24, "bold")).pack(side=LEFT)
        tb.Label(header_frame, text=f"Celkem kousků: {len(self.manager.items)}", font=("Helvetica", 10), bootstyle="secondary").pack(side=LEFT, padx=20, pady=10)

        self.scroll_window = ScrolledFrame(self.content_area, autohide=True)
        self.scroll_window.pack(fill=BOTH, expand=YES)

        grid_frame = tb.Frame(self.scroll_window)
        grid_frame.pack(fill=BOTH, expand=YES)

        self.image_references = []
        columns = 4
        for index, item in enumerate(self.manager.items):
            row = index // columns
            col = index % columns
            card = self.create_item_card(grid_frame, item)
            card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

    def create_item_card(self, parent, item):
        card_frame = tb.Frame(parent, bootstyle="secondary")
        img_size = (150, 150)
        try:
            if item.image_path and item.image_path != "None" and os.path.exists(item.image_path):
                img = Image.open(item.image_path)
                img.thumbnail(img_size)
            else:
                img = Image.new('RGB', img_size, color='#e0e0e0')
            
            photo = ImageTk.PhotoImage(img)
            self.image_references.append(photo)
            
            img_label = tb.Label(card_frame, image=photo)
            img_label.pack(pady=5)
        except Exception:
            tb.Label(card_frame, text="Chyba souboru fotky", bootstyle="danger").pack()

        tb.Label(card_frame, text=item.name, font=("Helvetica", 10, "bold"), anchor=CENTER).pack(fill=X)
        tb.Label(card_frame, text=f"{item.category} ({item.color})", font=("Helvetica", 8), bootstyle="info", anchor=CENTER).pack(fill=X)
        
        del_btn = tb.Button(card_frame, text="✕", bootstyle="danger-outline", command=lambda i=item.item_id: self.delete_item_action(i))
        del_btn.pack(pady=5)
        return card_frame

    def delete_item_action(self, item_id):
        if messagebox.askyesno("Smazat", "Opravdu chceš tento kousek odstranit?"):
            self.manager.remove_item(item_id)
            self.show_wardrobe()

    def show_add_form(self):
        self.clear_content()
        tb.Label(self.content_area, text="Přidat nové oblečení", font=("Helvetica", 20)).pack(pady=10)
        
        form_frame = tb.Frame(self.content_area)
        form_frame.pack(fill=X, padx=10)

        tb.Label(form_frame, text="Název kousku:").pack(anchor=W, pady=(10, 0))
        self.name_entry = tb.Entry(form_frame, bootstyle="info")
        self.name_entry.pack(fill=X, pady=5)

        tb.Label(form_frame, text="Kategorie:").pack(anchor=W, pady=(10, 0))
        self.category_combo = tb.Combobox(form_frame, values=ClothingItem.CATEGORIES, state="readonly")
        self.category_combo.pack(fill=X, pady=5)

        tb.Label(form_frame, text="Sezóna:").pack(anchor=W, pady=(10, 0))
        self.season_combo = tb.Combobox(form_frame, values=ClothingItem.SEASONS, state="readonly")
        self.season_combo.pack(fill=X, pady=5)

        tb.Label(form_frame, text="Barva:").pack(anchor=W, pady=(10, 0))
        self.color_combo = tb.Combobox(form_frame, values=ClothingItem.COLORS, state="readonly")
        self.color_combo.pack(fill=X, pady=5)

        self.selected_image_path = None
        photo_btn = tb.Button(form_frame, text="📸 Vybrat fotografii", bootstyle="outline-primary", command=self.select_image)
        photo_btn.pack(fill=X, pady=20)
        
        self.image_label = tb.Label(form_frame, text="Žádný soubor nevybrán", font=("Helvetica", 8))
        self.image_label.pack(anchor=W)

        save_btn = tb.Button(form_frame, text="ULOŽIT DO ŠATNÍKU", bootstyle="success", command=self.save_new_item)
        save_btn.pack(fill=X, pady=30)

    def select_image(self):
        file_path = filedialog.askopenfilename(title="Vyber fotku oblečení", filetypes=[("Obrázky", "*.jpg *.jpeg *.png *.bmp")])
        if file_path:
            self.selected_image_path = file_path
            self.image_label.config(text=f"Vybráno: {file_path.split('/')[-1]}")

    def save_new_item(self):
        name = self.name_entry.get()
        category = self.category_combo.get()
        season = self.season_combo.get()
        color = self.color_combo.get()

        if not name or not category or not season or not color:
            messagebox.showwarning("Chyba", "Prosím vyplňte název, kategorii, sezónu i barvu!")
            return

        self.manager.add_clothing_item(
            name=name,
            category=category,
            color=color,
            season=season,
            image_path=self.selected_image_path
        )

        messagebox.showinfo("Úspěch", f"Kousek '{name}' byl úspěšně přidán!")
        self.show_wardrobe()

    def show_settings(self):
        self.clear_content()
        tb.Label(self.content_area, text="Nastavení teplotních rozsahů", font=("Helvetica", 20, "bold")).pack(pady=20)

        current_settings = self.manager.storage.load_settings()

        form_frame = tb.Frame(self.content_area)
        form_frame.pack(fill=X, padx=10, pady=10)

        tb.Label(form_frame, text="Zima je pro me cokoliv pod (°C):").pack(anchor=W, pady=(10, 0))
        self.winter_spin = tb.Spinbox(form_frame, from_=-10, to=15)
        self.winter_spin.set(current_settings["winter_max"])
        self.winter_spin.pack(fill=X, pady=5)

        tb.Label(form_frame, text="Léto pro mě začíná od (°C):").pack(anchor=W, pady=(10, 0))
        self.summer_spin = tb.Spinbox(form_frame, from_=15, to=35)
        self.summer_spin.set(current_settings["summer_min"])
        self.summer_spin.pack(fill=X, pady=5)

        save_btn = tb.Button(form_frame, text="ULOŽIT NASTAVENÍ", bootstyle="success", command=self.save_settings_action)
        save_btn.pack(fill=X, pady=30)

    def save_settings_action(self):
        """Sebere data z GUI a uloží je"""
        new_settings = {
            "winter_max": int(self.winter_spin.get()),
            "summer_min": int(self.summer_spin.get())
        }
        if new_settings["summer_min"] <= new_settings["winter_max"]:
            messagebox.showerror("Chyba validace", "Začátek léta musí být vyšší než konec zimy!")
            return

        self.manager.storage.save_settings(new_settings)
        messagebox.showinfo("Úspěch", "Teplotní rozsahy byly úspěšně aktualizovány!")
        self.show_dashboard()