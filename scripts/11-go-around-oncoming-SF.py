from math import atan
from environs import Env
import lgsvl
import time
import copy
from lgsvl.geometry import Vector
import argparse
import os


# Run script with configurable parameters in Terminal to reduce the memory burden
if __name__ == '__main__':
    # common arguments - same across different test groups
    parser = argparse.ArgumentParser()
    parser.add_argument('--testid',type=str,default='0')
    parser.add_argument('--simSecond',type=int,default=60)
    parser.add_argument('--timeOfDay',type=int,default=12)
    parser.add_argument('--rain',type=float,default=0.)
    parser.add_argument('--fog',type=float,default=0.)
    parser.add_argument('--wetness',type=float,default=0.)
    parser.add_argument('--cloudiness',type=float,default=0.)
    parser.add_argument('--damage',type=float,default=0.)

    # specific arguments - only this test group
    parser.add_argument('--carSpeed1',type=float,default=15)
    parser.add_argument('--carSpeed2',type=float,default=10)
    parser.add_argument('--carSpeed3',type=float,default=10)
    args = parser.parse_args()


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


    # Write test outcome
    def write_testoutcome(content):
        try:
            if not os.path.isdir('tests'):
                os.makedirs('tests')
        except IOError:
            return
        f = open('tests/'+args.testid+'.txt','w')
        f.write(content)
        f.close()

    # Used later to determine what to write to the output file
    testPassed = True


    # Callback function to handle collision
    def on_collision(agent1, agent2, contact):
        name1 = 'STATIC OBSTACLE' if agent1 is None else agent1.name
        name2 = 'STATIC OBSTACLE' if agent2 is None else agent2.name
        outcome = 'Test failed.\nTEST CASE {}: {} seconds. {} collided with {} at position {}'.format(args.testid, sim.current_time, name1, name2, contact)
        outcome += '\nEgo Speed: {} m/s'.format(ego.state.speed)
        outcome += '\nConditions:\n{}'.format(args)
        global testPassed
        testPassed = False
        print(outcome)
        write_testoutcome(outcome)
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
    oncoming_wp.append(lgsvl.DriveWaypoint(oncomingState.transform.position, idle=0, speed=args.carSpeed1, trigger_distance=CAR_LENGTH * 10, angle=angleVector))
    oncoming_wp.append(lgsvl.DriveWaypoint(wp_2, speed=args.carSpeed2, angle=oncomingState.rotation))
    oncoming_wp.append(lgsvl.DriveWaypoint(egoInitialState.transform.position - (LANE_WIDTH * right) + (CAR_LENGTH * 4 * forward), speed=args.carSpeed3, angle=oncomingState.rotation))
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

    ## -- Setting weather and time of day -- ##
    sim.weather = lgsvl.WeatherState(rain=args.rain, fog=args.fog, wetness=args.wetness, cloudiness=args.cloudiness, damage=args.damage)
    sim.set_time_of_day(args.timeOfDay, fixed=True)
    
    sim.run(args.simSecond)

    if (testPassed):
        write_testoutcome('Test passed.')