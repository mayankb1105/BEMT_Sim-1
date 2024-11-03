import tkinter as tk
from tkinter import ttk
import json

class MissionPlannerGUI:
    def __init__(self, main_app):
        self.main_app = main_app
        self.window = tk.Toplevel()
        self.window.title("Add Mission Phase")
        self.window.geometry('450x500')
        self.window.configure(bg="#f9f9f9")

        # Mission Type Selection
        mission_frame = ttk.LabelFrame(self.window, text="Mission Details", padding=(15, 10))
        mission_frame.grid(column=0, row=0, padx=20, pady=10, sticky="ew")

        tk.Label(mission_frame, text="Type:").grid(column=0, row=0, sticky="w")
        self.mission_type = tk.StringVar(value="Hover")
        self.mission_type_dropdown = ttk.Combobox(mission_frame, textvariable=self.mission_type, values=["Hover", "Forward Flight", "Climb"])
        self.mission_type_dropdown.grid(column=1, row=0, pady=5, sticky="ew")
        self.mission_type_dropdown.bind("<<ComboboxSelected>>", lambda e: self.update_mission_fields(self.mission_type.get()))

        # Mission Parameters
        tk.Label(mission_frame, text="Mass (kg):").grid(column=0, row=1, sticky="w")
        self.mass = ttk.Entry(mission_frame)
        self.mass.grid(column=1, row=1, pady=5, sticky="ew")

        tk.Label(mission_frame, text="Altitude (m):").grid(column=0, row=2, sticky="w")
        self.altitude = ttk.Entry(mission_frame)
        self.altitude.grid(column=1, row=2, pady=5, sticky="ew")

        tk.Label(mission_frame, text="V_inf (m/s):").grid(column=0, row=3, sticky="w")
        self.v_inf = ttk.Entry(mission_frame)
        self.v_inf.grid(column=1, row=3, pady=5, sticky="ew")

        # Additional fields for specific mission types
        self.time_taken_label = tk.Label(mission_frame, text="Time Taken (s):")
        self.time_taken = ttk.Entry(mission_frame)

        self.distance_traveled_label = tk.Label(mission_frame, text="Distance Traveled (m):")
        self.distance_traveled = ttk.Entry(mission_frame)

        self.altitude_change_label = tk.Label(mission_frame, text="Altitude Change (m):")
        self.altitude_change = ttk.Entry(mission_frame)

        self.climb_rate_label = tk.Label(mission_frame, text="Climb Rate (m/s):")
        self.climb_rate = ttk.Entry(mission_frame)

        self.headwind_label = tk.Label(mission_frame, text="Headwind (m/s):")
        self.headwind = ttk.Entry(mission_frame)

        self.distance_traveled.bind("<FocusOut>", lambda e: self.calculate_time())
        self.time_taken.bind("<FocusOut>", lambda e: self.calculate_distance())

        # Initialize fields for default mission type "Hover"
        self.update_mission_fields("Hover")

    def update_mission_fields(self, mission_type):
        """Update fields based on mission type."""
        # Hide all specific fields initially
        self.time_taken_label.grid_forget()
        self.time_taken.grid_forget()
        self.distance_traveled_label.grid_forget()
        self.distance_traveled.grid_forget()
        self.altitude_change_label.grid_forget()
        self.altitude_change.grid_forget()
        self.climb_rate_label.grid_forget()
        self.climb_rate.grid_forget()
        self.headwind_label.grid_forget()
        self.headwind.grid_forget()
        self.v_inf.config(state="normal")

        if mission_type == "Hover":
            self.v_inf.config(state="disabled")
            self.v_inf.delete(0, tk.END)
            self.v_inf.insert(0, "0")
            self.time_taken_label.grid(column=0, row=4, sticky="w")
            self.time_taken.grid(column=1, row=4, pady=5, sticky="ew")
        
        elif mission_type == "Forward Flight":
            self.headwind_label.grid(column=0, row=5, sticky="w")  # Set to row 5
            self.headwind.grid(column=1, row=5, pady=4, sticky="ew")  # Set to row 5
            self.distance_traveled_label.grid(column=0, row=6, sticky="w")  # Move to row 6
            self.distance_traveled.grid(column=1, row=6, pady=5, sticky="ew")  # Move to row 6
            self.time_taken_label.grid(column=0, row=7, sticky="w")  # Set to row 7
            self.time_taken.grid(column=1, row=7, pady=5, sticky="ew")  # Set to row 7
            self.altitude_change_label.grid(column=0, row=8, sticky="w")  # Move to row 8
            self.altitude_change.grid(column=1, row=8, pady=5, sticky="ew")  # Move to row 8
        
        elif mission_type == "Climb":
            self.v_inf.config(state="disabled")
            self.v_inf.delete(0, tk.END)
            self.v_inf.insert(0, "0")
            self.altitude_change_label.grid(column=0, row=4, sticky="w")
            self.altitude_change.grid(column=1, row=4, pady=5, sticky="ew")
            self.climb_rate_label.grid(column=0, row=5, sticky="w")
            self.climb_rate.grid(column=1, row=5, pady=5, sticky="ew")

    def calculate_time(self):
        """Calculate time based on distance and velocity."""
        try:
            v_inf = float(self.v_inf.get())
            headwind = float(self.headwind.get())
            distance = self.distance_traveled.get()

            if distance:  # If distance is provided, calculate time
                distance_value = float(distance)
                time_value = distance_value / (v_inf - headwind)
                self.time_taken.delete(0, tk.END)
                self.time_taken.insert(0, f"{time_value:.2f}")
        except ValueError:
            # print("Invalid input. Please enter numeric values.")
            pass

    def calculate_distance(self):
        """Calculate distance based on time and velocity."""
        try:
            v_inf = float(self.v_inf.get())
            headwind = float(self.headwind.get())
            time = self.time_taken.get()

            if time:  # If time is provided, calculate distance
                time_value = float(time)
                distance_value = (v_inf - headwind) * time_value
                self.distance_traveled.delete(0, tk.END)
                self.distance_traveled.insert(0, f"{distance_value:.2f}")
        except ValueError:
            # print("Invalid input. Please enter numeric values.")
            pass

    def submit(self):
        """Collect and submit mission data."""
        mission_data = {
            "type": self.mission_type.get(),
            "mass": self.mass.get(),
            "altitude": self.altitude.get(),
            "V_inf": self.v_inf.get(),
            "time_taken": self.time_taken.get() if self.mission_type.get() == "Hover" else "",
            "distance_traveled": self.distance_traveled.get() if self.mission_type.get() == "Forward Flight" else "",
            "altitude_change": self.altitude_change.get() if self.mission_type.get() in ["Forward Flight", "Climb"] else "",
            "climb_rate": self.climb_rate.get() if self.mission_type.get() == "Climb" else "",
            "headwind": self.headwind.get() if self.mission_type.get() == "Forward Flight" else ""
        }
        
        self.main_app.add_mission_data(mission_data)
        self.window.destroy()

class MainWindow:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Mission Planner")
        self.window.geometry('500x650')
        self.window.configure(bg="#f4f4f4")

        # Styling
        self.style = ttk.Style()
        self.style.configure("TLabel", font=("Arial", 10), background="#f9f9f9")
        self.style.configure("TButton", font=("Arial", 10), padding=6, relief="flat", background="#3498db", foreground="black")
        self.style.configure("TEntry", relief="flat")
        self.style.configure("TCombobox", font=("Arial", 10))

        header_label = tk.Label(self.window, text="Mission Planner", font=("Helvetica", 18), bg="#3498db", fg="white", pady=10)
        header_label.grid(column=0, row=0, pady=20, columnspan=2, sticky="nsew")

        # Temp deviation and fuel
        tk.Label(self.window, text="Temp Deviation from ISA (°C):").grid(column=0, row=1, sticky="w", padx=20, pady=10)
        self.temp_dev_isa = ttk.Entry(self.window)
        self.temp_dev_isa.grid(column=1, row=1, padx=20, pady=10, sticky="ew")

        tk.Label(self.window, text="Initial Fuel (kg):").grid(column=0, row=2, sticky="w", padx=20, pady=10)
        self.fuel = ttk.Entry(self.window)
        self.fuel.grid(column=1, row=2, padx=20, pady=10, sticky="ew")

        # Filename Entry
        tk.Label(self.window, text="Filename:").grid(column=0, row=3, sticky="w", padx=20, pady=10)
        self.filename_entry = ttk.Entry(self.window)
        self.filename_entry.insert(0, "mission_data.json")  # Default filename
        self.filename_entry.grid(column=1, row=3, padx=20, pady=10, sticky="ew")

        # Add maneuver button
        self.add_maneuver_button = ttk.Button(self.window, text="Add Mission Phase", command=self.add_maneuver, style="TButton")
        self.add_maneuver_button.grid(column=0, row=4, padx=20, pady=10, sticky="ew")

        # Listbox for maneuvers and save button (rest of the code remains the same)
        maneuvers_frame = ttk.LabelFrame(self.window, text="Mission Phases", padding=(10, 10))
        maneuvers_frame.grid(column=0, row=5, padx=20, pady=10, sticky="nsew", columnspan=2)

        self.maneuvers_listbox = tk.Listbox(maneuvers_frame, height=15, width=70, selectmode=tk.SINGLE)
        self.maneuvers_listbox.grid(row=0, column=0, sticky="nsew", pady=(0, 5))

        self.scrollbar = ttk.Scrollbar(maneuvers_frame, orient="vertical", command=self.maneuvers_listbox.yview)
        self.maneuvers_listbox.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.grid(row=0, column=1, sticky="ns")

        self.delete_button = ttk.Button(self.window, text="Delete Selected", command=self.delete_maneuver, style="TButton")
        self.delete_button.grid(column=0, row=6, padx=20, pady=10, sticky="ew")

        self.save_button = ttk.Button(self.window, text="Save Mission Data to JSON", command=self.save_to_json, style="TButton")
        self.save_button.grid(column=1, row=6, padx=20, pady=10, sticky="ew")

        self.maneuvers = []
        self.window.mainloop()

    def add_maneuver(self):
        MissionPlannerGUI(self)

    def add_mission_data(self, mission_data):
        self.maneuvers.append(mission_data)
        self.update_maneuvers_listbox()

    def update_maneuvers_listbox(self):
        self.maneuvers_listbox.delete(0, tk.END)
        for mission in self.maneuvers:
            detail = f"Type={mission['type']}, Mass={mission['mass']} kg, Altitude={mission['altitude']} m, V_inf={mission['V_inf']} m/s"
            if mission["type"] == "Hover":
                detail += f", Time Taken={mission['time_taken']} s"
            elif mission["type"] == "Forward Flight":
                detail += f", Distance={mission['distance_traveled']} m, Altitude Change={mission['altitude_change']} m, Headwind={mission['headwind']} m/s"
            elif mission["type"] == "Climb":
                detail += f", Altitude Gained={mission['altitude_change']} m, Climb Rate={mission['climb_rate']} m/s"
            self.maneuvers_listbox.insert(tk.END, detail)

    def delete_maneuver(self):
        selected_index = self.maneuvers_listbox.curselection()
        if selected_index:
            del self.maneuvers[selected_index[0]]
            self.update_maneuvers_listbox()

    def save_to_json(self):
        mission_data = {
            "temp_dev_isa": self.temp_dev_isa.get(),
            "fuel": self.fuel.get(),
            "mission_phases": self.maneuvers
        }
        filename = self.filename_entry.get()  # Get the filename from the entry box
        with open(filename, "w") as f:
            json.dump(mission_data, f, indent=4)

# Run the main application
MainWindow()