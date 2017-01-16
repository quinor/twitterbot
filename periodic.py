#!/usr/bin/env python3
import schedule
import time
import traceback
import signal
import sys
from crawl import crawl
 
def signal_term_handler(signal, frame):
    print ("stopped!\n")
    sys.exit(0) 

def safe_crawl():
  try:
    crawl()
  except:
    print("Something has blown up!")
    print(traceback.format_exc())

schedule.every(5).minutes.do(safe_crawl)


if __name__ == '__main__':
  signal.signal(signal.SIGTERM, signal_term_handler)
  while True:
    schedule.run_pending()
    time.sleep(1)
