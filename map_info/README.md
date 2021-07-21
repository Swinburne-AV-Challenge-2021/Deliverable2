# Map Info

As with our Deliverable 1 submission, most scenarios created use the San Francisco map as we were already familiar with it and had it set up. This setup involved manually downloading the map binaries (routing_map.bin, sim_map.bin, base_map.bin) from the [Apollo 5.0 LGSVL Fork](https://github.com/lgsvl/apollo-5.0/tree/simulator/modules/map/data/san_francisco), before placing them into the `apollo/modules/map/data/SanFrancisco` directory. One scenario was created using the Borregas Avenue map.


## Scenario A - Close Quarters:
This scenario sees the Apollo ego navigate through a tight space with stationary cars on either side, possibly simulating a narrow street or a traffic jam. Suddenly, two pedestrians appear from between some cars and cross in front of the ego.

The purpose of this test is to attempt to identify if the ego can successfully detect the danger and stop in time. Additionally, if sensor detection is used, this scenario would also 'stress' the perception module by providing multiple other entities to track, potentially increasing the chance of missing the pedestrians.

The ego vehicle is set to drive to the next intersection, just beyond the line of N cars (10, by default). The pedestrians spawn in the place of the ith (default, 5th) car position, with waypoints set to the position in the opposite line of cars, along with a trigger distance of initially 20 meters. These values are parameterised to allow for greater testing coverage.

It was found with the default values used that the ego vehicle, despite detecting the pedestrians, fails to stop in time and collides with at least one of them.


## Scenario B - Pedestrian Intersection:
This scenario also relates to testing Apollo's ability to detect and respond to pedestrians. In this situation, the ego vehicle is set to make a left turn at an intersection. A pedestrian is then triggered to walk across the intersection parallel to the original direction of the ego, directly crossing its path as it makes the turn. Two stationary cars are also placed at the intersection, although their presence serves little direct purpose, only to somewhat block the view of the pedestrian.

The goal of this test is to again identify if Apollo can respond to pedestrians in time. However, different to the first scenario, an intersection with a turn is involved and the ego expects to have complete right of way. Additionally, the ego will have more time to recognise and respond to the moving pedestrian.

Various values affecting this test scenario are extracted to allow them to be parameterised for automated testing, as further discussed in the report. These values are the speed and trigger distance of the pedestrian, as well as its initial starting distance from the road. Furthermore, as with other scenarios, general parameters are provided for controlling the weather and time of day.


## C - Camera Tricks:
The goal of this scenario is to understand and confirm the reaction of the ego vehicle in the task of navigating a busy intersection. This is simulated using many stationary NPCs in the parallel lane to the ego's starting position. Additionally, 2 NPC vehicles are triggered to cross the intersection perpendicularly when the ego approaches, thus getting in its way.

The ego vehicle can be set to make a left turn, right turn, or proceed straight ahead through the intersection, depending on the parameter passed. Additional parameters that can be adjusted include the trigger distance and speed for the left and right NPCs individually as well as the time of day, weather conditions, and NPC car color.

One of the main motivators for creating this specific scenario was to test how well the ego's perception module, if it is installed, can handle difficult environment and lighting conditions. As such, all NPC vehicles are made black by default and the scenario is best run in a dark night time setting with high fog and rain.

Even without the weather conditions, it was found from this scenario that the ego will not stop in time when set to drive straight through the intersection, colliding with at least one NPC vehicle in some conditions. This is likely because the ego always has right of way, regardless of its destination direction, however, when it is driving straight, it does not need to slow down so cannot respond to the encroaching perpendicular vehicles. When turning, however, the ego will slow down before the turn, allowing it to detect and avoid the NPCs. Despite this, it can still be possible for the ego to have a collision, even when making a turn.


## D - Go Around, Oncoming:
This scenario is about testing the ego's ability to detect and respond to oncoming vehicles, as it tries to get around a blocked car in its way. In some ways, this scenario is similar to Deliverable 1's Scenario 5, where the ego needs to respond to oncoming vehicles. However, this time the ego vehicle is the one that wants to encroach on to the other side of the road.

This scenario uses the Borregas Avenue map as this map has a road with only 1 lane per direction, unlike the San Francisco map. The ego vehicle is placed on one end of the road, with an oncoming NPC vehicle spawned some distance away and in the oncoming adjacent lane, with a trigger distance set to cause it to approach the ego. A 2nd, stationary, NPC is then placed in the same lane as the ego vehicle, a few meters directly ahead. Apollo is then commanded to drive with a destination set just ahead of the stationary NPC. General weather conditions are parameterised, along with the oncoming NPC vehicle speed, spawn distance, and trigger distance.

Although less time was dedicated to testing this scenario with many parameter combinations, from the testing so far, no collision occurs. It is interesting to note that the ego vehicle does not even attempt to go around the blocked car into the other lane, suggesting that the ego vehicle does not want to encroach onto the other side of the road, despite the lane lines. The testers are not familiar with road rules in the US and the line markings are not very clear in the map itself, but it would seem that this particular road should allow vehicles to drive on the other side for overtaking and passing.


## E - Go Around, OnComing, San Francisco:
Due to the outcomes from the tests in Scenario D, it was decided to recreate the same scenario on a 2-lane-per-direction road in the San Francisco map. This is because it is known that the ego will change lanes to move around a stationary vehicle. This time, however, the encroaching vehicle would enter the ego's side of the road and pass the stationary NPC in the lane that the ego will use to get around that NPC, thus testing if the ego will stop before it makes its own lane change, or possibly changes back to its original lane to avoid the danger.

The ego vehicle was set to take a right turn at the next intersection in order to ensure that it returned to the original lane it started in, thus effectively going around.

This scenario has parameters for speeds for the three different waypoints that the oncoming vehicle moves through. It is possible that the ego vehicle will not react in time if faster speeds are used. Additionally, the usual weather condition parameters are provided.

It was again decided to focus more test automation time on the first three scenarios, resulting in less testing here. We did, however, find that in some cases the ego would halt its lane change as the oncoming vehicle moved past, and then proceed afterwards, with no collision. In other cases, though, the ego did not see the encroaching vehicle early enough and still entered the overtaking lane, or, upon seeing the oncoming NPC, it did not attempt to avoid it.