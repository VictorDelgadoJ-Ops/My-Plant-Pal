"""
My Plant Pal — Modern UI Edition
Author: Victor Delgado

Features:
- Add plants with name, watering frequency, sunlight level, and optional image.
- View plant details including last watered date and image.
- Mark plants as watered.
- Delete plants.
- Save/load JSON.
- Modern UI: header bar, PNG icons, card-style list, thumbnails, light/dark mode.
"""

import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter import ttk
import json
import os
from datetime import datetime, timedelta
from PIL import Image, ImageTk

# ---------- THEMES ----------

LIGHT_THEME = {
    "bg_main": "#FAFAFA",
    "bg_panel": "#F0F0F0",
    "header_bg": "#E0E0E0",
    "header_text": "#333333",
    "btn": "#8BC34A",
    "btn_hover": "#7CB342",
    "btn_text": "#FFFFFF",
    "text": "#333333",
    "accent": "#DCEDC8",
    "list_bg": "#F0F0F0",
    "list_fg": "#333333"
}

DARK_THEME = {
    "bg_main": "#121212",
    "bg_panel": "#1E1E1E",
    "header_bg": "#1F2933",
    "header_text": "#E5E5E5",
    "btn": "#4CAF50",
    "btn_hover": "#66BB6A",
    "btn_text": "#FFFFFF",
    "text": "#E5E5E5",
    "accent": "#2E7D32",
    "list_bg": "#1E1E1E",
    "list_fg": "#E5E5E5"
}

THEME = LIGHT_THEME.copy()


# ---------- ICON LOADER ----------

def load_icon(filename, size):
    path = os.path.join("images", filename)
    if not os.path.exists(path):
        return None
    img = Image.open(path).resize(size, Image.LANCZOS)
    return ImageTk.PhotoImage(img)


# ---------- MAIN APP ----------

class MyPlantPal:
    def __init__(self, root):
        self.root = root
        self.root.title("My Plant Pal")
        self.current_theme = "light"

        self.plants = []
        self.buttons = []
        self.tree_items = []
        self.plant_thumbs = []

        # Load icons
        self.icon_add = load_icon("add.png", (20, 20))
        self.icon_delete = load_icon("delete.png", (20, 20))
        self.icon_leaf = load_icon("leaf.png", (20, 20))
        self.icon_sun = load_icon("sun.png", (20, 20))
        self.icon_water = load_icon("water.png", (20, 20))
        self.icon_default = load_icon("default.png", (40, 40))

        self.root.configure(bg=THEME["bg_main"])

        # ---------- HEADER ----------
        self.header_frame = tk.Frame(self.root, bg=THEME["header_bg"], height=50)
        self.header_frame.pack(fill="x")

        self.title_label = tk.Label(
            self.header_frame,
            text=" My Plant Pal",
            font=("Arial", 16, "bold"),
            bg=THEME["header_bg"],
            fg=THEME["header_text"],
            image=self.icon_leaf,
            compound="left"
        )
        self.title_label.pack(side="left", padx=10, pady=8)

        self.dark_mode_btn = tk.Button(
            self.header_frame,
            text="Dark Mode",
            bg=THEME["btn"],
            fg=THEME["btn_text"],
            activebackground=THEME["btn_hover"],
            relief="flat",
            bd=0,
            padx=12,
            pady=4,
            command=self.toggle_theme
        )
        self.dark_mode_btn.pack(side="right", padx=10, pady=8)
        self._style_button(self.dark_mode_btn)

        # ---------- MAIN CONTENT ----------
        main_frame = tk.Frame(self.root, bg=THEME["bg_main"])
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Treeview card-style list
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

        self.plant_tree = ttk.Treeview(
            main_frame,
            style="PlantTreeview",
            show="tree"
        )
        self.plant_tree.pack(fill="both", expand=True, pady=5)

        # Buttons row
        btns = tk.Frame(main_frame, bg=THEME["bg_main"])
        btns.pack(pady=10)

        self.add_btn = self._create_button(btns, "Add Plant", self.add_plant_window, self.icon_add)
        self.add_btn.grid(row=0, column=0, padx=5)

        self.details_btn = self._create_button(btns, "Details", self.show_details)
        self.details_btn.grid(row=0, column=1, padx=5)

        self.delete_btn = self._create_button(btns, "Delete", self.delete_plant, self.icon_delete)
        self.delete_btn.grid(row=0, column=2, padx=5)

        self.save_btn = self._create_button(main_frame, "Save Plants", self.save_plants)
        self.save_btn.pack(pady=5)

        # Load data
        self.load_plants()
        self.update_list()
        self.check_watering_reminders()

    # ---------- BUTTON STYLING ----------

    def _create_button(self, parent, text, command, icon=None):
        btn = tk.Button(
            parent,
            text=text,
            image=icon,
            compound="left",
            bg=THEME["btn"],
            fg=THEME["btn_text"],
            activebackground=THEME["btn_hover"],
            relief="flat",
            bd=0,
            padx=12,
            pady=6,
            command=command
        )
        self._style_button(btn)
        return btn

    def _style_button(self, btn):
        self.buttons.append(btn)

        def on_enter(e):
            try:
                btn.configure(bg=THEME["btn_hover"])
            except tk.TclError:
                pass

        def on_leave(e):
            try:
                btn.configure(bg=THEME["btn"])
            except tk.TclError:
                pass

        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)

    # ---------- THEME TOGGLE ----------

    def toggle_theme(self):
        global THEME
        if self.current_theme == "light":
            THEME.update(DARK_THEME)
            self.current_theme = "dark"
            self.dark_mode_btn.config(text="Light Mode")
        else:
            THEME.update(LIGHT_THEME)
            self.current_theme = "light"
            self.dark_mode_btn.config(text="Dark Mode")
        self.apply_theme()

    def apply_theme(self):
        self.root.configure(bg=THEME["bg_main"])
        self.header_frame.configure(bg=THEME["header_bg"])
        self.title_label.configure(bg=THEME["header_bg"], fg=THEME["header_text"])

        for btn in self.buttons:
            btn.configure(bg=THEME["btn"], fg=THEME["btn_text"], activebackground=THEME["btn_hover"])

        self.style.configure(
            "PlantTreeview",
            background=THEME["list_bg"],
            fieldbackground=THEME["list_bg"],
            foreground=THEME["list_fg"]
        )

    # ---------- ADD PLANT WINDOW ----------

    def add_plant_window(self):
        win = tk.Toplevel(self.root)
        win.title("Add Plant")
        win.configure(bg=THEME["bg_panel"])

        def label(text, row):
            tk.Label(win, text=text, bg=THEME["bg_panel"], fg=THEME["text"]).grid(
                row=row, column=0, pady=5, padx=5, sticky="e"
            )

        label("Plant Name:", 0)
        name_entry = tk.Entry(win)
        name_entry.grid(row=0, column=1, pady=5, padx=5)

        label("Water Every (days):", 1)
        water_entry = tk.Entry(win)
        water_entry.grid(row=1, column=1, pady=5, padx=5)

        label("Sunlight Level:", 2)
        sunlight_var = tk.StringVar(value="Medium")
        sun_menu = tk.OptionMenu(win, sunlight_var, "Low", "Medium", "High")
        sun_menu.configure(bg=THEME["bg_panel"], fg=THEME["text"])
        sun_menu.grid(row=2, column=1, pady=5, padx=5, sticky="w")

        label("Image (optional):", 3)
        img_path_var = tk.StringVar()
        tk.Entry(win, textvariable=img_path_var).grid(row=3, column=1, pady=5, padx=5)

        def browse_img():
            path = filedialog.askopenfilename(filetypes=[("Images", "*.png;*.jpg;*.jpeg")])
            if path:
                img_path_var.set(path)

        browse_btn = tk.Button(
            win,
            text="Browse",
            bg=THEME["btn"],
            fg=THEME["btn_text"],
            activebackground=THEME["btn_hover"],
            relief="flat",
            bd=0,
            padx=10,
            pady=4,
            command=browse_img
        )
        browse_btn.grid(row=3, column=2, padx=5)
        self._style_button(browse_btn)

        def save():
            name = name_entry.get().strip()
            water = water_entry.get().strip()
            sun = sunlight_var.get()
            img = img_path_var.get().strip()

            if not name:
                messagebox.showerror("Error", "Please enter a plant name.")
                return

            if not water.isdigit():
                messagebox.showerror("Error", "Watering frequency must be a number.")
                return

            plant = {
                "name": name,
                "water": int(water),
                "sun": sun,
                "image": img,
                "last_watered": datetime.now().strftime("%Y-%m-%d")
            }

            self.plants.append(plant)
            self.update_list()
            win.destroy()

        save_btn = tk.Button(
            win,
            text="Save Plant",
            bg=THEME["btn"],
            fg=THEME["btn_text"],
            activebackground=THEME["btn_hover"],
            relief="flat",
            bd=0,
            padx=12,
            pady=6,
            command=save
        )
        save_btn.grid(row=4, column=0, columnspan=3, pady=10)
        self._style_button(save_btn)

    # ---------- DETAILS WINDOW ----------

    def show_details(self):
        selected = self.plant_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Pick a plant first.")
            return

        item_id = selected[0]
        index = self.tree_items.index(item_id)
        plant = self.plants[index]

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
            messagebox.showinfo("Updated", f"{plant['name']} marked as watered today.")
            win.destroy()
            self.update_list()

        mark_btn = tk.Button(
            win,
            text="Mark as Watered",
            image=self.icon_water,
            compound="left",
            bg=THEME["btn"],
            fg=THEME["btn_text"],
            activebackground=THEME["btn_hover"],
            relief="flat",
            bd=0,
            padx=12,
            pady=6,
            command=mark_as_watered
        )
        mark_btn.pack(pady=5)
        self._style_button(mark_btn)

        close_btn = tk.Button(
            win,
            text="Close",
            bg=THEME["btn"],
            fg=THEME["btn_text"],
            activebackground=THEME["btn_hover"],
            relief="flat",
            bd=0,
            padx=12,
            pady=6,
            command=win.destroy
        )
        close_btn.pack(pady=10)
        self._style_button(close_btn)

    # ---------- DELETE PLANT ----------

    def delete_plant(self):
        selected = self.plant_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select a plant to delete.")
            return

        item_id = selected[0]
        index = self.tree_items.index(item_id)

        del self.plants[index]
        self.update_list()

    # ---------- SAVE / LOAD ----------

    def save_plants(self):
        with open("plants.json", "w") as f:
            json.dump(self.plants, f, indent=4)
        messagebox.showinfo("Saved", "Plants saved successfully.")

    def load_plants(self):
        if os.path.exists("plants.json"):
            with open("plants.json", "r") as f:
                self.plants = json.load(f)

    # ---------- REMINDERS ----------

    def check_watering_reminders(self):
        today = datetime.now().date()
        reminders = []

        for plant in self.plants:
            last = datetime.strptime(plant["last_watered"], "%Y-%m-%d").date()
            due = last + timedelta(days=plant["water"])
            if today >= due:
                reminders.append(plant["name"])

        if reminders:
            messagebox.showinfo(
                "Watering Reminder",
                "These plants need water:\n\n" + "\n".join(reminders)
            )

    # ---------- UPDATE TREEVIEW ----------

    def update_list(self):
        # Clear tree
        for item in self.plant_tree.get_children():
            self.plant_tree.delete(item)

        self.tree_items = []
        self.plant_thumbs = []

        for p in self.plants:
            img_path = p.get("image")

            # Try to load plant image
            photo = None
            if img_path and os.path.exists(img_path):
                try:
                    img = Image.open(img_path).resize((40, 40), Image.LANCZOS)
                    photo = ImageTk.PhotoImage(img)
                except:
                    photo = None

            # Fallback to default icon
            if photo is None:
                if self.icon_default is not None:
                    photo = self.icon_default
                else:
                    img = Image.new("RGBA", (40, 40), (180, 180, 180, 255))
                    photo = ImageTk.PhotoImage(img)

            self.plant_thumbs.append(photo)

            item_id = self.plant_tree.insert("", "end", text=p["name"], image=photo)
            self.tree_items.append(item_id)


# ---------- RUN APP ----------

if __name__ == "__main__":
    root = tk.Tk()
    app = MyPlantPal(root)
    root.mainloop()
