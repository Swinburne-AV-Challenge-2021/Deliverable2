Selected scenario trip/route and map information (e.g. which maps were used; include descriptions and/or sketches of routes for ego and NPC trajectories)

# Map Info

As with our deliverable 1 submission, all scenarios created again only use the San Francisco map as we were already familar with it and had it setup. This setup involved manually downloading the map binaries (routing_map.bin, sim_map.bin, base_map.bin) from the [Apollo 5.0 LGSVL Fork](https://github.com/lgsvl/apollo-5.0/tree/simulator/modules/map/data/san_francisco), before placing them into the `apollo/modules/map/data/SanFrancisco` directory.



## Scenario 07 - Close Quarters:
This scenario sees the Apollo ego navigate through a tight space with stationary cars on either side, possibly simulating a narrow street or a traffic jam. Suddenly, two pedestrians appear from between some cars and cross in front of the ego.

The purpose of this test is to attempt to identify if the ego can successfully detect the danger and stop in time. Additionally, if sensor detection is used, this scenario would also 'stress' the perception module by providing multiple other entities to track, potentially increasing the chances of missing the pedestrians.

The ego vehicle is set to drive to the next interestion, just beyond the line of 10 cars. The pedestrians spawn in the place of the 5th car position, with waypoints set to the position in the opposite line of cars, along with a trigger distance of 20 meters. These values could potentially be parameterised later.

It was found with the values currently used that the ego vehicle, despite detecting the pedstrians, fails to stop in time and collides with at least one of them.


## Scenario 08 - Pedestrian Intersection:
This scenario also relates to testing Apollo's ability to detect and respond to pedestrians. In this situation, the ego vehicle is set to make a left turn at an intersection. A pedestrian is then triggered to walk across the intersection parallel to the original direction of the ego, directly crossing its path as it makes the turn. Two stationary cars are also placed at the intersection, although their presence serves little direct purpose.

The goal of this test is to again identify if Apollo can respond to pedestrians in time. However, different to the first scenario, an intersection with a turn is involved and the ego expects to have complete right of way. Additionally, the ego will have more time to recognise and respond to the moving pedestrian.

*write about how the scenario is setup, including with the parameteris-able variables*