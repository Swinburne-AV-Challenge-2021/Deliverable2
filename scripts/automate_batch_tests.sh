

# TEST GROUP NO.6 
# ASSOCIATED WITH PEDESTRIAN AT INTERSECTION AND AFFECTED BY WEATHER
compiler=python3
testscript=08-pedestrian-intersection-weather.py
simSecond=60
timeOfDay=12
rains=("0" "0.5" "1.0")
fogs=("0" "0.5" "1.")
wetnesses=("0" "0.5" "1.")
cloudinesses=("0" "0.5" "1.")
damages=("0" "0.5" "1.")
testcount=0
for rain in "${rains[@]}" ; do
for fog in "${fogs[@]}" ; do
for wetness in "${wetnesses[@]}" ; do
for cloudiness in "${cloudinesses[@]}" ; do
for damage in "${damages[@]}" ; do
let "testcount=testcount+1"
testid="TEST_${testcount}"
echo "${testscript}: ${testid}"
${compiler} ${testscript} --testid ${testid} --simSecond ${simSecond} --timeOfDay ${timeOfDay} --rain ${rain} --fog ${fog} --wetness ${wetness} --cloudiness ${cloudiness} --damage ${damage}
done
done
done
done
done