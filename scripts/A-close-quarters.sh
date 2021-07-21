# TEST CATEGORY 7: CLOSE QUARTERS
# ......................
compiler=python3
testscript=A-close-quarters.py
simSecond=60
# ......................
# TEST GROUP 7.1: TEST IMPACT OF WEATHER
# ......................
timeOfDays=("12" "0")
rains=("0" "0.5" "1.0")
fogs=("0" "0.5" "1.0")
testcount=0
for timeOfDay in "${timeOfDays[@]}" ; do
for rain in "${rains[@]}" ; do
for fog in "${fogs[@]}" ; do
let "testcount=testcount+1"
testid="TEST_7.1_WEATHER_${testcount}"
echo "${testscript}: ${testid}"
${compiler} ${testscript} --testid ${testid} --simSecond ${simSecond} --timeOfDay ${timeOfDay} --rain ${rain} --fog ${fog}
done
done
done
# ......................
# TEST GROUP 7.2: TEST FOR DIFFERENT ROADSIDE PEDESTRIANS AND CARS
# ......................
timeOfDays=("12" "0")
rains=("0" "1.0")
fogs=("0" "1.0")
pedSpeeds=("1" "2" "4")
pedTriggers=("10" "20" "30")
numberOfCars=("4" "10" "20")
pedLocations=("2" "3" "5")
testcount=0
for timeOfDay in "${timeOfDays[@]}" ; do
for rain in "${rains[@]}" ; do
for fog in "${fogs[@]}" ; do
for pedSpeed in "${pedSpeeds[@]}" ; do
for pedTrigger in "${pedTriggers[@]}" ; do
for numberOfCar in "${numberOfCars[@]}" ; do
for pedLocation in "${pedLocations[@]}" ; do
let "testcount=testcount+1"
testid="TEST_7.2_ROADSIDE_${testcount}"
echo "${testscript}: ${testid}"
${compiler} ${testscript} --testid ${testid} --simSecond ${simSecond} --rain ${rain} --fog ${fog} --timeOfDay ${timeOfDay} --pedSpeed ${pedSpeed} --pedTrigger ${pedTrigger} --numberOfCar ${numberOfCar} --pedLocation ${pedLocation}
done
done
done
done
done
done
done