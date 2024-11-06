from __init__ import *

def plot_mission(log_file_path):
    with open(log_file_path) as file:
        mission_log = json.load(file)

    # Mission Profile Window
    fig1, axs1 = plt.subplots(2, 2, figsize=(12, 8))
    fig1.suptitle('Mission Profile')

    # Altitude
    axs1[0, 0].plot(np.array(mission_log['timestamp'])/60, mission_log['altitude'], label='Altitude')
    axs1[0, 0].set_title('Altitude')
    axs1[0, 0].set_xlabel('Time (min)')
    axs1[0, 0].set_ylabel('Altitude (m)')
    axs1[0, 0].legend()

    # Airspeed and Groundspeed with secondary y-axis for km/hr
    # Airspeed and Groundspeed with secondary y-axis for km/hr
    ax1 = axs1[0, 1]
    ax1.plot(np.array(mission_log['timestamp'])/60, mission_log['airspeed'], label='Airspeed (m/s)')
    ax1.plot(np.array(mission_log['timestamp'])/60, mission_log['groundspeed'], label='Groundspeed (m/s)')
    ax1.set_title('Airspeed and Groundspeed')
    ax1.set_xlabel('Time (min)')
    ax1.set_ylabel('Speed (m/s)')
    ax1.legend(loc='upper left')

    # Add secondary y-axis for km/hr without re-plotting airspeed
    ax2 = ax1.twinx()
    ax2.set_ylabel('Speed (km/hr)')
    ax2.set_ylim(ax1.get_ylim()[0] * 3.6, ax1.get_ylim()[1] * 3.6)  # Adjust y-limits accordingly

    # Climb Rate
    axs1[1, 0].plot(np.array(mission_log['timestamp'])/60, mission_log['climb_rate'], label='Climb rate')
    axs1[1, 0].set_title('Climb rate')
    axs1[1, 0].set_xlabel('Time (min)')
    axs1[1, 0].set_ylabel('Climb rate (m/s)')
    axs1[1, 0].legend()

    # Distance Covered
    axs1[1, 1].plot(np.array(mission_log['timestamp'])/60, mission_log['distance_covered'], label='Distance covered')
    axs1[1, 1].set_title('Distance covered')
    axs1[1, 1].set_xlabel('Time (min)')
    axs1[1, 1].set_ylabel('Distance (m)')
    axs1[1, 1].legend()

    # Adjust layout for Mission Profile
    fig1.tight_layout(rect=[0, 0, 1, 0.96])

    # Weight and Power Window
    fig2, axs2 = plt.subplots(2, 2, figsize=(12, 8))
    fig2.suptitle('Weight and Power')

    # Gross Weight and Fuel Weight
    axs2[0, 0].plot(np.array(mission_log['timestamp'])/60, mission_log['gross_weight'], label='Gross weight')
    axs2[0, 0].plot(np.array(mission_log['timestamp'])/60, mission_log['fuel_weight'], label='Fuel weight')
    axs2[0, 0].set_title('Gross weight and fuel weight')
    axs2[0, 0].set_xlabel('Time (min)')
    axs2[0, 0].set_ylabel('Weight (kg)')
    axs2[0, 0].legend()

    # Fuel Burn Rate
    axs2[0, 1].plot(np.array(mission_log['timestamp'])/60, np.array(mission_log['fuel_burn_rate']) * 1000, label='Fuel burn rate')
    axs2[0, 1].set_title('Fuel burn rate')
    axs2[0, 1].set_xlabel('Time (min)')
    axs2[0, 1].set_ylabel('Fuel burn rate (g/s)')
    axs2[0, 1].legend()

    # Power Required and Power Available
    axs2[1, 0].plot(np.array(mission_log['timestamp'])/60, np.array(mission_log['power_required']) / 1000, label='Power required')
    axs2[1, 0].plot(np.array(mission_log['timestamp'])/60, np.array(mission_log['power_available']) / 1000, label='Power available')
    axs2[1, 0].set_title('Power required and power available')
    axs2[1, 0].set_xlabel('Time (min)')
    axs2[1, 0].set_ylabel('Power (kW)')
    axs2[1, 0].legend()

    # Hide the last unused subplot
    axs2[1, 1].axis('off')

    # Adjust layout for Weight and Power
    fig2.tight_layout(rect=[0, 0, 1, 0.96])

    # Display both windows
    plt.show()

plot_mission('output_files/mission_A_results.json')