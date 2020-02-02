from os.path import dirname, join

from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill, intent_handler, intent_file_handler
from mycroft.util.log import getLogger
from mycroft.util.log import LOG
from mycroft.skills.context import adds_context, removes_context
from mycroft.api import DeviceApi
from mycroft.skills.audioservice import AudioService
from mycroft.audio import wait_while_speaking\

import json
import re
import time
import threading
import os
from threading import Timer


class NewThread:
    id = 0
    idStop = False
    next_interval = 0
    idThread = threading.Thread


__author__ = 'PCWii'

# Logger: used for debug lines, like "LOGGER.debug(xyz)". These
# statements will show up in the command line when running Mycroft.
LOGGER = getLogger(__name__)


# The logic of each skill is contained within its own class, which inherits
# base methods from the MycroftSkill class with the syntax you can see below:
# "class ____Skill(MycroftSkill)"
class C25kSkill(MycroftSkill):

    # The constructor of the skill, which calls Mycroft Skill's constructor
    def __init__(self):
        super(C25kSkill, self).__init__(name="C25kSkill")
        # Initialize settings values
        self._is_setup = False
        self.workout_mode = NewThread
        self.schedule_location = ""
        self.interval_position = 0
        self.progress_week = 0
        self.progress_day = 0
        self.halt_all = False
        self.workout_file = ""
        self.audio_service = ""

    # This method loads the files needed for the skill's functioning, and
    # creates and registers each intent that the skill uses
    def initialize(self):
        self.load_data_files(dirname(__file__))
        #  Check and then monitor for credential changes
        self.audio_service = AudioService(self.bus)
        self.settings.set_changed_callback(self.on_websettings_changed)
        self.on_websettings_changed()
        # Todo Add / update the following to the websettings for tracking
        location = os.path.dirname(os.path.realpath(__file__))
        self.schedule_location = location + '/./schedules/'  # get the current skill parent directory path
        self.interval_position = 0
        # self.progress_week = 9
        # self.progress_day = 3
        # self.workout_file = ""
        self.halt_all = False

    def on_websettings_changed(self):  # called when updating mycroft home page
        self._is_setup = False
        LOG.info("Websettings Changed!")
        self.progress_week = self.settings.get("progress_week", 1)
        self.progress_day = self.settings.get("progress_day", 1)
        self.workout_file = self.settings.get("workout_file", "c25k.json")
        self._is_setup = True

    def load_file(self, filename):  # loads the workout file json
        with open(filename) as json_file:
            data = json.load(json_file)
            return data

    def end_of_interval(self):
        LOG.info('Interval Completed!')
        self.interval_position += 1

    def end_of_workout(self):
        LOG.info('Workout Ended!')
        self.halt_workout_thread()

    def init_workout_thread(self):  # creates the workout thread
        self.workout_mode.idStop = False
        self.workout_mode.id = 101
        self.workout_mode.idThread = threading.Thread(target=self.do_workout_thread,
                                                      args=(self.workout_mode.id,
                                                            lambda: self.workout_mode.idStop))
        self.workout_mode.idThread.start()

    def halt_workout_thread(self):  # requests an end to the workout
        try:
            self.workout_mode.id = 101
            self.workout_mode.idStop = True
            self.workout_mode.idThread.join()
        except Exception as e:
            LOG.error(e)  # if there is an error attempting the workout then here....

    def do_workout_thread(self, my_id, terminate):  # This is an independant thread handling the workout
        LOG.info("Starting Workout with ID: " + str(my_id))
        active_schedule = self.load_file(self.schedule_location + self.workout_file)  # "test_schedule.json")
        schedule_name = active_schedule["Name"]
        this_week = active_schedule["weeks"][self.progress_week - 1]
        this_day = this_week["day"][self.progress_day - 1]
        all_intervals = this_day["intervals"]
        last_interval = len(all_intervals)
        LOG.info('Last Interval = ' + str(last_interval))
        workout_duration = 0
        for each_interval in this_day["intervals"]:
            for interval_type in each_interval:
                workout_duration = workout_duration + each_interval[interval_type]
        workout_duration = int(workout_duration / 60)  # minutes
        wait_while_speaking()
        self.speak_dialog('details_000', data={"name": schedule_name},
                          expect_response=False)
        wait_while_speaking()
        self.speak_dialog('details_001', data={"week": this_week["Name"], "day": this_day["Name"]},
                          expect_response=False)
        wait_while_speaking()
        self.speak_dialog('details_002', data={"duration": str(workout_duration)},
                          expect_response=False)
        wait_while_speaking()
        self.speak_dialog('details_003', data={"intervals": str(last_interval)},
                          expect_response=False)
        interval_list = enumerate(all_intervals)
        try:
            for index, value in interval_list:
                this_interval = json.dumps(all_intervals[index])
                for key in all_intervals[index]:
                    this_duration = all_intervals[index][key]
                    LOG.info("Workout Type: " + key)
                    workout_type = key
                LOG.info("Workout Interval Length: " + str(this_duration) + " seconds")
                LOG.info("Workout underway at step: " + str(index + 1) + "/" + str(last_interval) +
                         ", " + str(this_interval))
                notification_threads = []  # reset notification threads
                # Insert general workout prompts here
                # Each workout prompt below is a separate thread timer
                if this_duration >= 10:  # Motivators only added if interval length is greater than 10 seconds
                    notification_threads.append(Timer(int(this_duration - 6), self.speak_countdown))
                if this_duration >= 30:  # Motivators only added if interval length is greater than 30 seconds
                    notification_threads.append(Timer(int(this_duration / 2), self.speak_mid_point))
                    notification_threads.append(Timer(int(this_duration - 10), self.speak_transition))
                if this_duration >= 120:  # Motivators only added if interval length is greater than 2 minutes seconds
                    first_quarter = int(this_duration / 4)
                    last_quarter = first_quarter * 3
                    notification_threads.append(Timer(int(first_quarter), self.speak_first_quarter))
                    notification_threads.append(Timer(int(last_quarter), self.speak_last_quarter))
                if index == (last_interval - 1):  # Check for the last interval
                    notification_threads.append(Timer(this_duration, self.end_of_workout))
                    LOG.info('Last Interval workout almost completed!')
                else:
                    notification_threads.append(Timer(this_duration, self.end_of_interval))
                for each_thread in notification_threads:
                    each_thread.start()
                wait_while_speaking()
                self.speak_dialog('details_004', data={"interval_length": str(this_duration),
                                                       "interval_type": workout_type},
                                  expect_response=False)
                interval_start_mp3 = "ding_001.mp3"
                self.audio_service.play(join(dirname(__file__), "soundclips", interval_start_mp3))
                while (index == self.interval_position) and not terminate():  # wait while this interval completes
                    time.sleep(1)
                    # This is a do nothing loop while the workout proceeds
                if terminate():
                    for each_thread in notification_threads:
                        each_thread.cancel()
                        self.interval_position = 0
                    if index != (last_interval - 1):
                        LOG.info('Workout was terminated!')
                    else:
                        LOG.info('Workout was Completed!')
                        # update the day and week schedule for next run
                        if self.progress_day == len(this_week["day"]):
                            self.progress_day = 1
                            if self.progress_week == len(active_schedule["weeks"]):
                                self.progress_week = 1
                            else:
                                self.progress_week += 1
                                self.settings["progress_week"] = self.progress_week
                        else:
                            self.progress_day += 1
                            self.settings["progress_day"] = self.progress_day
                        self.speak_workout_completed()
                    break
        except Exception as e:
            LOG.error(e)  # if there is an error attempting the workout then here....
            for each_thread in notification_threads:
                each_thread.cancel()

    def speak_mid_point(self):
        self.speak_dialog('mid_point', expect_response=False)

    def speak_first_quarter(self):
        self.speak_dialog('first_quarter', expect_response=False)

    def speak_last_quarter(self):
        self.speak_dialog('last_quarter', expect_response=False)

    def speak_transition(self):
        self.speak_dialog('transitions', expect_response=False)

    def speak_countdown(self):
        count_down = 5
        while count_down and not self.halt_all:
            self.speak_dialog('countdown', data={"value": str(count_down)}, expect_response=False)
            count_down -= 1
            time.sleep(1)

    def speak_workout_completed(self):
        self.speak_dialog('completed', expect_response=False)

    def get_change(self, payload):
        request_change = False
        week_matches = re.search(r'(?P<weeks>week \d+)', payload)
        if week_matches:
            utt_week = re.findall("\d+", week_matches.group('weeks'))[0]
            LOG.info("Caught week: " + str(utt_week))
        else:
            request_change = True
        day_matches = re.search(r'(?P<days>day \d+)', payload)
        if day_matches:
            utt_day = re.findall("\d+", day_matches.group('days'))[0]
            LOG.info("Caught day: " + str(utt_day))
        else:
            request_change = True
        if request_change:
            return "none"
        else:
            return str(utt_week, utt_day)

    @intent_handler(IntentBuilder("BeginWorkoutIntent").require("RequestKeyword").require('WorkoutKeyword').build())
    def handle_begin_workout_intent(self, message):
        self.halt_all = False
        self.init_workout_thread()
        LOG.info("The workout has been Started")

    @intent_handler(IntentBuilder('StopWorkoutIntent').require('StopKeyword').require('WorkoutKeyword').build())
    def handle_stop_workout_intent(self, message):
        self.halt_all = True
        self.halt_workout_thread()
        LOG.info("The workout has been Stopped")
        self.speak_dialog('shutdown', expect_response=False)

    @intent_handler(IntentBuilder('ChangeWorkoutIntent').require('ChangeKeyword').require('WorkoutKeyword').build())
    def handle_change_workout_intent(self, message):
        voice_payload = str(message.data.get('utterance'))
        self.halt_all = True
        self.halt_workout_thread()
        LOG.info("Workout change requested")
        change_data = self.get_change(voice_payload)
        LOG.info("Change Request returned: " + str(change_data))
#        if request_change:
#            change_payload = self.get_response('request_change')
        # todo add conversation if week / day is not included in the utterance

    def stop(self):
        pass


# The "create_skill()" method is used to create an instance of the skill.
# Note that it's outside the class itself.
def create_skill():
    return C25kSkill()
