# TEST CATEGORY 8: TEST PEDESTRIAN AT INTERSECTION
# ......................
compiler=python3
testscript=B-pedestrian-intersection.py
simSecond=60
# ......................
# TEST GROUP 8.1: TEST IMPACT OF WEATHER
# ......................
damages=("0" "1.")
timeOfDays=("12" "24")
rains=("0" "0.5" "1.0")
fogs=("0" "0.5" "1.0")
wetnesses=("0" "0.5" "1.0")
cloudinesses=("0" "0.5" "1.0")
testcount=0
for damage in "${damages[@]}" ; do
for timeOfDay in "${timeOfDays[@]}" ; do
for rain in "${rains[@]}" ; do
for fog in "${fogs[@]}" ; do
for wetness in "${wetnesses[@]}" ; do
for cloudiness in "${cloudinesses[@]}" ; do
let "testcount=testcount+1"
testid="TEST_8.1_WEATHER_${testcount}"
echo "${testscript}: ${testid}"
${compiler} ${testscript} --testid ${testid} --simSecond ${simSecond} --rain ${rain} --fog ${fog} --wetness ${wetness} --cloudiness ${cloudiness} --damage ${damage} --timeOfDay ${timeOfDay}
done
done
done
done
done
done
# ......................
# TEST GROUP 8.2: TEST IMPACT OF PEDESTRIAN LOCATION & SPEED
# ......................
damages=("0" "1.")
timeOfDays=("12" "0")
rains=("0" "1.0")
fogs=("0" "1.0")
pedSpeeds=("6" "8" "10")
pedTriggers=("14" "24" "32")
pedDistanceFromIntersections=("6" "9" "12")
testcount=0
for damage in "${damages[@]}" ; do
for timeOfDay in "${timeOfDays[@]}" ; do
for rain in "${rains[@]}" ; do
for fog in "${fogs[@]}" ; do
for pedSpeed in "${pedSpeeds[@]}" ; do
for pedTrigger in "${pedTriggers[@]}" ; do
for pedDistanceFromIntersection in "${pedDistanceFromIntersections[@]}" ; do
let "testcount=testcount+1"
testid="TEST_8.2_PEDESTRIAN_${testcount}"
echo "${testscript}: ${testid}"
${compiler} ${testscript} --testid ${testid} --simSecond ${simSecond} --rain ${rain} --fog ${fog} --damage ${damage} --timeOfDay ${timeOfDay} --pedSpeed ${pedSpeed} --pedDistanceFromIntersection ${pedDistanceFromIntersection} --pedTrigger ${pedTrigger}
done
done
done
done
done
done
done