import math
import matplotlib.pyplot as plt

# constants
cons_G = float(6.6738e-11) # in N.m².kg⁻²
cons_EarthMass = float(5.972e24) # in kg
cons_EarthRadi = float(6.371e6) # in meters
cons_airRho = float(1.293) # in kg/m³
cons_atm = float(1.01325e5) # in Pa

def get_curr_grav(height):
	# returns the current acceleration of gravity in m.s⁻²
	return (cons_G*cons_EarthMass)/(cons_EarthRadi + height)**2
	
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
	newtank_pres = tank_pres*tank_vol/newtank_vol
	
	return exit_flow, newtank_vol, newtank_pres, exit_spd
	
def get_curr_thrust(fuel_flow, fuel_rho, delta_t, fuel_spd, fuel_mass):
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

def rerun(nozzle_rad):
	# vars
	height = 0 # in meters
	mass = 0.2 # in kg
	speed = 0 # in m/s
	tank_capacity = 1.5 # in liters
	nozzle_area = math.pi * nozzle_rad**2

	drag_coeff = 0.75 # drag coefficient given by CFD
	vis_section = math.pi * 0.05**2 # apparent section of the rocket (5 cm radius in this case)

	fuel_vol = 51
	fuel_rho = 998 # in g/L (or kg/m³)

	tank_pres = 6*cons_atm
	tank_vol = 100-fuel_vol # in % of the tank's capacity

	delta_t = 0.000001 # in secs
	sim_time = 0 # in secs
	max_time = 10 # in secs

	# plot lists
	timelst = []
	pllst1 = []
	pllst2 = []
	pllst3 = []
	pllst4 = []

	fuel_vol = (fuel_vol/100) * tank_capacity
	init_fuel_vol = fuel_vol
	tank_vol = (tank_vol/100) * tank_capacity

	capped = False

	# time loop	
	while sim_time < max_time:
		grav = get_curr_grav(height)
		fuel_flow, tank_vol, tank_pres, fuel_spd = get_fuel_flow(fuel_rho, tank_pres, tank_vol, nozzle_area, delta_t, fuel_vol)
		
		fuel_vol = get_fuel_vol(fuel_vol, fuel_flow, delta_t)
		fuel_mass = get_fuel_mass(fuel_vol, fuel_rho)
		thrust = get_curr_thrust(fuel_flow, fuel_rho, delta_t, fuel_spd, fuel_mass)
		drag = get_drag(drag_coeff, speed, vis_section)
		push_force = get_curr_push(grav, thrust, mass, fuel_mass, drag)
		height = get_disp(push_force, fuel_mass, mass, delta_t, height, speed)
		speed = get_spd(push_force, fuel_mass, mass, delta_t, speed, height)
		
		
		timelst.append(sim_time)
		pllst1.append(speed)
		pllst2.append(drag)
		pllst3.append(push_force)
		pllst4.append(thrust)
		if thrust == 0: return max(pllst2)
		sim_time+=delta_t

	#print("{}% of fuel left | air tank pressure: {} atm | apogee: {}m | max speed: {}m/s".format(round(100*fuel_vol/init_fuel_vol, 2), round(tank_pres/cons_atm, 2), round(max(pllst3),2), round(max(pllst1),2)))
	return max(pllst2)

optlst = []
xlst = []

#for i in range(10,40,1):
#	i = i/10000
#	apogee = rerun(i)
#	print(i, apogee)
#	optlst.append(apogee)
#	xlst.append(i)
#print("going faster")
for i in range(3,25,1):
	i = i/1000
	apogee = rerun(i)
	print(i, apogee)
	optlst.append(apogee)
	xlst.append(i)

plt.plot(xlst, optlst, label="Drag in Newtons")
plt.title('Nozzle radius vs Drag')
plt.ylabel('Drag in Newtons')
plt.xlabel('Nozzle radius in meters')
plt.legend()
plt.show()
