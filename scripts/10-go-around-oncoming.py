from environs import Env
from lgsvl.agent import Agent
import lgsvl
import time
import copy

# Constants
LANE_WIDTH = 4.0
CAR_LENGTH = 8.0
ONCOMING_GROUND_HEIGHT = -4.726
EGO_GROUND_HEIGHT = -3.30108
EGO_GROUND_SPAWN_GAP = 2 # Used to reduce the height above the road that the ego spawns at


env = Env()
sim = lgsvl.Simulator(env.str("LGSVL__SIMULATOR_HOST", "127.0.0.1"), env.int("LGSVL__SIMULATOR_PORT", 8181))
if sim.current_scene == "BorregasAve":
    sim.reset()
else:
    sim.load("BorregasAve")


def on_collision(agent1: Agent, agent2, contact):
  name1 = "STATIC OBSTACLE" if agent1 is None else agent1.name
  name2 = "STATIC OBSTACLE" if agent2 is None else agent2.name
  print("{} collided with {} at {}".format(name1, name2, contact))
  sim.stop()


spawns = sim.get_spawn()
egoInitialState = lgsvl.AgentState()
egoInitialState.transform = spawns[0]
egoInitialState.transform.position.y -= EGO_GROUND_SPAWN_GAP

forward = lgsvl.utils.transform_to_forward(egoInitialState.transform)
right = lgsvl.utils.transform_to_right(egoInitialState.transform)

egoInitialState.transform.position -= LANE_WIDTH * 0.7 * right
egoInitialState.transform.position += CAR_LENGTH * 15 * forward

ego = sim.add_agent("2e9095fa-c9b9-4f3f-8d7d-65fa2bb03921", lgsvl.AgentType.EGO, egoInitialState)


# Spawn a vehicle in the oncomming lane, set to begin driving in its lane as the ego approaches a stationary vehicle
oncomingState = copy.deepcopy(egoInitialState)
oncomingState.transform.position -= LANE_WIDTH * right
oncomingState.transform.position += CAR_LENGTH * 15 * forward
oncomingState.transform.rotation.y += 180
oncomingState.transform.position.y = ONCOMING_GROUND_HEIGHT # Due to map spawn being lower than y = 0
oncomingNPC = sim.add_agent("Sedan", lgsvl.AgentType.NPC, oncomingState)
oncomingNPC.on_collision(on_collision)
oncoming_wp = []

oncoming_wp.append(lgsvl.DriveWaypoint(oncomingState.transform.position, idle=0, speed=10, trigger_distance=CAR_LENGTH * 14, angle=oncomingState.transform.rotation))
egoInitialState.transform.position.y = EGO_GROUND_HEIGHT
oncoming_wp.append(lgsvl.DriveWaypoint(egoInitialState.transform.position - (LANE_WIDTH * right), speed=0, angle=oncomingState.transform.rotation))
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
#dv.set_hd_map("san_fransisco")
dv.set_hd_map("borregas_ave")
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
destination = egoInitialState.transform.position + CAR_LENGTH * 5 * forward
dv.setup_apollo(destination.x, destination.z, modules)

sim.run()