"""
My Plant Pal - A modern plant care tracker with a sleek UI, built using Tkinter.
|================================================================================|
Author: Victor Delgado | GitHub: https://github.com/VictorDelgadoJ-Ops/My-Plant-Pal
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import json, os
from datetime import datetime, timedelta

# ---------- THEMES ----------
# Light theme color palette with bright, neutral colors
LIGHT_THEME = {
    "bg_main": "#FAFAFA", "bg_panel": "#F0F0F0",
    "header_bg": "#E0E0E0", "header_text": "#333333",
    "btn": "#8BC34A", "btn_hover": "#7CB342",
    "btn_text": "#FFFFFF", "text": "#333333",
    "accent": "#DCEDC8", "list_bg": "#F0F0F0",
    "list_fg": "#333333", "entry_bg": "#FFFFFF",
    "entry_fg": "#333333", "input_border": "#CCCCCC"
}

# Dark theme color palette with dark backgrounds and light text for better night visibility
DARK_THEME = {
    "bg_main": "#0D0D0D", "bg_panel": "#1A1A1A",
    "header_bg": "#1F1F1F", "header_text": "#E8E8E8",
    "btn": "#2E7D32", "btn_hover": "#4CAF50",
    "btn_text": "#FFFFFF", "text": "#E8E8E8",
    "accent": "#1B5E20", "list_bg": "#1A1A1A",
    "list_fg": "#E8E8E8", "entry_bg": "#252525",
    "entry_fg": "#E8E8E8", "input_border": "#404040"
}

# Global theme variable that can be switched at runtime
THEME = DARK_THEME.copy()

# Load image icons and resize them for consistent UI appearance
def load_icon(filename, size):
    path = os.path.join("images", filename)
    if not os.path.exists(path):
        return None  # Return None if icon file not found
    return ImageTk.PhotoImage(Image.open(path).resize(size, Image.LANCZOS))

class MyPlantPal:
    def __init__(self, root):
        self.root = root
        self.root.title("My Plant Pal")
        self.current_theme = "dark"

        # Initialize data structures for storing plant information and UI state
        self.plants = []  # List of all plant dictionaries
        self.buttons = []  # Track all buttons for theme updates
        self.tree_items = []  # Tree item IDs for each displayed plant
        self.plant_thumbs = []  # Plant thumbnail images for treeview
        self.filtered_plants = []  # Track filtered plant indices from search
        self.toast_windows = []  # Track open toast notification windows
        self.selected_plant_item = None  # Current selected plant item for highlighting

        # Load icons for UI buttons and plant thumbnails
        self.icon_add = load_icon("add.png", (20, 20))
        self.icon_delete = load_icon("delete.png", (20, 20))
        self.icon_leaf = load_icon("leaf.png", (20, 20))
        self.icon_water = load_icon("water.png", (20, 20))
        self.icon_default = load_icon("default.png", (40, 40))  # Fallback icon if plant image missing

        self.root.configure(bg=THEME["bg_main"])

        # ---------- HEADER ----------
        self.header_frame = tk.Frame(self.root, bg=THEME["header_bg"], height=50)
        self.header_frame.pack(fill="x")

        self.title_label = tk.Label(
            self.header_frame, text=" My Plant Pal",
            font=("Arial", 16, "bold"),
            bg=THEME["header_bg"], fg=THEME["header_text"],
            image=self.icon_leaf, compound="left"
        )
        self.title_label.pack(side="left", padx=10)

        self.btn_dashboard = self._header_button("Dashboard", self.show_dashboard)
        self.btn_dashboard.pack(side="left", padx=5)

        self.btn_plants = self._header_button("Plants", self.show_plants_page)
        self.btn_plants.pack(side="left", padx=5)

        self.dark_mode_btn = self._header_button("Light Mode", self.toggle_theme)
        self.dark_mode_btn.pack(side="right", padx=10)

        # ---------- PAGES ----------
        # Create frame containers for dashboard and plants pages
        self.dashboard_frame = tk.Frame(self.root, bg=THEME["bg_main"])
        self.plants_frame = tk.Frame(self.root, bg=THEME["bg_main"])

        # Show dashboard first
        self.dashboard_frame.pack(fill="both", expand=True)

        # Load plant data from JSON file before rendering UI
        self.load_plants()

        # Build UI page components
        self.build_dashboard()
        self.build_plants_page()

        # Refresh plant list display and show any pending watering reminders
        self.update_list()
        self.check_watering_reminders()

    # ---------- HEADER BUTTON ----------
    def _header_button(self, text, command):
        btn = tk.Button(
            self.header_frame, text=text,
            bg=THEME["btn"], fg=THEME["btn_text"],
            activebackground=THEME["btn_hover"],
            relief="flat", bd=0, padx=12, pady=4,
            command=command
        )
        self._style_button(btn)
        return btn

    # ---------- BUTTON STYLE ----------
    def _style_button(self, btn):
        self.buttons.append(btn)
        btn.bind("<Enter>", lambda e: btn.config(bg=THEME["btn_hover"]))
        btn.bind("<Leave>", lambda e: btn.config(bg=THEME["btn"]))

    def _create_button(self, parent, text, command, icon=None):
        btn = tk.Button(
            parent, text=text, image=icon, compound="left",
            bg=THEME["btn"], fg=THEME["btn_text"],
            activebackground=THEME["btn_hover"],
            relief="flat", bd=0, padx=12, pady=6,
            command=command
        )
        self._style_button(btn)
        return btn

    # ---------- TOAST NOTIFICATIONS ----------
    def show_toast(self, message, duration=3000):
        """Display a toast notification that auto-closes after specified duration (ms)"""
        toast = tk.Toplevel(self.root)
        toast.wm_overrideredirect(True)
        toast.wm_attributes('-alpha', 0.9)
        toast.configure(bg=THEME["bg_panel"])
        
        # Create a frame with border for card effect
        frame = tk.Frame(toast, bg=THEME["btn"], highlightthickness=1, highlightbackground=THEME["input_border"])
        frame.pack(padx=1, pady=1)
        
        label = tk.Label(frame, text=message, bg=THEME["btn"], fg=THEME["btn_text"],
                        font=("Arial", 10), padx=20, pady=10)
        label.pack()
        
        # Position at bottom right
        toast.update_idletasks()
        x = self.root.winfo_x() + self.root.winfo_width() - toast.winfo_width() - 20
        y = self.root.winfo_y() + self.root.winfo_height() - toast.winfo_height() - 20
        toast.geometry(f"+{x}+{y}")
        
        self.toast_windows.append(toast)
        
        # Auto-close
        toast.after(duration, lambda: self._close_toast(toast))
    
    def _close_toast(self, toast):
        try:
            toast.destroy()
            self.toast_windows.remove(toast)
        except:
            pass

    # ---------- THEME ----------
    def toggle_theme(self):
        """Switch between light and dark themes and refresh all UI elements"""
        global THEME
        if self.current_theme == "light":
            THEME.update(DARK_THEME)  # Switch to dark theme
            self.current_theme = "dark"
            self.dark_mode_btn.config(text="Light Mode")
        else:
            THEME.update(LIGHT_THEME)  # Switch to light theme
            self.current_theme = "light"
            self.dark_mode_btn.config(text="Dark Mode")
        self.apply_theme()  # Reapply all colors to UI components

    def apply_theme(self):
        """Apply current theme colors to all UI components"""
        self.root.configure(bg=THEME["bg_main"])
        self.header_frame.configure(bg=THEME["header_bg"])
        self.title_label.configure(bg=THEME["header_bg"], fg=THEME["header_text"])
        self.dashboard_frame.configure(bg=THEME["bg_main"])
        self.plants_frame.configure(bg=THEME["bg_main"])

        # Update all buttons with new theme colors
        for btn in self.buttons:
            btn.configure(bg=THEME["btn"], fg=THEME["btn_text"])

        if hasattr(self, "style"):
            self.style.configure(
                "PlantTreeview",
                background=THEME["list_bg"],
                fieldbackground=THEME["list_bg"],
                foreground=THEME["list_fg"]
            )

        self.build_dashboard()
        self.build_plants_page()
        self.update_list()

    # ---------- PAGE SWITCH ----------
    def show_dashboard(self):
        self.plants_frame.pack_forget()
        self.dashboard_frame.pack(fill="both", expand=True)
        self.build_dashboard()

    def show_plants_page(self):
        self.dashboard_frame.pack_forget()
        self.plants_frame.pack(fill="both", expand=True)

    # ---------- DASHBOARD ----------
    def build_dashboard(self):
        for w in self.dashboard_frame.winfo_children():
            w.destroy()

        stats = self.get_stats()

        # Stat cards
        card_frame = tk.Frame(self.dashboard_frame, bg=THEME["bg_main"])
        card_frame.pack(pady=20)

        def card(label, value, color):
            # Shadow effect with nested frames
            shadow = tk.Frame(card_frame, bg=THEME["bg_main"], height=2)
            c = tk.Frame(shadow, bg=THEME["bg_panel"], padx=20, pady=15, relief="raised", bd=2)
            c.pack(side="top")
            shadow.pack(side="left", padx=8, pady=10)
            tk.Label(c, text=value, font=("Arial", 20, "bold"), fg=color, bg=THEME["bg_panel"]).pack()
            tk.Label(c, text=label, font=("Arial", 10), fg=THEME["text"], bg=THEME["bg_panel"]).pack()

        card("Total Plants", stats["total"], "#2E7D32")
        card("Need Water Today", stats["today"], "#0277BD")
        card("Overdue", stats["overdue"], "#C62828")

        # Health bar
        bar_frame = tk.Frame(self.dashboard_frame, bg=THEME["bg_main"])
        bar_frame.pack(pady=20)

        tk.Label(bar_frame, text="Plant Health Overview",
                 font=("Arial", 12, "bold"),
                 bg=THEME["bg_main"], fg=THEME["text"]).pack()

        canvas = tk.Canvas(bar_frame, width=400, height=30,
                           bg=THEME["bg_panel"], highlightthickness=1,
                           highlightbackground=THEME["input_border"])
        canvas.pack(pady=10)

        total = max(stats["total"], 1)
        x = 0

        def bar(width, color):
            nonlocal x
            canvas.create_rectangle(x, 0, x + width, 30, fill=color, width=0)
            x += width

        bar((stats["healthy"] / total) * 400, "#66BB6A")
        bar((stats["today"] / total) * 400, "#FFCA28")
        bar((stats["overdue"] / total) * 400, "#EF5350")

        # Quick actions
        actions = tk.Frame(self.dashboard_frame, bg=THEME["bg_main"])
        actions.pack(pady=20)

        self._create_button(actions, "Add Plant", self.add_plant_window).pack(side="left", padx=10)
        self._create_button(actions, "View Plants", self.show_plants_page).pack(side="left", padx=10)

    # ---------- STATS ----------
    def get_stats(self):
        """Calculate plant health statistics for dashboard display"""
        today = datetime.now().date()
        total = len(self.plants)
        today_due = overdue = healthy = 0

        # Categorize each plant based on watering schedule
        for p in self.plants:
            last = datetime.strptime(p["last_watered"], "%Y-%m-%d").date()
            due = last + timedelta(days=p["water"])  # Calculate next watering date
            if today > due:
                overdue += 1  # Plant needs water urgently
            elif today == due:
                today_due += 1  # Plant needs water today
            else:
                healthy += 1  # Plant is fine, not due yet

        return {"total": total, "today": today_due, "overdue": overdue, "healthy": healthy}

    # ---------- PLANTS PAGE ----------
    def build_plants_page(self):
        for w in self.plants_frame.winfo_children():
            w.destroy()

        self.style = ttk.Style(self.root)
        self.style.configure(
            "PlantTreeview",
            rowheight=48,
            background=THEME["list_bg"],
            fieldbackground=THEME["list_bg"],
            foreground=THEME["list_fg"],
            borderwidth=0
        )
        self.style.layout("PlantTreeview", [("Treeview.treearea", {"sticky": "nswe"})])

        # Search frame
        search_frame = tk.Frame(self.plants_frame, bg=THEME["bg_main"])
        search_frame.pack(fill="x", padx=10, pady=10)
        
        tk.Label(search_frame, text="Search Plants:", bg=THEME["bg_main"], fg=THEME["text"]).pack(side="left", padx=5)
        
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=self.search_var, 
                               bg=THEME["entry_bg"], fg=THEME["entry_fg"],
                               insertbackground=THEME["entry_fg"], width=30)
        search_entry.pack(side="left", padx=5)
        search_entry.bind("<KeyRelease>", lambda e: self.filter_plants())

        self.plant_tree = ttk.Treeview(self.plants_frame, style="PlantTreeview", show="tree")
        self.plant_tree.pack(fill="both", expand=True, pady=5)
        
        # Bind hover effects
        self.plant_tree.bind("<Motion>", self._on_treeview_hover)
        self.plant_tree.bind("<Leave>", self._on_treeview_leave)
        self.plant_tree.bind("<Button-1>", self._on_treeview_click)
        self.last_hovered_item = None

        btns = tk.Frame(self.plants_frame, bg=THEME["bg_main"])
        btns.pack(pady=10)

        self._create_button(btns, "Add Plant", self.add_plant_window, self.icon_add).grid(row=0, column=0, padx=5)
        self._create_button(btns, "Details", self.show_details).grid(row=0, column=1, padx=5)
        self._create_button(btns, "Delete", self.delete_plant, self.icon_delete).grid(row=0, column=2, padx=5)

        self._create_button(self.plants_frame, "Save Plants", self.save_plants).pack(pady=5)

    def filter_plants(self):
        """Filter and display plants based on search query"""
        query = self.search_var.get().lower()
        
        # Clear current treeview display
        for item in self.plant_tree.get_children():
            self.plant_tree.delete(item)
        
        # Reset tracking lists
        self.tree_items = []
        self.plant_thumbs = []
        self.filtered_plants = []
        self.selected_plant_item = None  # Clear selection when filtering
        
        # Add only plants matching the search query
        for idx, p in enumerate(self.plants):
            if query == "" or query in p["name"].lower():
                img_path = p.get("image")
                photo = None
                
                # Try to load plant's custom image
                if img_path and os.path.exists(img_path):
                    try:
                        img = Image.open(img_path).resize((40, 40), Image.LANCZOS)
                        photo = ImageTk.PhotoImage(img)
                    except:
                        photo = None  # Fallback if image fails to load
                
                # Use default icon if no custom image available
                if photo is None and self.icon_default is not None:
                    photo = self.icon_default
                
                self.plant_thumbs.append(photo)
                
                if photo is not None:
                    item_id = self.plant_tree.insert("", "end", text=p["name"], image=photo)
                else:
                    item_id = self.plant_tree.insert("", "end", text=p["name"])
                
                self.tree_items.append(item_id)
                self.filtered_plants.append(idx)
    
    def _on_treeview_hover(self, event):
        """Handle treeview hover effects"""
        item = self.plant_tree.identify("item", event.x, event.y)
        if item != self.last_hovered_item:
            if self.last_hovered_item and self.last_hovered_item != self.selected_plant_item:
                self.plant_tree.item(self.last_hovered_item, tags=())
            if item and item != self.selected_plant_item:
                self.plant_tree.item(item, tags=("hover",))
                self.plant_tree.tag_configure("hover", background="#2E7D32")
            self.last_hovered_item = item
    
    def _on_treeview_leave(self, event):
        """Remove hover effect when leaving treeview"""
        if self.last_hovered_item and self.last_hovered_item != self.selected_plant_item:
            self.plant_tree.item(self.last_hovered_item, tags=())
            self.last_hovered_item = None
    
    def _on_treeview_click(self, event):
        """Handle plant selection with dark yellow highlight"""
        item = self.plant_tree.identify("item", event.x, event.y)
        
        # Remove highlight from previously selected item
        if self.selected_plant_item and self.selected_plant_item != item:
            self.plant_tree.item(self.selected_plant_item, tags=())
        
        # Highlight clicked item in dark yellow
        if item:
            self.plant_tree.item(item, tags=("selected",))
            self.plant_tree.tag_configure("selected", background="#B8860B")
            self.selected_plant_item = item

    # ---------- ADD PLANT ----------
    def add_plant_window(self):
        win = tk.Toplevel(self.root)
        win.title("Add Plant")
        win.configure(bg=THEME["bg_panel"])

        def label(text, row):
            tk.Label(win, text=text, bg=THEME["bg_panel"], fg=THEME["text"]).grid(
                row=row, column=0, pady=5, padx=5, sticky="e"
            )

        label("Plant Name:", 0)
        name_entry = tk.Entry(win, bg=THEME["entry_bg"], fg=THEME["entry_fg"],
                              insertbackground=THEME["entry_fg"])
        name_entry.grid(row=0, column=1, pady=5, padx=5)

        label("Water Every (days):", 1)
        water_entry = tk.Entry(win, bg=THEME["entry_bg"], fg=THEME["entry_fg"],
                               insertbackground=THEME["entry_fg"])
        water_entry.grid(row=1, column=1, pady=5, padx=5)

        label("Sunlight Level:", 2)
        sunlight_var = tk.StringVar(value="Medium")
        sun_menu = tk.OptionMenu(win, sunlight_var, "Low", "Medium", "High")
        sun_menu.configure(bg=THEME["btn"], fg=THEME["btn_text"],
                          activebackground=THEME["btn_hover"],
                          activeforeground=THEME["btn_text"])
        sun_menu.grid(row=2, column=1, pady=5, padx=5, sticky="w")

        label("Image (optional):", 3)
        img_path_var = tk.StringVar()
        tk.Entry(win, textvariable=img_path_var, bg=THEME["entry_bg"],
                fg=THEME["entry_fg"], insertbackground=THEME["entry_fg"]).grid(row=3, column=1, pady=5, padx=5)

        def browse_img():
            path = filedialog.askopenfilename(filetypes=[("Images", "*.png;*.jpg;*.jpeg")])
            if path:
                img_path_var.set(path)

        self._create_button(win, "Browse", browse_img).grid(row=3, column=2, padx=5)

        def save():
            # Get form input values
            name = name_entry.get().strip()
            water = water_entry.get().strip()
            sun = sunlight_var.get()
            img = img_path_var.get().strip()

            # Validate plant name is not empty
            if not name:
                self.show_toast("Please enter a plant name.")
                return
            # Validate watering frequency is a valid number
            if not water.isdigit():
                self.show_toast("Watering frequency must be a number.")
                return

            # Add new plant to database with metadata
            self.plants.append({
                "name": name,
                "water": int(water),
                "sun": sun,
                "image": img,
                "last_watered": datetime.now().strftime("%Y-%m-%d")  # Initialize with today's date
            })
            self.update_list()
            self.build_dashboard()
            self.show_toast(f"{name} added successfully!")
            win.destroy()

        self._create_button(win, "Save Plant", save).grid(row=4, column=0, columnspan=3, pady=10)

    # ---------- DETAILS ----------
    def show_details(self):
        if not hasattr(self, "plant_tree"):
            return
        selected = self.plant_tree.selection()
        if not selected:
            self.show_toast("Pick a plant first.")
            return

        index = self.tree_items.index(selected[0])
        plant = self.plants[self.filtered_plants[index]]

        win = tk.Toplevel(self.root)
        win.title("Plant Details")
        win.configure(bg=THEME["bg_panel"])

        def detail(text):
            tk.Label(win, text=text, bg=THEME["bg_panel"], fg=THEME["text"]).pack(pady=5)

        detail(f"Name: {plant['name']}")
        detail(f"Water Every: {plant['water']} days")
        detail(f"Sunlight: {plant['sun']}")
        detail(f"Last Watered: {plant['last_watered']}")

        if plant["image"] and os.path.exists(plant["image"]):
            img = Image.open(plant["image"]).resize((200, 200), Image.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            img_label = tk.Label(win, image=photo, bg=THEME["bg_panel"])
            img_label.image = photo
            img_label.pack(pady=10)

        def mark_as_watered():
            plant["last_watered"] = datetime.now().strftime("%Y-%m-%d")
            self.show_toast(f"{plant['name']} marked as watered!")
            win.destroy()
            self.update_list()
            self.build_dashboard()

        self._create_button(win, "Mark as Watered", mark_as_watered, self.icon_water).pack(pady=5)
        self._create_button(win, "Close", win.destroy).pack(pady=10)

    # ---------- DELETE ----------
    def delete_plant(self):
        if not hasattr(self, "plant_tree"):
            return
        selected = self.plant_tree.selection()
        if not selected:
            self.show_toast("Select a plant to delete.")
            return
        index = self.tree_items.index(selected[0])
        deleted_name = self.plants[self.filtered_plants[index]]["name"]
        del self.plants[self.filtered_plants[index]]
        self.update_list()
        self.build_dashboard()
        self.show_toast(f"{deleted_name} deleted!")

    # ---------- SAVE / LOAD ----------
    def save_plants(self):
        """Persist all plant data to JSON file for recovery on app restart"""
        with open("plants.json", "w") as f:
            json.dump(self.plants, f, indent=4)  # Pretty-print JSON for readability
        self.show_toast("Plants saved successfully!")

    def load_plants(self):
        """Load plant data from JSON file at app startup"""
        if os.path.exists("plants.json"):
            with open("plants.json", "r") as f:
                self.plants = json.load(f)  # Load plant list from persistent storage

    # ---------- REMINDERS ----------
    def check_watering_reminders(self):
        """Check for plants that need watering and show alert"""
        today = datetime.now().date()
        reminders = []
        for plant in self.plants:
            last = datetime.strptime(plant["last_watered"], "%Y-%m-%d").date()
            due = last + timedelta(days=plant["water"])  # Calculate when plant is due
            if today >= due:  # If today is on or past the due date
                reminders.append(plant["name"])
        if reminders:
            message = "Plants need water: " + ", ".join(reminders)
            self.show_toast(message, duration=5000)  # Show longer notification for reminders

    # ---------- UPDATE LIST ----------
    def update_list(self):
        """Refresh the plant list display with current search filter applied"""
        # Guard against calling before treeview is initialized
        if not hasattr(self, "plant_tree") or self.plant_tree is None:
            return

        # Reapply search filter to update displayed plants
        self.filter_plants()

if __name__ == "__main__":
    root = tk.Tk()
    app = MyPlantPal(root)
    root.mainloop()