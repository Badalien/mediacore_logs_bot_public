from mediacore import mediacore
from telegram import telegram as tg
from google_api import google_client
from db import db
from multiprocessing import Pool
from pathlib import Path
import logging
import sys
from typing import List

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger

# Interval when need to check logs
# Need to define while run command: python3 main.py --check-delay=X
diff = int(sys.argv[1].split("=")[1])

prod_mode = True # bool value to setup production mode

parent_directory = str(Path().absolute())
log_file = parent_directory + '/logs/mc-logs-full.log'
logging.basicConfig(
    filename=log_file,
    filemode='a',
    format='[%(asctime)s] {%(name)s}: %(levelname)s: %(message)s',
    datefmt='%m/%d/%Y %H:%M:%S',
    level=logging.INFO
)

logger = logging.getLogger("MAIN")

mc = mediacore.Mediacore(ignore_test = prod_mode)
google = google_client.GoogleClient()
# db = db.DB()
scheduler = BlockingScheduler()


@scheduler.scheduled_job(IntervalTrigger(seconds=diff), max_instances=15)
def send_logs() -> None:
    # logs = mc.getLogs(diff)
    logs = handling_logs()
    anis = mc.getANIchanges(diff)
    logs.extend(anis)

    for l in logs:
        if (prod_mode):
            tg.sendMessage(l)
        else:
            tg.sendMessageTest(l)
    
    
# here we proceed a list of changes
def handling_logs() -> List[str]:
    logs_list = mc.getLogsAsList(diff + 2)

    output = []

    # making output strings for sending to telegram (as function mc.getLogs() do)
    for log in logs_list:
        output_string_logs = "<i>{}</i> · {} · <b>{}</b> · p=<b>{}</b> · {} д\\п <b>{}</b> · {}".format(
                log['user'],
                "добавил" if (log['action'] == 'insert') else "удалил",
                log['vendor'],
                log['priority'],
                log['to_from'],
                log['dialpeer'],
                mc.format_output_date(log['time'])
            )
        output.append(output_string_logs)
        country = log['dialpeer'].rsplit("_")[0]
        # insert changes to MySQL database and Google Table
        if prod_mode:
            try:
                result = google.write_sheet(log['user'], log['action'], log['vendor'], log['priority'], country, log['dialpeer'], log['time'])
                logger.info(f'Data sent to Google: {result}')
            except:
                logger.exception('Data not sent to Google:')
        # db.update_changes_no_reason(mc.format_output_date(log['time']), log['user'], log['action'], log['vendor'], log['priority'], log['dialpeer'], country)

    return output
    


def main_loop():
    scheduler.start()


if __name__ == '__main__':
    # pool = Pool(processes=2)
    # r1 = pool.apply_async(main_loop)
    # r2 = pool.apply_async(tg.startPolling())
    # pool.close()
    # pool.join()

    main_loop()
