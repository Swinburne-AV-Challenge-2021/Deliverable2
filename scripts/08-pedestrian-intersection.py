import os
from environs import Env
from lgsvl.geometry import Vector
import lgsvl
import time
import copy
import argparse

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
    parser.add_argument('--pedSpeed',type=float,default=8)
    parser.add_argument('--pedTrigger',type=float,default=24)    
    parser.add_argument('--pedDistanceFromIntersection',type=float,default=9.)    
    args = parser.parse_args()


    # Constants
    LANE_WIDTH = 4.0
    CAR_LENGTH = 8.0
    NPC_COLOR = Vector(68, 168, 50)
    MAX_CAR_LINE = 10
    PED_STREETPOS,PED_ROADSIDE1,PED_ROADSIDE2,PED_DIRECTION = -12,-15,10,90
    # Manual arameters for Metamorphic Testing # input ranges
    #pedDistanceFromIntersection = args.pedDistanceFromIntersection # Meters from the start of the crossing (>= 0), values more than 0 mean spawns back a bit
    #pedSpeed = args.pedSpeed # 0 - 10
    #pedTrigger = args.pedTrigger # > 6 (when pedDistanceFromIntersection is 0)
    #timeOfDay = 12 # [0, 24)
    #weatherQuality = 0 # [0.0, 1.0] 0 is good quality, 1 is bad, worst conditions


    env = Env()
    sim = lgsvl.Simulator(env.str('LGSVL__SIMULATOR_HOST', '127.0.0.1'), env.int('LGSVL__SIMULATOR_PORT', 8181))
    if sim.current_scene == 'SanFrancisco':
        sim.reset()
    else:
        sim.load('SanFrancisco')


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
    egoInitialState.transform = spawns[1]

    forward = lgsvl.utils.transform_to_forward(egoInitialState.transform)
    right = lgsvl.utils.transform_to_right(egoInitialState.transform)

    egoInitialState.transform.position -= LANE_WIDTH * right

    ego = sim.add_agent('2e9095fa-c9b9-4f3f-8d7d-65fa2bb03921', lgsvl.AgentType.EGO, egoInitialState)


    # 2 cars waiting on the left street of the intersection (to block view)
    leftIntersectionState = egoInitialState
    leftIntersectionState.transform = spawns[1]
    leftIntersectionState.transform.position -= CAR_LENGTH * 3.7 * right
    leftIntersectionState.transform.position += CAR_LENGTH * 5.9 * forward
    leftIntersectionState.transform.rotation.y += 95
    sim.add_agent('Sedan', lgsvl.AgentType.NPC, leftIntersectionState, NPC_COLOR)
    leftIntersectionState.transform.position -= LANE_WIDTH * forward
    sim.add_agent('Sedan', lgsvl.AgentType.NPC, leftIntersectionState, NPC_COLOR)

    # Pedestrian to cross the path of the ego as it turns left, setting starting point to just at the road
    pedState = copy.deepcopy(egoInitialState)
    pedState.transform.position.x += PED_STREETPOS
    pedState.transform.position.z += PED_ROADSIDE1
    pedState.transform.rotation.y += PED_DIRECTION
    pedState.transform.position += args.pedDistanceFromIntersection * forward

    ped = sim.add_agent('Pamela', lgsvl.AgentType.PEDESTRIAN, pedState)

    # Setting up pedestrian waypoints for across the road
    ped_wp = []
    ped_wp.append(lgsvl.WalkWaypoint(pedState.transform.position, idle=0, trigger_distance=args.pedTrigger))
    pedFinalState = copy.deepcopy(egoInitialState)
    pedFinalState.transform.position.x += PED_STREETPOS
    pedFinalState.transform.position.z += PED_ROADSIDE2
    pedFinalState.transform.rotation.y += PED_DIRECTION
    ped_wp.append(lgsvl.WalkWaypoint(pedFinalState.transform.position, speed=args.pedSpeed, idle=0))

    ped.follow(ped_wp)
    ped.on_collision(on_collision)


    ## -- Apollo Setup -- ##
    print('Bridge connected:', ego.bridge_connected)
    #Connect to Apollo bridge
    ego.connect_bridge(env.str('LGSVL__AUTOPILOT_0_HOST', lgsvl.wise.SimulatorSettings.bridge_host), env.int('LGSVL__AUTOPILOT_0_PORT', lgsvl.wise.SimulatorSettings.bridge_port))
    while not ego.bridge_connected:
        time.sleep(1)
    print('Bridge connected:', ego.bridge_connected)

    #Connect to Dreamview to control Apollo
    dv = lgsvl.dreamview.Connection(sim, ego, ip='localhost', port='8888')
    dv.set_hd_map('san_fransisco')
    dv.set_vehicle('Lincoln2017MKZ_LGSVL')
    modules = [
        'Localization',
        'Transform',
        'Perception',
        'Traffic Light',
        'Planning',
        'Prediction',
        'Camera',
        'Routing',
        'Control'
    ]

    # Set a (relative) destination for apollo (turn left at intersection)
    destination = egoInitialState.position + (CAR_LENGTH * 6 * forward) - (CAR_LENGTH * 3 * right)
    dv.setup_apollo(destination.x, destination.z, modules)

    ## -- Setting weather and time of day -- ##
    sim.weather = lgsvl.WeatherState(rain=args.rain, fog=args.fog, wetness=args.wetness, cloudiness=args.cloudiness, damage=args.damage)
    sim.set_time_of_day(args.timeOfDay, fixed=True)

    sim.run(args.simSecond)

    if (testPassed):
        write_testoutcome('Test passed.')