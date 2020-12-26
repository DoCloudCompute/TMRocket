import math
import matplotlib.pyplot as plt

# constants
cons_airRho = float(1.293) # in kg/m³
cons_atm = float(1.01325e5) # in Pa
cons_adbiatic_idx =  1.4
cons_grav = 9.81

# vars
height = 0 # in meters
mass = 0.171 # in kg
speed = 0 # in m/s
tank_capacity = 1.5 # in liters
nozzle_area = math.pi * 0.0045**2

drag_coeff = 0.75 # drag coefficient given by CFD
vis_section = math.pi * 0.05**2 # apparent section of the rocket (5 cm radius in this case)

fuel_rho = 998 # in g/L (or kg/m³)
fuel_vol = int(input("fuel %? [51%]") or 51)
#fuel_vol =  30 # in % of the tank's capacity

tank_pres = 4*cons_atm
tank_vol = 100-fuel_vol # in % of the tank's capacity

delta_t = 0.0001 # in secs
sim_time = 0 # in secs
max_time = 10 # in secs

# plot lists
timelst = []
pllst1 = []
pllst2 = []
pllst3 = []
pllst4 = []
optlst = []

fuel_vol = (fuel_vol/100) * tank_capacity
init_fuel_vol = fuel_vol
tank_vol = (tank_vol/100) * tank_capacity
adbiatic_constant = tank_pres * tank_vol ** cons_adbiatic_idx

# funcs
def get_fuel_vol(fuel_vol, fuel_flow, delta_t):
	# returns the new quant of fuel in liters
	return max([0, fuel_vol - (fuel_flow*delta_t)]) # clamps min value to 0

def get_fuel_mass(fuel_vol, fuel_rho):
	# returns fuel mass in kg
	return fuel_vol*fuel_rho / 1000

def get_fuel_flow(fuel_rho, tank_pres, tank_vol, nozzle_area, delta_t, fuel_vol):
	if tank_pres-cons_atm < 0 or fuel_vol == 0:
		exit_spd = 0
	else:
		exit_spd = 0.97 * math.sqrt(2 *(tank_pres-cons_atm)/fuel_rho)
	exit_flow = nozzle_area * exit_spd * 1000

	newtank_vol = tank_vol+(exit_flow*delta_t)
	newtank_pres = adbiatic_constant / (newtank_vol ** cons_adbiatic_idx)

	return exit_flow, newtank_vol, newtank_pres, exit_spd

def get_curr_thrust(fuel_flow, fuel_rho, delta_t, fuel_spd):
	if round(fuel_mass, 5) == 0:
		return 0 # if out of fuel, no thrust
	else:
		exit_fuel_mass = fuel_flow*delta_t*fuel_rho/1000
		return exit_fuel_mass*fuel_spd/delta_t

def get_drag(drag_coeff, speed, vis_section):
	if speed >= 0:
		return 0.5 * drag_coeff * vis_section * cons_airRho * (speed**2)
	else:
		return 0.5 * drag_coeff * vis_section * cons_airRho * (speed**2) * -1

def get_curr_push(grav, thrust, mass, fuel_mass, drag):
	weight = (mass+fuel_mass)*grav # F=m.a
	return thrust-(weight+drag)

def get_spd(push_force, fuel_mass, mass, delta_t, speed, height):
	if height == 0: return 0
	else:
		r_mass = fuel_mass + mass
		acc = push_force/r_mass
		return acc*delta_t+speed

def get_disp(push_force, fuel_mass, mass, delta_t, height, speed):
	r_mass = fuel_mass + mass
	acc = push_force/r_mass
	disp = (0.5 * acc * delta_t**2) + (speed*delta_t) + (height) # x = 0.5.at²+x0
	return max([0, disp]) # clamp min at 0

capped = False

# time loop
while sim_time < max_time:
	fuel_flow, tank_vol, tank_pres, fuel_spd = get_fuel_flow(fuel_rho, tank_pres, tank_vol, nozzle_area, delta_t, fuel_vol)

	fuel_vol = get_fuel_vol(fuel_vol, fuel_flow, delta_t)
	fuel_mass = get_fuel_mass(fuel_vol, fuel_rho)
	thrust = get_curr_thrust(fuel_flow, fuel_rho, delta_t, fuel_spd)
	drag = get_drag(drag_coeff, speed, vis_section)
	push_force = get_curr_push(cons_grav, thrust, mass, fuel_mass, drag)
	height = get_disp(push_force, fuel_mass, mass, delta_t, height, speed)
	speed = get_spd(push_force, fuel_mass, mass, delta_t, speed, height)

	if height == 0 and sim_time != 0 and not capped:
		max_time = sim_time + 1
		capped = True

	timelst.append(sim_time)
	pllst1.append(speed)
	pllst2.append(drag)
	pllst3.append(height)
	pllst4.append(thrust)
	sim_time+=delta_t

print("{}% of fuel left | air tank pressure: {} atm | apogee: {}m | max speed: {}m/s".format(round(100*fuel_vol/init_fuel_vol, 2), round(tank_pres/cons_atm, 2), round(max(pllst3),2), round(max(pllst1),2)))


plt.plot(timelst, pllst1, label="speed")
plt.plot(timelst, pllst2, label="drag")
plt.plot(timelst, pllst3, label="height")
plt.plot(timelst, pllst4, label="thrust")
plt.legend()
plt.show()
