# Product: GUI developed for Helicopter Simulation on behalf of Rotary Wing Aerodynamics Course
# Note: Comments starts from # (hashtag) or just for understanding, string comments between """_""" 3 double inverted commas are important comments and instructions made for smooth handling


import tkinter as tk                                 # Importing tkinter library for GUI development
from tkinter import messagebox                       # Importing messagebox from tkinter for displaying alerts
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg  # Importing FigureCanvasTkAgg for embedding matplotlib plots in tkinter
import matplotlib.pyplot as plt                      # Importing matplotlib for plotting graphs
from PIL import Image, ImageTk                       # Importing Image and ImageTk from PIL to handle image processing
""" Import your functions data here, from your_file_name import your_class_name_in_file. If the functions are  
written using non-oops concept, you try with this command from your_file_name import * """
from New_dummy_data import SimulationData            # Importing dummy data developed under SimulationData class 

root = tk.Tk()                                       # Creating the main window for the application
""" Change SimulationData() class to your respective class """
sim_data = SimulationData('input_files/heli.json','input_files/fbd.json',13.89,0.002,2000)                          # Creating an instance of the SimulationData class
plots_data = {}                                      # Initialize a dictionary to store data for the plots
graph_var1 = tk.StringVar(value="Forces X")          # Creating a StringVar to hold the selected graph type for the first plot
graph_var2 = tk.StringVar(value="Moments X")         # Creating a StringVar to hold the selected graph type for the second plot
auto_run = tk.BooleanVar(value=False)                # Creating a BooleanVar to hold the state of the auto-run checkbox

""" This is the important function where you are connecting your defined force and moment functions """
def run_simulation():
    #Runs simulation and update plots
    try:
        # Get values from sliders
        collective_pitch = float(collective_pitch_entry.get())
        lateral_pitch = float(lateral_pitch_entry.get())
        longitudinal_pitch = float(longitudinal_pitch_entry.get())
        tail_rotor_collective = float(tail_rotor_collective_entry.get())

        """ Connect your functions here properly, in this example, sim_dat.generate_force_x is function called from sim_data class named generate_force_x
         which can take the inputs(arguments) of collective_pitch, lateral_pitch, longitudinal_pitch and tail_rotor_collective """
        # Generates simulation data for different forces and moments
        plots_data["Forces X"] = sim_data.generate_forces_x(collective_pitch, lateral_pitch, longitudinal_pitch, tail_rotor_collective)
        plots_data["Forces Y"] = sim_data.generate_forces_y(collective_pitch, lateral_pitch, longitudinal_pitch, tail_rotor_collective)
        plots_data["Forces Z"] = sim_data.generate_forces_z(collective_pitch, lateral_pitch, longitudinal_pitch, tail_rotor_collective)
        plots_data["Forces XYZ"] = sim_data.generate_forces_xyz(collective_pitch, lateral_pitch, longitudinal_pitch, tail_rotor_collective)
        plots_data["Moments X"] = sim_data.generate_moments_x(collective_pitch, lateral_pitch, longitudinal_pitch, tail_rotor_collective)
        plots_data["Moments Y"] = sim_data.generate_moments_y(collective_pitch, lateral_pitch, longitudinal_pitch, tail_rotor_collective)
        plots_data["Moments Z"] = sim_data.generate_moments_z(collective_pitch, lateral_pitch, longitudinal_pitch, tail_rotor_collective)
        plots_data["Moments XYZ"] = sim_data.generate_moments_xyz(collective_pitch, lateral_pitch, longitudinal_pitch, tail_rotor_collective)

        # Update the plots with the new data
        update_plot(ax1, canvas1, graph_var1.get(),plots_data)
        update_plot(ax2, canvas2, graph_var2.get(), plots_data)

    except ValueError:
        messagebox.showerror("Invalid Input", "Please ensure all input fields are filled with valid numbers.")  # Show error if inputs are invalid



""" Don't change anything from here """
def create_row(frame, from_, to, label_text, rel_y):
    #Creating a row with a label, entry, and slider using relative positioning
    label = tk.Label(frame, text=label_text)                          # Creating a label with specified text
    label.place(relx=0.05, rely=rel_y, relwidth=0.2, relheight=0.05)  # Position the label using relative positioning

    entry = tk.Entry(frame)                                           # Creating an entry widget for user input
    entry.place(relx=0.3, rely=rel_y, relwidth=0.1, relheight=0.05)   # Position the entry widget

    # Creating a slider (Scale) widget with specified range and orientation, updates entry when slider is moved
    slider = tk.Scale(frame, from_=from_, to=to, orient=tk.HORIZONTAL, resolution=0.001,command=lambda v: update_entry_from_slider(v, entry))
    slider.place(relx=0.5, rely=rel_y-0.05, relwidth=0.4, relheight=0.15)  # Position the slider

    # Creating labels to display the minimum and maximum values at the ends of the slider
    min_label = tk.Label(frame, text=f"{from_:.3f}")                        # Label for minimum value
    min_label.place(relx=0.45, rely=rel_y , relwidth=0.05, relheight=0.05)  # Position the minimum value label

    max_label = tk.Label(frame, text=f"{to:.3f}")                           # Label for maximum value
    max_label.place(relx=0.9, rely=rel_y , relwidth=0.05, relheight=0.05)   # Position the maximum value label

    entry.bind("<Return>", lambda event: update_slider_from_entry(entry, slider))  # Bind Return key to update slider when entry is changed
    slider.bind("<Motion>", lambda event: check_auto_run())                        # Bind slider movement to check auto-run functionality

    return entry, slider  # Return the entry and slider for further use

def update_entry_from_slider(var, entry):
    # Update entry field when slider is moved
    entry.delete(0, tk.END)    # Clear the entry field
    entry.insert(0, str(var))  # Insert the slider value into the entry field

def update_slider_from_entry(entry, slider):
    # Update slider position when entry is changed
    try:
        value = float(entry.get())  # Get the value from the entry field and convert it to float
        slider.set(value)           # Set the slider position to the entry value
    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter a valid number.")  # Show error message if input is invalid

def check_auto_run():
    # Auto-run simulation if enabled
    if auto_run.get():    # Check if auto-run is enabled
        run_simulation()  # Run the simulation

def auto_run_toggle():
    # Toggle auto-run functionality
    if auto_run.get():    # Check if auto-run is enabled
        run_simulation()  # Run the simulation

# def update_plot(ax, canvas, graph_type):
#     # Update plot based on selected graph type
#     ax.clear()                         # Clear the current plot
#     if graph_type in plots_data:       # Check if the selected graph type is in the data
#         x, y = plots_data[graph_type]  # Get the x and y data for the selected graph type
#         ax.plot(x, y, label=graph_type)# Plot the data
#     ax.set_title(graph_type)           # Set the plot title to the selected graph type
#     ax.legend()                        # Display the legend
#     canvas.draw()                      # Refresh the canvas to show the updated plot

def update_plot(ax, canvas, graph_type, plots_data):
    """
    Update the plot based on the selected graph type.

    Parameters:
    - ax: The axes of the plot.
    - canvas: The canvas to draw the plot on.
    - graph_type: The type of graph to display.
    - plots_data: A dictionary containing the data for different graph types.
    """
    ax.clear()  # Clear the current plot

    if graph_type in plots_data:
        data = plots_data[graph_type]  # Get the data for the selected graph type

        if len(data) == 2:  # Single y data case
            x, y = data
            ax.plot(x, y, label=graph_type)
        elif len(data) == 4:  # Separate x, y, z components case
            x, force_x, force_y, force_z = data
            ax.plot(x, force_x, label=f'{graph_type} - X')
            ax.plot(x, force_y, label=f'{graph_type} - Y')
            ax.plot(x, force_z, label=f'{graph_type} - Z')
        else:
            raise ValueError("Unexpected data format for plotting")

    ax.set_title(graph_type)  # Set the plot title to the selected graph type
    ax.legend()  # Display the legend
    canvas.draw()  # Refresh the canvas to show the updated plot


def reset_fields():
    # Reset all fields and clear plots
    collective_pitch_slider.set(0)     # Reset collective pitch slider to 0
    lateral_pitch_slider.set(0)        # Reset lateral pitch slider to 0
    longitudinal_pitch_slider.set(0)   # Reset longitudinal pitch slider to 0
    tail_rotor_slider.set(0)           # Reset tail rotor slider to 0
    ax1.clear()                        # Clear the first plot
    ax2.clear()                        # Clear the second plot
    canvas1.draw()                     # Refresh the first canvas
    canvas2.draw()                     # Refresh the second canvas

# GUI Setup
root.title("Rotary Wing Aerodynamics - Helicopter Flight Simulator")  # Set the window title
root.geometry("1600x1000")              # Set the initial window size
root.state('zoomed')                   # Maximize the window

# Load and display image
image = Image.open("heli1.jpg")        # Open the image file
photo = ImageTk.PhotoImage(image)      # Convert the image to a PhotoImage object for tkinter
image_label = tk.Label(root, image=photo)  # Creating a label widget to hold the image
image_label.place(relx=0.02, rely=0.05, relwidth=0.45, relheight=0.4)  # Position the image label

main_frame = tk.Frame(root)            # Creating a frame for input controls
main_frame.place(relx=0.02, rely=0.55, relwidth=0.45, relheight=0.4)  # Position the main frame

# Creating rows for sliders
collective_pitch_entry, collective_pitch_slider = create_row(main_frame, -20, 20, "Collective Pitch (°)", 0.05)
lateral_pitch_entry, lateral_pitch_slider = create_row(main_frame, -20, 20, "Lateral Cyclic Pitch (°)", 0.15)
longitudinal_pitch_entry, longitudinal_pitch_slider = create_row(main_frame, -20, 20, "Longitudinal Cyclic Pitch (°)", 0.25)
tail_rotor_collective_entry, tail_rotor_slider = create_row(main_frame, -20, 20, "Tail Rotor Collective (°)", 0.35)

# Auto-run and reset buttons
auto_run_button = tk.Checkbutton(main_frame, text="Auto-Run", variable=auto_run, command=auto_run_toggle)  # Creating auto-run toggle button
auto_run_button.place(relx=0.4, rely=0.85, relwidth=0.2, relheight=0.06)                                  # Position the auto-run button

run_button = tk.Button(main_frame, text="Run Simulation", command=run_simulation)                          # Creating button to run simulation
run_button.place(relx=0.05, rely=0.85, relwidth=0.2, relheight=0.06)                                        # Position the run button

reset_button = tk.Button(main_frame, text="Reset", command=reset_fields)                                   # Creating button to reset fields
reset_button.place(relx=0.75, rely=0.85, relwidth=0.2, relheight=0.06)                                     # Position the reset button

# Dropdowns for selecting graphs
graph_dropdown1_label = tk.Label(main_frame, text="Select Graph for Window 1:")                            # Creating label for first graph dropdown
graph_dropdown1_label.place(relx=0.0, rely=0.5, relwidth=0.3, relheight=0.06)                            # Position the label
graph_dropdown1 = tk.OptionMenu(main_frame, graph_var1, "Forces X", "Forces Y", "Forces Z", "Forces XYZ", command=lambda _: update_plot(ax1, canvas1, graph_var1.get(),plots_data))  # Creating dropdown menu for first plot selection
graph_dropdown1.place(relx=0.45, rely=0.5, relwidth=0.5, relheight=0.06)                                  # Position the first dropdown menu

graph_dropdown2_label = tk.Label(main_frame, text="Select Graph for Window 2:")                            # Creating label for second graph dropdown
graph_dropdown2_label.place(relx=0.0, rely=0.6, relwidth=0.3, relheight=0.06)                            # Position the label
graph_dropdown2 = tk.OptionMenu(main_frame, graph_var2, "Moments X", "Moments Y", "Moments Z", "Moments XYZ", command=lambda _: update_plot(ax2, canvas2, graph_var2.get(), plots_data))  # Creating dropdown menu for second plot selection
graph_dropdown2.place(relx=0.45, rely=0.6, relwidth=0.5, relheight=0.06)                                  # Position the second dropdown menu

# Frames for plots
plot_frame_1 = tk.Frame(root)                                                                              # Creating frame for the first plot
plot_frame_1.place(relx=0.5, rely=0.05, relwidth=0.45, relheight=0.4)                                      # Position the first plot frame
fig1, ax1 = plt.subplots()                                                                                 # Creating a matplotlib figure and axis for the first plot
canvas1 = FigureCanvasTkAgg(fig1, master=plot_frame_1)                                                     # Creating a canvas widget to hold the first plot
canvas1.get_tk_widget().pack(fill=tk.BOTH, expand=True)                                                    # Pack the canvas in the frame

plot_frame_2 = tk.Frame(root)                                                                              # Creating frame for the second plot
plot_frame_2.place(relx=0.5, rely=0.55, relwidth=0.45, relheight=0.4)                                      # Position the second plot frame
fig2, ax2 = plt.subplots()                                                                                 # Creating a matplotlib figure and axis for the second plot
canvas2 = FigureCanvasTkAgg(fig2, master=plot_frame_2)                                                     # Creating a canvas widget to hold the second plot
canvas2.get_tk_widget().pack(fill=tk.BOTH, expand=True)                                                    # Pack the canvas in the frame

# Main loop
root.mainloop()  # Start the Tkinter event loop to run the application
