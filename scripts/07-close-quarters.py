from environs import Env
from lgsvl.geometry import Vector
import lgsvl
import time
import copy
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
    parser.add_argument('--pedSpeed',type=float,default=2)
    parser.add_argument('--pedTrigger',type=float,default=20)
    parser.add_argument('--pedIdle',type=float,default=5)
    parser.add_argument('--numberOfCar',type=int,default=10)
    parser.add_argument('--pedLocation',type=int,default=3)
    args = parser.parse_args()


    LANE_WIDTH = 4.0
    CAR_LENGTH = 8.0
    EGO_INITIAL_POSITION = Vector(-165,10,-120)
    DESTINATION = Vector(-30,10,-126)

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
        outcome = 'Test failed.\nTEST CASE {}: {} collided with {} at {}'.format(args.testid, name1, name2, contact)
        outcome += '\nConditions:\n{}'.format(args)
        global testPassed
        testPassed = False
        print(outcome)
        write_testoutcome(outcome)
        sim.stop()


    spawns = sim.get_spawn()

    egoInitialState = lgsvl.AgentState()
    egoInitialState.transform = spawns[0]

    egoInitialState.transform.position = EGO_INITIAL_POSITION
    egoInitialState.transform.rotation.y -= 90

    forward = lgsvl.utils.transform_to_forward(egoInitialState.transform)
    right = lgsvl.utils.transform_to_right(egoInitialState.transform)

    ego = sim.add_agent('2e9095fa-c9b9-4f3f-8d7d-65fa2bb03921', lgsvl.AgentType.EGO, egoInitialState)


    # Spawn a line of parked cars to the left and right of the ego vehicle
    leftState = copy.deepcopy(egoInitialState)
    rightState = copy.deepcopy(egoInitialState)

    # Initial, immediately adjacent cars
    leftState.transform.position -= (LANE_WIDTH  - 1) * right
    rightState.transform.position += LANE_WIDTH * right
    sim.add_agent('Sedan', lgsvl.AgentType.NPC, leftState)
    sim.add_agent('Sedan', lgsvl.AgentType.NPC, rightState)


    leftPedWp = []
    rightPedWp = []

    # More cars ahead, leaving room for some pedestrians on the 3rd loop
    for i in range(args.numberOfCar):
        leftState.transform.position += (CAR_LENGTH * forward)
        rightState.transform.position += (CAR_LENGTH * forward)

        if (i != args.pedLocation): # add car if there is no pedestrian
            sim.add_agent('Sedan', lgsvl.AgentType.NPC, leftState)
            sim.add_agent('Sedan', lgsvl.AgentType.NPC, rightState)
            
        else: # Add 2 pedestrians, opposite each other and slightly separated by 1/4th the CAR_LENGTH (so they don't collide)
            leftPedState = copy.deepcopy(leftState)
            rightPedState = copy.deepcopy(rightState)
            leftPedState .transform.position += (CAR_LENGTH/4) * forward
            rightPedState.transform.position -= (CAR_LENGTH/4) * forward
            leftPed = sim.add_agent('Pamela', lgsvl.AgentType.PEDESTRIAN, leftPedState)
            rightPed = sim.add_agent('Pamela', lgsvl.AgentType.PEDESTRIAN, rightPedState)

            # Set their waypoints to the opposite side of the lane, to be only triggered when the ego is 20m away
            leftPedWp.append(lgsvl.WalkWaypoint(leftPedState.transform.position, idle=0, trigger_distance=args.pedTrigger))
            leftPedWp.append(lgsvl.WalkWaypoint(rightPedState.transform.position, idle=args.pedIdle, speed=args.pedSpeed))
            rightPedWp.append(lgsvl.WalkWaypoint(rightPedState.transform.position, idle=0, trigger_distance=args.pedTrigger))
            rightPedWp.append(lgsvl.WalkWaypoint(leftPedState.transform.position, idle=args.pedIdle, speed=args.pedSpeed))

            leftPed.follow(leftPedWp)
            rightPed.follow(rightPedWp)
            leftPed.on_collision(on_collision)
            rightPed.on_collision(on_collision)



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

    #Set a destination for apollo (straight ahead, to next intersection)
    dv.setup_apollo(DESTINATION.x, DESTINATION.z, modules)

    ## -- Setting weather and time of day -- ##
    sim.weather = lgsvl.WeatherState(rain=args.rain, fog=args.fog, wetness=args.wetness, cloudiness=args.cloudiness, damage=args.damage)
    sim.set_time_of_day(args.timeOfDay, fixed=True)
    
    sim.run(args.simSecond)

    if (testPassed):
        write_testoutcome('Test passed.')