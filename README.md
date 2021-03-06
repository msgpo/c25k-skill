# <img src='https://raw.githack.com/FortAwesome/Font-Awesome/master/svgs/solid/couch.svg' card_color='#40DBB0' width='50' height='50' style='vertical-align:bottom'/> <img src='https://raw.githack.com/FortAwesome/Font-Awesome/master/svgs/solid/arrow-circle-right.svg' card_color='#40DBB0' width='50' height='50' style='vertical-align:bottom'/><img src='https://raw.githack.com/FortAwesome/Font-Awesome/master/svgs/solid/running.svg' card_color='#40DBB0' width='50' height='50' style='vertical-align:bottom'/> C25k 
Use mycroft.ai as a fitness coach and work your way through the 9 week 
Couch to 5km running program.
## About
Mycroft.ai becomes your motivational coach as you work your way through each of the intervals in the workout.
* Depending on the length of the current interval motivations will be provided at the 1/4, 1/2, 3/4
points of the interval.
This skill uses a schedule json (c25k.json) to track and support you as you work 
through the couch to 5k running program.
The default c25k.json file is based on the Couch to 5 km running program.
Other workout json files could be created based on this and selected from the websettings.

The skill will keep track of the last week #, day # that you completed and proceed through each day
of the workout found in the json file.
* The skill will loose this information if the mycroft is rebooted or the skill is updated.
    - Mycroft does not properly push websettings changes in skills to the web ui.
    - I will work to address this in future updates (20200202).

## Examples
* "Start my workout"
* "Start my run"
* "I want to run"
* "Change my workout to week 3 day 4" (This can also be done in websettings)
    - [ ] WIP (20200202)
    

## Credits
pcwii

## Category
**Fitness**

## Tags
#C25K
#fitness
#running
#workout

## Installation Notes
- msm install https://github.com/pcwii/c25k-skill.git
- set websettings to your active week / day
    - Mycroft does not properly push websettings changes in skills to the web ui.
    - this will not update upon completion although mycroft will remember last workout until a power loss or reboot

## Requirements
- none

## ToDo
- [ ] Provide ability to select/deselect motivations at different intervals in websettings
- [ ] Ability to update websettings with current workout interval
- [ ] Ability to store current workout interval for power loss or skill update
- [ ] Ability to query Mycroft.ai for the next workout schedule

## Overview
<img src='http://www.tombenninger.com/files/2011/09/VisualC25K.v1_0b.png'/>

