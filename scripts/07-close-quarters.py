LANE_WIDTH = 4.0

from environs import Env
from lgsvl.geometry import Vector
import lgsvl
import time

env = Env()

sim = lgsvl.Simulator(env.str("LGSVL__SIMULATOR_HOST", "127.0.0.1"), env.int("LGSVL__SIMULATOR_PORT", 8181))
if sim.current_scene == "SanFrancisco":
    sim.reset()
else:
    sim.load("SanFrancisco")

spawns = sim.get_spawn()

state = lgsvl.AgentState()
state.transform = spawns[0]

forward = lgsvl.utils.transform_to_forward(spawns[0])
right = lgsvl.utils.transform_to_right(spawns[0])

state.transform.position = Vector(-165,10,-120)
state.transform.rotation.y -= 90

#testing
#state.transform.position = Vector(-190,10,20) # + LANE_WIDTH * right
#state.transform.rotation.y += 180 

ego = sim.add_agent("2e9095fa-c9b9-4f3f-8d7d-65fa2bb03921", lgsvl.AgentType.EGO, state)

forward = lgsvl.utils.transform_to_forward(spawns[0])
right = lgsvl.utils.transform_to_right(spawns[0])





INITIAL_PED_DISTANCE_AHEAD = 100

wp = []
state = lgsvl.AgentState()
spawns = sim.get_spawn()
ped_initial_pos = Vector(-172, 10, -44)
wp.append(
    lgsvl.WalkWaypoint(ped_initial_pos, idle=1, speed=3)
)
wp.append(
    lgsvl.WalkWaypoint( Vector(-172, 10, -22), idle=0, speed=3)
)

wp.append(
    lgsvl.WalkWaypoint( Vector(-172, 10, -25), idle=0.5, speed=3)
)

wp.append(
    lgsvl.WalkWaypoint( Vector(-172, 10, -30), idle=0.1, speed=3)
)
state = lgsvl.AgentState()
state.transform.position = ped_initial_pos
p = sim.add_agent("Pamela", lgsvl.AgentType.PEDESTRIAN, state)
# # This sends the list of waypoints to the pedestrian. The bool controls whether or not the pedestrian will continue walking (default false)
p.follow(wp, True)

wp = []
state = lgsvl.AgentState()
spawns = sim.get_spawn()
ped_initial_pos = Vector(-174, 10, -22)
wp.append(
    lgsvl.WalkWaypoint(ped_initial_pos, idle=1, speed=3)
)

wp.append(
    lgsvl.WalkWaypoint( Vector(-174, 10, -25), idle=0.5, speed=3)
)

wp.append(
    lgsvl.WalkWaypoint( Vector(-174, 10, -30), idle=0, speed=3)
)
wp.append(
    lgsvl.WalkWaypoint( Vector(-175, 10, -44), idle=0, speed=3)
)
state = lgsvl.AgentState()
state.transform.position = ped_initial_pos
p = sim.add_agent("Johny", lgsvl.AgentType.PEDESTRIAN, state)
# # This sends the list of waypoints to the pedestrian. The bool controls whether or not the pedestrian will continue walking (default false)
p.follow(wp, True)

wp = []
state = lgsvl.AgentState()
spawns = sim.get_spawn()
ped_initial_pos = Vector(-174, 10, -21)
wp.append(
    lgsvl.WalkWaypoint(ped_initial_pos, idle=5, speed=2)
)

wp.append(
    lgsvl.WalkWaypoint( Vector(-174, 10, -25), idle=0, speed=2)
)

wp.append(
    lgsvl.WalkWaypoint( Vector(-174, 10, -30), idle=0, speed=2)
)
wp.append(
    lgsvl.WalkWaypoint( Vector(-175, 10, -48), idle=2, speed=2)
)
state = lgsvl.AgentState()
state.transform.position = ped_initial_pos
p = sim.add_agent("EntrepreneurFemale", lgsvl.AgentType.PEDESTRIAN, state)
# # This sends the list of waypoints to the pedestrian. The bool controls whether or not the pedestrian will continue walking (default false)
p.follow(wp, True)


## -- Apollo Setup -- ##

print("Bridge connected:", ego.bridge_connected)
#Connect to Apollo bridge
ego.connect_bridge(env.str("LGSVL__AUTOPILOT_0_HOST", lgsvl.wise.SimulatorSettings.bridge_host), env.int("LGSVL__AUTOPILOT_0_PORT", lgsvl.wise.SimulatorSettings.bridge_port))
while not ego.bridge_connected:
    time.sleep(1)
print("Bridge connected:", ego.bridge_connected)

#Connect to Dreamview to control Apollo
dv = lgsvl.dreamview.Connection(sim, ego, ip="localhost", port="8888")
dv.set_hd_map("san_fransisco")
dv.set_vehicle("Lincoln2017MKZ_LGSVL")
modules = [
    "Localization",
    "Transform",
    "Perception",
    "Traffic Light",
    "Planning",
    "Prediction",
    "Camera",
    "Routing",
    "Control"
]

#Set a destination for apollo (straight ahead, to next intersection)
state = lgsvl.AgentState()
state.transform.position = Vector(-30,10,-126)
destination = state.transform.position
dv.setup_apollo(destination.x, destination.z, modules)

sim.run()
