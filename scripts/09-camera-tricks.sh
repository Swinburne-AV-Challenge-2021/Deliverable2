# TEST CATEGORY 9: CLOSE QUARTERS
# ......................
compiler=python3
testscript=09-camera-tricks.py
simSecond=60
# ......................
# TEST GROUP 9.1: TEST IMPACT OF WEATHER
# ......................
timeOfDays=("12" "0")
rains=("0" "0.5" "1.0")
fogs=("0" "0.5" "1.0")
testcount=0
for timeOfDay in "${timeOfDays[@]}" ; do
for rain in "${rains[@]}" ; do
for fog in "${fogs[@]}" ; do
let "testcount=testcount+1"
testid="TEST_9.1_WEATHER_${testcount}"
echo "${testscript}: ${testid}"
${compiler} ${testscript} --testid ${testid} --simSecond ${simSecond} --timeOfDay ${timeOfDay} --rain ${rain} --fog ${fog}
done
done
done
# ......................
# TEST GROUP 9.2: TEST FOR DIFFERENT ROADSIDE PEDESTRIANS AND CARS
# ......................
timeOfDays=("12" "0")
rains=("0" "1.0")
fogs=("0" "1.0")
leftSpeeds=("0" "5" "10" "20")
leftTriggers=("5" "25" "55" "100")
rightSpeeds=("0" "5" "10" "20")
rightTriggers=("10" "15" "45" "95")
turnDirections=("0" "1" "2")
testcount=0
for timeOfDay in "${timeOfDays[@]}" ; do
for rain in "${rains[@]}" ; do
for fog in "${fogs[@]}" ; do
for leftSpeed in "${leftSpeeds[@]}" ; do
for leftTrigger in "${leftTriggers[@]}" ; do
for rightSpeed in "${rightSpeeds[@]}" ; do
for rightTrigger in "${rightTriggers[@]}" ; do
for turnDirection in "${turnDirections[@]}" ; do
let "testcount=testcount+1"
testid="TEST_9.2_TRIGGER_${testcount}"
echo "${testscript}: ${testid}"
${compiler} ${testscript} --testid ${testid} --simSecond ${simSecond} --rain ${rain} --fog ${fog} --timeOfDay ${timeOfDay} --leftSpeed ${leftSpeed} --leftTrigger ${leftTrigger} --rightSpeed ${rightSpeed} --rightTrigger ${rightTrigger} --turnDirection ${turnDirection}
done
done
done
done
done
done
done