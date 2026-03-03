My Plant Pal
My Plant Pal is a desktop application built with Python and Tkinter that helps users track their houseplants, watering schedules, sunlight needs, and overall plant health. It includes a modern UI, dark/light themes, toast notifications, image support, and a dashboard with helpful stats.

|---------------------------------------------------------------|

Features
Plant Management
Add plants with:

Name

Watering frequency (days)

Sunlight level (Low / Medium / High)

Optional plant image

View plant details, including last watered date

Mark plants as watered

Delete plants

Save and load plant data automatically (plants.json)

Dashboard Overview
Total number of plants

Plants needing water today

Overdue plants

Visual health bar showing:

Healthy

Due today

Overdue

Plant List Page
Search bar with live filtering

Treeview list with plant thumbnails

Hover highlight and selection highlight

Buttons for Add, Details, Delete, and Save

Themes:
Fully supports Dark Mode and Light Mode

Theme toggle updates all UI elements dynamically

Notifications
Custom toast pop‑ups for:

Errors

Success messages

Watering reminders

Watering Reminders
On startup, the app checks which plants need water today or are overdue

Displays a toast notification listing them

Screenshots (Optional)
You can add screenshots here later, e.g.:

|---------------------------------------------------------------|

Code
/images/
    add.png
    delete.png
    leaf.png
    water.png
    default.png

|---------------------------------------------------------------|
Installation

Requirements
Python

Pillow (PIL)

Tkinter (included with most Python installations)

Install dependencies
bash
pip install pillow

|---------------------------------------------------------------|

 Running the App
Run the main script:

bash
python my_plant_pal.py
Make sure your folder structure looks like:

Code
MyPlantPal/
│── my_plant_pal.py
│── plants.json        (auto-created)
│── images/
│     ├── add.png
│     ├── delete.png
│     ├── leaf.png
│     ├── water.png
│     └── default.png

|---------------------------------------------------------------|

Project Structure
Code
my_plant_pal.py        # Main application
plants.json            # Saved plant data
images/                # Icons and default plant image
How It Works
Data Storage
Plants are stored in a JSON file:

json
{
  "name": "Aloe Vera",
  "water": 7,
  "sun": "High",
  "image": "path/to/image.jpg",
  "last_watered": "2026-03-03"
}
Watering Logic
last_watered + water (days) = next due date

If today > due → Overdue

If today == due → Needs water today

Otherwise → Healthy

Search Filtering
Typing in the search bar instantly filters the plant list by name.

Themes
The app includes two theme dictionaries:

LIGHT_THEME

DARK_THEME

Switching themes updates:

Backgrounds

Buttons

Text

Treeview colors

Entry fields

|---------------------------------------------------------------|