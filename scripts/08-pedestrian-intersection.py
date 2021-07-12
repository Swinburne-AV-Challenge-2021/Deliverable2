from environs import Env
from lgsvl.geometry import Vector
import lgsvl
import time
import copy

# Constants
LANE_WIDTH = 4.0
CAR_LENGTH = 8.0
NPC_COLOR = Vector(68, 168, 50)
MAX_CAR_LINE = 10

# Paramters for Metamorphic Testing # input ranges
pedDistanceFromIntersection = 9 # Meters from the start of the crossing (>= 0), values more than 0 mean spawns back a bit
pedSpeed = 8 # 0 - 10
pedTrigger = 24 # > 0
timeOfDay = 12 # [0, 24)
weatherQuality = 0 # [0.0, 1.0] 0 is good quality, 1 is bad, worst conditions


def on_collision(agent1, agent2, contact):
  name1 = "STATIC OBSTACLE" if agent1 is None else agent1.name
  name2 = "STATIC OBSTACLE" if agent2 is None else agent2.name
  print("{} collided with {} at {}".format(name1, name2, contact))
  lgsvl.simulator.Simulator.close()


env = Env()
sim = lgsvl.Simulator(env.str("LGSVL__SIMULATOR_HOST", "127.0.0.1"), env.int("LGSVL__SIMULATOR_PORT", 8181))
if sim.current_scene == "SanFrancisco":
    sim.reset()
else:
    sim.load("SanFrancisco")

spawns = sim.get_spawn()

egoInitialState = lgsvl.AgentState()
egoInitialState.transform = spawns[1]

forward = lgsvl.utils.transform_to_forward(egoInitialState.transform)
right = lgsvl.utils.transform_to_right(egoInitialState.transform)

egoInitialState.transform.position -= LANE_WIDTH * right

ego = sim.add_agent("2e9095fa-c9b9-4f3f-8d7d-65fa2bb03921", lgsvl.AgentType.EGO, egoInitialState)


# -- Leftside -- 2 Cars waiting on the left street of the intersection
leftIntersectionState = egoInitialState
leftIntersectionState.transform = spawns[1]
leftIntersectionState.transform.position -= CAR_LENGTH * 3.7 * right
leftIntersectionState.transform.position += CAR_LENGTH * 5.9 * forward
leftIntersectionState.transform.rotation.y += 95
sim.add_agent("Sedan", lgsvl.AgentType.NPC, leftIntersectionState, NPC_COLOR)
leftIntersectionState.transform.position -= LANE_WIDTH * forward
sim.add_agent("Sedan", lgsvl.AgentType.NPC, leftIntersectionState, NPC_COLOR)

# Pedestrian to cross the path of the ego as it turns left
pedState = copy.deepcopy(egoInitialState)
pedState.transform.position.x -= 12
pedState.transform.position.z -= 15
pedState.transform.rotation.y += 90
pedState.transform.position += pedDistanceFromIntersection * forward

ped = sim.add_agent("Pamela", lgsvl.AgentType.PEDESTRIAN, pedState)

# Setting up pedestrian waypoints for across the road
ped_wp = []
ped_wp.append(lgsvl.WalkWaypoint(pedState.transform.position, idle=0, trigger_distance=pedTrigger))
pedFinalState = copy.deepcopy(egoInitialState)
pedFinalState.transform.position.x -= 12
pedFinalState.transform.position.z += 10
pedFinalState.transform.rotation.y += 90
ped_wp.append(lgsvl.WalkWaypoint(pedFinalState.transform.position, speed=pedSpeed, idle=0))

ped.follow(ped_wp)
ped.on_collision(on_collision)


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

#Set a destination for apollo (turn left at intersection)
destination = egoInitialState.position + (CAR_LENGTH * 6* forward) - (CAR_LENGTH * 3 * right)
dv.setup_apollo(destination.x, destination.z, modules)

## -- Setting weather and time of day -- ##
sim.weather = lgsvl.WeatherState(rain=weatherQuality, fog=weatherQuality, wetness=weatherQuality, cloudiness=weatherQuality, damage=0)
sim.set_time_of_day(timeOfDay, fixed=True)

sim.run(60.0)