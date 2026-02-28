import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import json, os
from datetime import datetime, timedelta

# ---------- THEMES ----------
LIGHT_THEME = {
    "bg_main": "#FAFAFA", "bg_panel": "#F0F0F0",
    "header_bg": "#E0E0E0", "header_text": "#333333",
    "btn": "#8BC34A", "btn_hover": "#7CB342",
    "btn_text": "#FFFFFF", "text": "#333333",
    "accent": "#DCEDC8", "list_bg": "#F0F0F0",
    "list_fg": "#333333"
}

DARK_THEME = {
    "bg_main": "#121212", "bg_panel": "#1E1E1E",
    "header_bg": "#1F2933", "header_text": "#E5E5E5",
    "btn": "#4CAF50", "btn_hover": "#66BB6A",
    "btn_text": "#FFFFFF", "text": "#E5E5E5",
    "accent": "#2E7D32", "list_bg": "#1E1E1E",
    "list_fg": "#E5E5E5"
}

THEME = LIGHT_THEME.copy()


def load_icon(filename, size):
    path = os.path.join("images", filename)
    if not os.path.exists(path):
        return None
    return ImageTk.PhotoImage(Image.open(path).resize(size, Image.LANCZOS))


class MyPlantPal:
    def __init__(self, root):
        self.root = root
        self.root.title("My Plant Pal")
        self.current_theme = "light"

        self.plants = []
        self.buttons = []
        self.tree_items = []
        self.plant_thumbs = []

        # Icons
        self.icon_add = load_icon("add.png", (20, 20))
        self.icon_delete = load_icon("delete.png", (20, 20))
        self.icon_leaf = load_icon("leaf.png", (20, 20))
        self.icon_water = load_icon("water.png", (20, 20))
        self.icon_default = load_icon("default.png", (40, 40))

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

        self.dark_mode_btn = self._header_button("Dark Mode", self.toggle_theme)
        self.dark_mode_btn.pack(side="right", padx=10)

        # ---------- PAGES ----------
        self.dashboard_frame = tk.Frame(self.root, bg=THEME["bg_main"])
        self.plants_frame = tk.Frame(self.root, bg=THEME["bg_main"])

        # Show dashboard first
        self.dashboard_frame.pack(fill="both", expand=True)

        # Build UI pages
        self.build_dashboard()
        self.build_plants_page()

        # Load data AFTER pages exist
        self.load_plants()
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

    # ---------- THEME ----------
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
            c = tk.Frame(card_frame, bg="white", padx=20, pady=15)
            c.pack(side="left", padx=10)
            tk.Label(c, text=value, font=("Arial", 20, "bold"), fg=color, bg="white").pack()
            tk.Label(c, text=label, font=("Arial", 10), fg="#555", bg="white").pack()

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
                           bg=THEME["bg_panel"], highlightthickness=0)
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
        today = datetime.now().date()
        total = len(self.plants)
        today_due = overdue = healthy = 0

        for p in self.plants:
            last = datetime.strptime(p["last_watered"], "%Y-%m-%d").date()
            due = last + timedelta(days=p["water"])
            if today > due:
                overdue += 1
            elif today == due:
                today_due += 1
            else:
                healthy += 1

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

        self.plant_tree = ttk.Treeview(self.plants_frame, style="PlantTreeview", show="tree")
        self.plant_tree.pack(fill="both", expand=True, pady=5)

        btns = tk.Frame(self.plants_frame, bg=THEME["bg_main"])
        btns.pack(pady=10)

        self._create_button(btns, "Add Plant", self.add_plant_window, self.icon_add).grid(row=0, column=0, padx=5)
        self._create_button(btns, "Details", self.show_details).grid(row=0, column=1, padx=5)
        self._create_button(btns, "Delete", self.delete_plant, self.icon_delete).grid(row=0, column=2, padx=5)

        self._create_button(self.plants_frame, "Save Plants", self.save_plants).pack(pady=5)

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

        self._create_button(win, "Browse", browse_img).grid(row=3, column=2, padx=5)

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

            self.plants.append({
                "name": name,
                "water": int(water),
                "sun": sun,
                "image": img,
                "last_watered": datetime.now().strftime("%Y-%m-%d")
            })
            self.update_list()
            self.build_dashboard()
            win.destroy()

        self._create_button(win, "Save Plant", save).grid(row=4, column=0, columnspan=3, pady=10)

    # ---------- DETAILS ----------
    def show_details(self):
        if not hasattr(self, "plant_tree"):
            return
        selected = self.plant_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Pick a plant first.")
            return

        index = self.tree_items.index(selected[0])
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
            self.build_dashboard()

        self._create_button(win, "Mark as Watered", mark_as_watered, self.icon_water).pack(pady=5)
        self._create_button(win, "Close", win.destroy).pack(pady=10)

    # ---------- DELETE ----------
    def delete_plant(self):
        if not hasattr(self, "plant_tree"):
            return
        selected = self.plant_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select a plant to delete.")
            return
        index = self.tree_items.index(selected[0])
        del self.plants[index]
        self.update_list()
        self.build_dashboard()

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

    # ---------- UPDATE LIST ----------
    def update_list(self):
        # Prevent crash if TreeView isn't built yet
        if not hasattr(self, "plant_tree") or self.plant_tree is None:
            return

        for item in self.plant_tree.get_children():
            self.plant_tree.delete(item)

        self.tree_items = []
        self.plant_thumbs = []

        for p in self.plants:
            img_path = p.get("image")
            photo = None

            if img_path and os.path.exists(img_path):
                try:
                    img = Image.open(img_path).resize((40, 40), Image.LANCZOS)
                    photo = ImageTk.PhotoImage(img)
                except:
                    photo = None

            # If no image loaded, try default icon
            if photo is None and self.icon_default is not None:
                photo = self.icon_default

            self.plant_thumbs.append(photo)

            if photo is not None:
                item_id = self.plant_tree.insert("", "end", text=p["name"], image=photo)
            else:
                # No valid image at all: insert without image
                item_id = self.plant_tree.insert("", "end", text=p["name"])

            self.tree_items.append(item_id)


if __name__ == "__main__":
    root = tk.Tk()
    app = MyPlantPal(root)
    root.mainloop()
