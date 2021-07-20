# Map Info

As with our Deliverable 1 submission, most scenarios created use the San Francisco map as we were already familar with it and had it setup. This setup involved manually downloading the map binaries (routing_map.bin, sim_map.bin, base_map.bin) from the [Apollo 5.0 LGSVL Fork](https://github.com/lgsvl/apollo-5.0/tree/simulator/modules/map/data/san_francisco), before placing them into the `apollo/modules/map/data/SanFrancisco` directory. One scenario was created using the Borregas Avenue map.


## Scenario A - Close Quarters:
This scenario sees the Apollo ego navigate through a tight space with stationary cars on either side, possibly simulating a narrow street or a traffic jam. Suddenly, two pedestrians appear from between some cars and cross in front of the ego.

The purpose of this test is to attempt to identify if the ego can successfully detect the danger and stop in time. Additionally, if sensor detection is used, this scenario would also 'stress' the perception module by providing multiple other entities to track, potentially increasing the chance of missing the pedestrians.

The ego vehicle is set to drive to the next interestion, just beyond the line of N cars (10, by default). The pedestrians spawn in the place of the ith (default, 5th) car position, with waypoints set to the position in the opposite line of cars, along with a trigger distance of initially 20 meters. These values are parameterised to allow for greater testing coverage.

It was found with the default values used that the ego vehicle, despite detecting the pedstrians, fails to stop in time and collides with at least one of them.


## Scenario B - Pedestrian Intersection:
This scenario also relates to testing Apollo's ability to detect and respond to pedestrians. In this situation, the ego vehicle is set to make a left turn at an intersection. A pedestrian is then triggered to walk across the intersection parallel to the original direction of the ego, directly crossing its path as it makes the turn. Two stationary cars are also placed at the intersection, although their presence serves little direct purpose, only to somewhat block the view of the pedestrian.

The goal of this test is to again identify if Apollo can respond to pedestrians in time. However, different to the first scenario, an intersection with a turn is involved and the ego expects to have complete right of way. Additionally, the ego will have more time to recognise and respond to the moving pedestrian.

Various values affecting this test scenario are extracted to allow them to be parameterised for automated testing, as further discussed in the report. These values are the speed and trigger distance of the pedestrian, as well as its initial starting distance from the road. Furthermore, as with other scenarios, general parameters are provided for controlling the weather and time of day.


## C - Camera Tricks:
The goal of this scenario is to understand and confirm the reaction of the ego vehicle in the task of navigating a busy intersection. This is simulated using many stationary NPCs in the parallel lane to the ego's starting position. Additionally, 2 NPC vehicles are triggered to cross the intersection perpendicularly when the ego approaches, thus getting in its way.

The ego vehicle can be set to make a left turn, right turn, or proceed straight ahead through the intersection, depending on the parameter passed. Additional parameters that can be adjusted include the trigger distance and speed for the left and right NPCs individually as well as the time of day, weather conditions, and NPC car color.

One of the the main motivators for creating this specific scenario was to test how well the ego's perception module can handle difficult environment and lighting conditions, if it is installed. As such, all NPC vehicles are made black by default and the scenario is best run in a dark night time setting with high fog and rain.

Even without the weather conditions, it was found from this scenario that the ego will not stop in time when set to drive straight through the intersection, colliding with at least one NPC vehicle in some conditions. This is likely because the ego always has right of way, regardless of its destination direction, however, when it is driving straight, it does not need to slow down so cannot respond to the encroaching perpendicular vehicles. When turning, however, the ego will slow down before the turn, allowing it to detect and avoid the NPCs. Despite this, it can still be possible for the ego to have a collision, even when making a turn.