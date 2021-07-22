A (written) simulation test report, which documents the generated test scenarios, classes, scripting methods, simulation test coverage, and problem findings. Sample structure of the simulation test report (for reference only):
  * Section 1 Introduction
    * Test organization and roles
    * Challenge strategy and planning
    * Targeted simulation resources 
    * Targeted AV simulation test requirments
  * Section 2 AV Simulation Test Scenario Generation
    * Applied strategy
    * Used methods/approaches
    * Supporting technology and tools
  * Section 3 AV Simulation Test Results
    * Established AV simulation test requirements based on scenarios
    * Focused scenario classes and diversity 
    * Statistics and distribution report about executive scenarios and scripts for different classified scenario types (or classes)
    * Discovered problems and statistics
  * Section 4 Summary and Experience 
   

# Written Test Report
## 1 - Introduction
The aim of the testing conducted in this deliverable is to attempt to find faults with the Apollo Autonomous Vehicle driving system, in order to highlight problem areas for its developers to focus on. 

Four main classes of scenarios have been created, each with a goal to test the AVs operation in a unique and commonly observed driving situation. These scenarios include a mix of pedestrians and NPC car situations. The scenarios are named alaphabetically: *****************A, B, C, D/E,**************** where D and E are the same scenario class, but implemented on different maps, as explained in the [map information readme.]("..\map_info\README.md")

The main approach to the challenge that the team took included first identifying scenarios that were common in real driving situations and not already covered in the scenarios from Deliverable 1. These scenarios were then created with hardcoded parameters and manual observation tests conducted. Next, values that could be parameterised were extracted to be accepted as arguments to the python script. Once this was done, shell script files were then created to automatically run through multiple combinations of all parameters for the scenario. Finally, the shell scripts for each scenario were then combined into a single automated shell script to run all tests on all scenarios over a long period of time. Although some combinations (mainly relating to weather conditions) were not run due to time limitations, a total of 1078 test cases were run for this deliverable, totalling 18 hours of execution, with each scenario set to run for 60 seconds. The python scripts were also set to write outputs to a text file, including if a collision occurred. These text files where then analysed in the paper provided with this submission.


## 2 - Test Scenario Generation
The test scenarios were generally generated through brainstorming with the team. Ideas came from personal driving experience and ideas for common dangerous situations in which collisions are likely to occur. As this is a self-driving system that ultimately uses sensors to collect its data (for simulations not running using ground-truth), it was also decided to design at least one scenario (D) to test the camera module in particular. This included setting the scenario with unfavourable weather conditions. It was then decided that we could apply variations in weather conditions to all test scenarios, thus increasing the diversity of test cases. Explanation notes and diagrams for each scenario are provided in the map information readme.


Test cases have generally been developed using the
Equivalent Partitioning (EP) and Metamorphic Testing (MT) techniques. EP has been used to find groups of test cases in the input domain for the parameters used in the scenarios, and with an individual test case then selected to represent this group. MT has been used to generate test cases to attempt to detect inconsistency issuses with the behaviour of the AV, as further discussed in the paper.

No additional specialised tools or technologies were used during this competition.


## 3 - Test Results
Of the over one thousand tests run across all scenarios, some *58* failures were detected in which the ego vehicle was involved in a collision. These failures occurred across all scenarios except **Scenario C***. Scenario D had the most number of tests executed, including comprehensive testing with weather conditions. Most other scenarios were not extensively tested using weather condition parameters. While Scenario B had the most amount of failures detected, at 28, not all of these could be argued to be true failures of the AV system as some failures occurred when a pedestrian walked into the side of the ego vehicle. As such, it was not really the fault of the system under test.

The two most interesting set of test results are those for Scenarios A and D. In both these scenarios, major faults with the AV have been detected, thus identifying areas to focus development on. Failures from both these scenarios involved the vehicle's inability to stop sufficiently in time. In Scenario A, this occurred when the ego vehicle failed to stop for pedestrians suddenly appearing in its path. In some cases the vehicle would slow down greatly to a near stop, but a collision would still occur. Additionally, while the vehicle did detect the presence of the pedestrians, it does not always seem to recognise the potential of the threat, and does not slow down approaching them, even before they begin to move. The test cases that caused this failure also proved to be somewhat inconsistent, with a collision not always occurring for the same scenario parameters.

Scenario D also *had meaningful results*


## 4 - Summary and Experience
