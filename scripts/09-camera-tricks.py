from environs import Env
from lgsvl.geometry import Vector
import lgsvl
import time
import copy
from lgsvl.utils import ObjectState

# Constants
LANE_WIDTH = 4.0
CAR_LENGTH = 8.0
NPC_COLOR = Vector(0, 0, 0)
MAX_CAR_LINE = 10

# Paramters for Metamorphic Testing # input ranges
leftSpeed = 10 # 0 - 20
leftTrigger = 55 # > 0
rightSpeed = 5 # 0 - 20
rightTrigger = 45 # > 0
turnDirection = 0 # {0, 1, 2} 0 - Straight, 1 - Left, 2 - Right
timeOfDay = 22 # [0, 24)
weatherQuality = 1.0 # [0.0, 1.0] 0 is good quality, 1 is bad, worst conditions


# Spawns a line of cars up to MAX_CAR_LINE behind each other, and 2 lanes wide, starting from the initial ObjectState
def spawn2LaneTraffic(state: ObjectState, count = 0):
    # If not at the end of the line,
    if (count < MAX_CAR_LINE):
        # Move the state forward 1 length and add the NPC in the same lane
        state.transform.position += CAR_LENGTH * forward
        sim.add_agent("Sedan", lgsvl.AgentType.NPC, state, NPC_COLOR)
        count += 1

        # Add the next NPC behind this one
        spawn2LaneTraffic(state, count)

        # Add the NPC adjacent to this one (position will be changed before getting to this line)
        sim.add_agent("Sedan", lgsvl.AgentType.NPC, state, NPC_COLOR)

        # Before ending function, move the state back 1 car length for the next function call
        state.transform.position -= CAR_LENGTH * forward

    # When reach the end, move the state to the adjacent lane
    else:
        state.transform.position += LANE_WIDTH * right


def on_collision(agent1, agent2, contact):
  name1 = "STATIC OBSTACLE" if agent1 is None else agent1.name
  name2 = "STATIC OBSTACLE" if agent2 is None else agent2.name
  print("{} collided with {} at {}".format(name1, name2, contact))


env = Env()
sim = lgsvl.Simulator(env.str("LGSVL__SIMULATOR_HOST", "127.0.0.1"), env.int("LGSVL__SIMULATOR_PORT", 8181))
if sim.current_scene == "SanFrancisco":
    sim.reset()
else:
    sim.load("SanFrancisco")

spawns = sim.get_spawn()

egoInitialState = lgsvl.AgentState()
egoInitialState.transform = spawns[3]
egoInitialState.transform.rotation.y += 180

forward = lgsvl.utils.transform_to_forward(egoInitialState.transform)
right = lgsvl.utils.transform_to_right(egoInitialState.transform)

egoInitialState.transform.position += LANE_WIDTH * 2 * right
egoInitialState.transform.position -= CAR_LENGTH * 5 * forward

# Spawn the ego in the right lane if doing a right turn, then move its position back to keep the NPC spawns the same
if (turnDirection == 2):
    egoInitialState.transform.position += LANE_WIDTH * right
    ego = sim.add_agent("2e9095fa-c9b9-4f3f-8d7d-65fa2bb03921", lgsvl.AgentType.EGO, egoInitialState, Vector(68, 168, 50))
    egoInitialState.transform.position -= LANE_WIDTH * right
else:
    ego = sim.add_agent("2e9095fa-c9b9-4f3f-8d7d-65fa2bb03921", lgsvl.AgentType.EGO, egoInitialState, Vector(68, 168, 50))

# Set the initial oncoming and forwards states to be just at the beginning of the intersection
oncomingState = copy.deepcopy(egoInitialState)
forwardState = copy.deepcopy(egoInitialState)
oncomingState.transform.position -= LANE_WIDTH * right
oncomingState.transform.position += CAR_LENGTH * 5.7 * forward
oncomingState.transform.rotation.y -= 180
forwardState.transform.position += LANE_WIDTH * right + CAR_LENGTH * 5.7 * forward

#Adding some stationary NPCs on the ego's side of the intersection
sim.add_agent("Sedan", lgsvl.AgentType.NPC, oncomingState, NPC_COLOR)
oncomingState.transform.position -= LANE_WIDTH * right
sim.add_agent("Sedan", lgsvl.AgentType.NPC, oncomingState, NPC_COLOR)

if (turnDirection != 2):
    sim.add_agent("Sedan", lgsvl.AgentType.NPC, forwardState, NPC_COLOR)

# Spawn a line of traffic banked up on the oncoming side of the road, after the intersection
oncomingState.transform.position += CAR_LENGTH * 3.7 * forward
spawn2LaneTraffic(oncomingState)

# Add a single NPC on the ego's side of the road, but on the other side of the intersection
forwardState.transform.position += CAR_LENGTH * 4.7 * forward
forward_wp = []
forward_wp.append(lgsvl.DriveWaypoint(forwardState.transform.position, speed=6, idle=0, trigger_distance=8, angle=forwardState.rotation))
forward_wp.append(lgsvl.DriveWaypoint(forwardState.transform.position + CAR_LENGTH * 10 * forward, speed=0, angle=forwardState.rotation))
sim.add_agent("Sedan", lgsvl.AgentType.NPC, forwardState, NPC_COLOR).follow(forward_wp)


# -- Leftside -- Make car on left of intersection move left to right in front of the ego
leftIntersectionState = copy.deepcopy(egoInitialState)
leftIntersectionState.transform.rotation.y += 90
leftIntersectionState.transform.position -= LANE_WIDTH * 10 * right
leftIntersectionState.transform.position += CAR_LENGTH * 7.45 * forward
rightIntersectionState = copy.deepcopy(leftIntersectionState)

npc_l = sim.add_agent("Sedan", lgsvl.AgentType.NPC, leftIntersectionState, NPC_COLOR)
npc_l_wp = []
npc_l_wp.append(lgsvl.DriveWaypoint(leftIntersectionState.transform.position, speed=leftSpeed, idle=0, trigger_distance=leftTrigger, angle=leftIntersectionState.rotation))
npc_l_wp.append(lgsvl.DriveWaypoint(leftIntersectionState.transform.position + (CAR_LENGTH * 20 * right), speed=0, angle=leftIntersectionState.rotation))
npc_l.follow(npc_l_wp)
npc_l.on_collision(on_collision)


# -- Right side -- Make car on right of intersection move right to left in front of the ego
rightIntersectionState.transform.rotation.y += 180
rightIntersectionState.transform.position += LANE_WIDTH * 2 * forward
rightIntersectionState.transform.position += CAR_LENGTH * 7.4 * right
npc_r = sim.add_agent("Sedan", lgsvl.AgentType.NPC, rightIntersectionState, NPC_COLOR)
npc_r_wp = []
npc_r_wp.append(lgsvl.DriveWaypoint(rightIntersectionState.transform.position, speed=rightSpeed, idle=0, trigger_distance=rightTrigger))
npc_r_wp.append(lgsvl.DriveWaypoint(rightIntersectionState.transform.position - (CAR_LENGTH * 15 * right), speed=0))
npc_r.follow(npc_r_wp)
npc_r.on_collision(on_collision)

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

apolloDestinations = {}
# 20 car lengths straight ahead
apolloDestinations[0] = egoInitialState.position + (CAR_LENGTH * 20 * forward)
# Turn left
apolloDestinations[1] = rightIntersectionState.transform.position - (CAR_LENGTH * 7 * right)
# Turn right
apolloDestinations[2] = leftIntersectionState.transform.position + (CAR_LENGTH * 10 * right)


#Set a destination for apollo
destination = apolloDestinations[turnDirection]
dv.setup_apollo(destination.x, destination.z, modules)

## -- Setting weather and time of day -- ##
sim.weather = lgsvl.WeatherState(rain=weatherQuality, fog=weatherQuality, wetness=weatherQuality, cloudiness=weatherQuality, damage=0)
sim.set_time_of_day(timeOfDay, fixed=True)

sim.run(60.0)