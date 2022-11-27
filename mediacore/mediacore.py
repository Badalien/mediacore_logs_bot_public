from asyncio.log import logger
import json
import re
from utils import encoder
from utils import requests
from datetime import datetime
from datetime import timedelta
from pathlib import Path
import pytz
import logging
from typing import List


parent_directory = str(Path().absolute())

with open(parent_directory + '/mediacore/config.json') as config_file:
    data = json.load(config_file)

log_file = parent_directory + '/logs/' + data['log_file']
logging.basicConfig(
    filename=log_file,
    filemode='a',
    format='[%(asctime)s] {%(name)s}: %(levelname)s: %(message)s',
    datefmt='%m/%d/%Y %H:%M:%S',
    level=logging.INFO
)

logger = logging.getLogger("MEDIACORE")

class Mediacore:

    def __init__(self, ignore_test: bool = True) -> None:
        self.username = data['cred']['username']
        self.password = data['cred']['password']
        self.ip = data['ip']
        self.session_id = None
        self.format_mc = "%Y-%m-%dT%H:%M:%S"
        self.logs_prev_changes = []
        self.ani_prev_changes = []
        self.default_fields = [
            'row_id',
            'user',
            'date',
            'action',
            'field_name',
            'old_value',
            'new_value'
        ]
        self.ignore_test = ignore_test
        self.ignore_names = [
            'test_'
        ]


    def login(self) -> None:
        url = data['mc_base_url'] + data['methods']['login']
        payload = {
            'login': self.username,
            'password': self.password,
            'ip': self.ip
        }
        payload = json.dumps(payload)

        output = requests.sendPost(url, payload)
        if (output['status'] == 200):
            self.session_id = output['session_id']
            logger.debug(f'Successful login: {self.session_id}')
        else:
            logger.error(f'Can not login! Output: {output}')
            exit(0)

    # this function return list of dics with changing params 
    def getLogsAsList(self, diff: int) -> List[dict]:
        if (self.session_id is None):
            self.login()
        
        url = data['mc_base_url'] + data['methods']['logs']
        now = datetime.now(pytz.timezone('Europe/Moscow'))
        from_date = (now - timedelta(0, diff, 0)).strftime(self.format_mc)
        to_date = now.strftime(self.format_mc)
        # set payload for TP changes action
        payload_logs = {}
        payload_logs['session_id'] = self.session_id
        data_logs = {
            'limit': 100,
            'date_from': from_date,
            'date_to': to_date,
            'offset': 0,
            'time_zone': '+03:00',
            'table': 'routing_cz.rel_dialpeer_tp',
        }

        data_logs['fields'] = self.default_fields
        payload_logs['data'] = data_logs
        payload_logs = json.dumps(payload_logs, cls=encoder.SetEncoder)

        output_logs = requests.sendPost(url, payload_logs)
        try:
            result_logs = output_logs['data']
            if result_logs:
                logger.debug(f'Logs data: {result_logs}')
        except KeyError:
            logger.exception(f'Incorrect output: {output_logs}');
            raise KeyError

        
        output_list = []
        current_changes = []
        output_row = []
        # define variables for further output
        user, action, vendor, to_from, dp, time,priority = '','','','','','',''
        priority_list = []

        for row in result_logs:
            if (row[4] == 'priority'):
                priority_list.append(row)
        # parse MC output and generate output message for TP changes
        for row in result_logs:
            if (row[4] == 'tp'):
                if (self.ignore_test and self.check_ignore_values(row[0])):
                    continue

                user = row[1]
                action = row[3]
                vendor = row[6] if (row[3] == "insert") else row[5]
                to_from = "в" if (row[3] == "insert") else "из"
                dp = row[0]
                time = row[2]
                
                for p in priority_list:
                    if (p[2] == time):
                        priority = p[6] if (p[3] == "insert") else p[5]

                output_row = {
                    'user' : user,
                    'action' : action,
                    'vendor' : vendor,
                    'dialpeer' : dp,
                    'to_from' : to_from,
                    'time' : time,
                    'priority' : priority if (priority) else "0",
                }
            else:
                continue

            if (output_row not in self.logs_prev_changes and output_row not in current_changes):
                output_list.append(output_row)
                current_changes.append(output_row)

        # store received data to not duplicate messages 
        self.logs_prev_changes.clear()
        self.logs_prev_changes.extend(current_changes)

        return output_list

    # this function return prepared string for sending to telegram
    def getLogs(self, diff: int) -> List[str]:
        if (self.session_id is None):
            self.login()
        
        url = data['mc_base_url'] + data['methods']['logs']
        now = datetime.now(pytz.timezone('Europe/Moscow'))
        from_date = (now - timedelta(0, diff, 0)).strftime(self.format_mc)
        to_date = now.strftime(self.format_mc)
        # set payload for TP changes action
        payload_logs = {}
        payload_logs['session_id'] = self.session_id
        data_logs = {
            'limit': 100,
            'date_from': from_date,
            'date_to': to_date,
            'offset': 0,
            'time_zone': '+03:00',
            'table': 'routing_cz.rel_dialpeer_tp',
        }

        data_logs['fields'] = self.default_fields
        payload_logs['data'] = data_logs
        payload_logs = json.dumps(payload_logs, cls=encoder.SetEncoder)

        output_logs = requests.sendPost(url, payload_logs)
        try:
            result_logs = output_logs['data']
            if result_logs:
                logger.debug(f'Logs data: {result_logs}')
        except KeyError:
            logger.exception(f'Incorrect output: {output_logs}');
            raise KeyError
        
        output = []
        current_changes = []
        # define variables for further output
        user, action, vendor, to_from, dp, time,priority = '','','','','','',''
        priority_list = []

        for row in result_logs:
            if (row[4] == 'priority'):
                priority_list.append(row)
        # parse MC output and generate output message for TP changes
        for row in result_logs:
            if (row[4] == 'tp'):
                if (self.ignore_test and self.check_ignore_values(row[0])):
                    continue

                user = row[1]
                action = "добавил" if (row[3] == "insert") else "удалил"
                vendor = row[6] if (row[3] == "insert") else row[5]
                to_from = "в" if (row[3] == "insert") else "из"
                dp = row[0]
                time = row[2]
                
                for p in priority_list:
                    if (p[2] == time):
                        priority = p[6] if (p[3] == "insert") else p[5]
                    

            if (user == ''):
                continue

            output_string_logs = "<i>{}</i> · {} · <b>{}</b> · p=<b>{}</b> · {} д\\п <b>{}</b> · {}".format(
                user,
                action,
                vendor,
                priority if (priority) else "0",
                to_from,
                dp,
                self.format_output_date(time)
            )
            if (output_string_logs not in self.logs_prev_changes and output_string_logs not in current_changes):
                output.append(output_string_logs)
                current_changes.append(output_string_logs)

        # store received data to not duplicate messages 
        self.logs_prev_changes.clear()
        self.logs_prev_changes.extend(current_changes)

        return output


    def getANIchanges(self, diff: int) -> List[str]:
        if (self.session_id is None):
            self.login()
        
        url = data['mc_base_url'] + data['methods']['logs']
        now = datetime.now(pytz.timezone('Europe/Moscow'))
        from_date = (now - timedelta(0, diff, 0)).strftime(self.format_mc)
        to_date = now.strftime(self.format_mc)

        # set payload for ANI changes action
        payload_ani = {}
        payload_ani['session_id'] = self.session_id
        data_ani = {
            'limit': 100,
            'date_from': from_date,
            'date_to': to_date,
            'offset': 0,
            'time_zone': '+03:00',
            'table': 'dialpeers',
        }
        data_ani['fields'] = self.default_fields
        payload_ani['data'] = data_ani
        payload_ani = json.dumps(payload_ani, cls=encoder.SetEncoder)

        output_ani = requests.sendPost(url, payload_ani)
        try:
            result_ani = output_ani['data']
            if result_ani:
                logger.debug(f'Logs data: {result_ani}')
        except KeyError:
            logger.exception(f'Incorrect output: {output_ani}');
            raise KeyError

        output = []
        current_changes = []
        # parse MC output and generate output message for ANI changes
        for row in result_ani:
            if (row[4] == 'ani_regexp'):
                if (self.ignore_test and self.check_ignore_values(row[0])):
                    continue
                output_string_ani = "{} {} д\\п {} в {}".format(
                    row[1],
                    "изменил ANI\n{} на {}\nв".format(row[5], row[6]) if (row[5] != None and row[6] != None) else "{} ANI\n{}\n{}".format(
                        "удалил" if (row[5] != None) else "добавил",
                        row[5] if (row[5] != None) else row[6],
                        "из" if (row[5] != None) else "в"
                    ),
                    row[0],
                    self.format_output_date(row[2])
                )
                if (output_string_ani not in self.ani_prev_changes and output_string_ani not in current_changes):
                    output.append(output_string_ani)
                    current_changes.append(output_string_ani)

        # store received data to not duplicate messages 
        self.ani_prev_changes.clear()
        self.ani_prev_changes.extend(current_changes)

        return output


    # convert MC time format to human readable time
    def format_output_date(self, date: str) -> str:
        date = date.split('T')  # type: ignore
        day = date[0]
        time = date[1].split('.')[0]
        return day + " " + time

    # check if DP name equal to some value to ignore it (to skip test DPs)
    def check_ignore_values(self, dp_name: str) -> bool:
        dp_name = dp_name.lower()
        for n in self.ignore_names:
            if n in dp_name:
                return True
        return False
