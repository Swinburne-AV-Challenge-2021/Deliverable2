from environs import Env
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
    parser.add_argument('--carSpeed',type=float,default=10)
    parser.add_argument('--carDistance',type=float,default=15) # [5,30]
    parser.add_argument('--carTrigger',type=float,default=14)
    args = parser.parse_args()


    # Constants
    LANE_WIDTH = 4.0
    CAR_LENGTH = 8.0
    ONCOMING_DIRECTION = 180
    ONCOMING_GROUND_HEIGHT = (-0.1211 * args.carDistance) - 3.0418 # Non-flat road means the height spawn height needs to be automatically adjusted
    EGO_GROUND_HEIGHT = -3.30108
    EGO_GROUND_SPAWN_GAP = 2 # Used to reduce the height above the road that the ego spawns at
    EGO_CAR_DISTANCE = 15


    env = Env()
    sim = lgsvl.Simulator(env.str('LGSVL__SIMULATOR_HOST', '127.0.0.1'), env.int('LGSVL__SIMULATOR_PORT', 8181))
    if sim.current_scene == 'BorregasAve':
        sim.reset()
    else:
        sim.load('BorregasAve')


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
    egoInitialState.transform = spawns[0]
    egoInitialState.transform.position.y -= EGO_GROUND_SPAWN_GAP

    forward = lgsvl.utils.transform_to_forward(egoInitialState.transform)
    right = lgsvl.utils.transform_to_right(egoInitialState.transform)

    egoInitialState.transform.position -= LANE_WIDTH * 0.7 * right
    egoInitialState.transform.position += CAR_LENGTH * EGO_CAR_DISTANCE * forward

    ego = sim.add_agent('2e9095fa-c9b9-4f3f-8d7d-65fa2bb03921', lgsvl.AgentType.EGO, egoInitialState)


    # Spawn a vehicle in the oncomming lane, set to begin driving in its lane as the ego approaches a stationary vehicle
    oncomingState = copy.deepcopy(egoInitialState)
    oncomingState.transform.position -= LANE_WIDTH * right
    oncomingState.transform.position += CAR_LENGTH * args.carDistance * forward
    oncomingState.transform.rotation.y += ONCOMING_DIRECTION
    oncomingState.transform.position.y = ONCOMING_GROUND_HEIGHT # Due to map spawn being lower than y = 0
    oncomingNPC = sim.add_agent('Sedan', lgsvl.AgentType.NPC, oncomingState)
    oncomingNPC.on_collision(on_collision)
    oncoming_wp = []

    oncoming_wp.append(lgsvl.DriveWaypoint(oncomingState.transform.position, idle=0, speed=args.carSpeed, trigger_distance=CAR_LENGTH * args.carTrigger, angle=oncomingState.transform.rotation))
    egoInitialState.transform.position.y = EGO_GROUND_HEIGHT
    oncoming_wp.append(lgsvl.DriveWaypoint(egoInitialState.transform.position - (LANE_WIDTH * right), speed=0, angle=oncomingState.transform.rotation))
    oncomingNPC.follow(oncoming_wp)


    # Spawn a stationary car directly in front of the ego
    egoInitialState.transform.position += CAR_LENGTH * 5 * forward
    sim.add_agent('Sedan', lgsvl.AgentType.NPC, egoInitialState).on_collision(on_collision)


    ## -- Apollo Setup -- ##
    print('Bridge connected:', ego.bridge_connected)
    # Connect to Apollo bridge
    ego.connect_bridge(env.str('LGSVL__AUTOPILOT_0_HOST', lgsvl.wise.SimulatorSettings.bridge_host), env.int('LGSVL__AUTOPILOT_0_PORT', lgsvl.wise.SimulatorSettings.bridge_port))
    while not ego.bridge_connected:
        time.sleep(1)
    print('Bridge connected:', ego.bridge_connected)

    # Connect to Dreamview to control Apollo
    dv = lgsvl.dreamview.Connection(sim, ego, ip='localhost', port='8888')
    dv.set_hd_map('borregas_ave')
    dv.set_vehicle('Lincoln2017MKZ_LGSVL')
    modules = [
        'Localization',
        'Transform',
        'Planning',
        'Prediction',
        'Routing',
        'Control'
    ]

    # Set a destination for apollo (straight ahead, to next intersection)
    destination = egoInitialState.transform.position + CAR_LENGTH * 5 * forward
    dv.setup_apollo(destination.x, destination.z, modules)

    ## -- Setting weather and time of day -- ##
    sim.weather = lgsvl.WeatherState(rain=args.rain, fog=args.fog, wetness=args.wetness, cloudiness=args.cloudiness, damage=args.damage)
    sim.set_time_of_day(args.timeOfDay, fixed=True)
    
    sim.run(args.simSecond)

    if (testPassed):
        write_testoutcome('Test passed.')