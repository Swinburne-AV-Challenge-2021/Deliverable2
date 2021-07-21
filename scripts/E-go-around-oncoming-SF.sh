# TEST CATEGORY 11: GO AROUND ONCOMING CAR - SAN FRANCISCO MAP
# ......................
compiler=python3
testscript=E-go-around-oncoming-SF.py
simSecond=120
# ......................
# TEST GROUP 11.1: TEST IMPACT OF WEATHER
# ......................
timeOfDays=("12" "0")
rains=("0" "0.5" "1.0")
fogs=("0" "0.5" "1.0")
testcount=0
for timeOfDay in "${timeOfDays[@]}" ; do
for rain in "${rains[@]}" ; do
for fog in "${fogs[@]}" ; do
let "testcount=testcount+1"
testid="TEST_11.1_WEATHER_${testcount}"
echo "${testscript}: ${testid}"
${compiler} ${testscript} --testid ${testid} --simSecond ${simSecond} --timeOfDay ${timeOfDay} --rain ${rain} --fog ${fog}
done
done
done
# ......................
# TEST GROUP 11.2: TEST FOR DIFFERENT POSITION OF ONCOMING
# ......................
timeOfDays=("12" "0")
rains=("0" "1.0")
fogs=("0" "1.0")
carSpeed1s=("5" "15" "50" "100")
carSpeed2s=("10" "50")
carSpeed3s=("10" "50")
testcount=0
for timeOfDay in "${timeOfDays[@]}" ; do
for rain in "${rains[@]}" ; do
for fog in "${fogs[@]}" ; do
for carSpeed1 in "${carSpeed1s[@]}" ; do
for carSpeed2 in "${carSpeed2s[@]}" ; do
for carSpeed3 in "${carSpeed3s[@]}" ; do
let "testcount=testcount+1"
testid="TEST_11.2_ONCOMING_${testcount}"
echo "${testscript}: ${testid}"
${compiler} ${testscript} --testid ${testid} --simSecond ${simSecond} --rain ${rain} --fog ${fog} --timeOfDay ${timeOfDay} --carSpeed1 ${carSpeed1} --carSpeed2 ${carSpeed2} --carSpeed3 ${carSpeed3}
done
done
done
done
done
done