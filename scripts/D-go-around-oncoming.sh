# TEST CATEGORY 10: GO AROUND ONCOMING CAR
# ......................
compiler=python3
testscript=D-go-around-oncoming.py
simSecond=120
# ......................
# TEST GROUP 10.1: TEST IMPACT OF WEATHER
# ......................
timeOfDays=("12" "0")
rains=("0" "0.5" "1.0")
fogs=("0" "0.5" "1.0")
testcount=0
for timeOfDay in "${timeOfDays[@]}" ; do
for rain in "${rains[@]}" ; do
for fog in "${fogs[@]}" ; do
let "testcount=testcount+1"
testid="TEST_10.1_WEATHER_${testcount}"
echo "${testscript}: ${testid}"
${compiler} ${testscript} --testid ${testid} --simSecond ${simSecond} --timeOfDay ${timeOfDay} --rain ${rain} --fog ${fog}
done
done
done
# ......................
# TEST GROUP 10.2: TEST FOR DIFFERENT POSITION OF ONCOMING
# ......................
timeOfDays=("12" "0")
rains=("0" "1.0")
fogs=("0" "1.0")
carSpeeds=("0" "5" "10" "20")
carDistances=("5" "15" "30")
carTriggers=("4" "14" "24")
testcount=0
for timeOfDay in "${timeOfDays[@]}" ; do
for rain in "${rains[@]}" ; do
for fog in "${fogs[@]}" ; do
for carSpeed in "${carSpeeds[@]}" ; do
for carDistance in "${carDistances[@]}" ; do
for carTrigger in "${carTriggers[@]}" ; do
let "testcount=testcount+1"
testid="TEST_10.2_ONCOMING_${testcount}"
echo "${testscript}: ${testid}"
${compiler} ${testscript} --testid ${testid} --simSecond ${simSecond} --rain ${rain} --fog ${fog} --timeOfDay ${timeOfDay} --carSpeed ${carSpeed} --carTrigger ${carTrigger} --carDistance ${carDistance}
done
done
done
done
done
done