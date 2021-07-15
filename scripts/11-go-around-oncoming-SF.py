from math import atan
from environs import Env
from lgsvl.agent import Agent
import lgsvl
import time
import copy

from lgsvl.geometry import Vector

# Constants
LANE_WIDTH = 4.0
CAR_LENGTH = 8.0
ONCOMING_GROUND_HEIGHT = -4.726
EGO_GROUND_HEIGHT = -3.30108

env = Env()
sim = lgsvl.Simulator(env.str("LGSVL__SIMULATOR_HOST", "127.0.0.1"), env.int("LGSVL__SIMULATOR_PORT", 8181))
if sim.current_scene == "SanFrancisco":
    sim.reset()
else:
    sim.load("SanFrancisco")


def on_collision(agent1: Agent, agent2, contact):
  name1 = "STATIC OBSTACLE" if agent1 is None else agent1.name
  name2 = "STATIC OBSTACLE" if agent2 is None else agent2.name
  print("{} collided with {} at {}".format(name1, name2, contact))
  sim.stop()


spawns = sim.get_spawn()
egoInitialState = lgsvl.AgentState()
egoInitialState.transform = spawns[3]
egoInitialState.transform.rotation.y += 180

forward = lgsvl.utils.transform_to_forward(egoInitialState.transform)
right = lgsvl.utils.transform_to_right(egoInitialState.transform)

# Set a destination for Apollo (turn right at the intersection ahead)
destination = egoInitialState.transform.position + (20 * forward) + (80 * right)

egoInitialState.transform.position += LANE_WIDTH * 3 * right
egoInitialState.transform.position -= CAR_LENGTH * 10 * forward

ego = sim.add_agent("2e9095fa-c9b9-4f3f-8d7d-65fa2bb03921", lgsvl.AgentType.EGO, egoInitialState)


# Spawn a vehicle in the oncomming lane, set to begin driving in its lane as the ego approaches a stationary vehicle
oncomingState = copy.deepcopy(egoInitialState)
oncomingState.transform.rotation.y += 180
oncomingState.transform.position -= LANE_WIDTH * 2 * right
oncomingState.transform.position += CAR_LENGTH * 10 * forward
oncomingNPC = sim.add_agent("Sedan", lgsvl.AgentType.NPC, oncomingState)
oncomingNPC.on_collision(on_collision)
oncoming_wp = []

# Setting waypoints for the NPC to encroach into the lane that the ego needs to go in to go around the stationary car
wp_2: Vector = egoInitialState.transform.position - (LANE_WIDTH * right) + (CAR_LENGTH * 7 * forward)
angle = atan((wp_2.x - oncomingState.position.x) / (wp_2.z - oncomingState.position.z)) # Angle calculations to make the waypoint moving look a bit better
angleVector = oncomingState.rotation
angleVector.y -= angle
oncoming_wp.append(lgsvl.DriveWaypoint(oncomingState.transform.position, idle=0, speed=15, trigger_distance=CAR_LENGTH * 10, angle=angleVector))
oncoming_wp.append(lgsvl.DriveWaypoint(wp_2, speed=10, angle=oncomingState.rotation))
oncoming_wp.append(lgsvl.DriveWaypoint(egoInitialState.transform.position - (LANE_WIDTH * right) + (CAR_LENGTH * 4 * forward), speed=10, angle=oncomingState.rotation))
oncoming_wp.append(lgsvl.DriveWaypoint(egoInitialState.transform.position - (LANE_WIDTH * 2 * right), speed=0, angle=oncomingState.transform.rotation))
oncomingNPC.follow(oncoming_wp)


# Spawn a stationary car directly in front of the ego
egoInitialState.transform.position += CAR_LENGTH * 5 * forward
sim.add_agent("Sedan", lgsvl.AgentType.NPC, egoInitialState).on_collision(on_collision)


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

dv.setup_apollo(destination.x, destination.z, modules)

sim.run()