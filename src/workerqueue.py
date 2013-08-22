from threading import Thread, Lock
from time import sleep
import random

class WorkerThread(Thread):
  __sleepTime = 3
  work = True

  def __init__(self, *args, **kwargs):
    super(WorkerThread, self).__init__(*args, **kwargs)

  def run(self):
    while True:
      sleep(self.__sleepTime)
      self.doTheJob()
      if not self.work: 
        break
  
  def doTheJob(self):
    print "Starting do the job"
    queue = WorkerQueue().popQueue()
    for el in queue:
      print el  

class WorkerQueue(object):
  __instance = None
  __initialized = False

  __queue = []
  __worker_thread = None
  __queue_lock = None

  def __init__(self, *args, **kwargs):
    if self.__initialized: return
    self.__initialized = True
    print "initializing"
    self.__queue_lock = Lock()
    self.__worker_thread = WorkerThread()
    self.__worker_thread.start()
    super(WorkerQueue, self).__init__(*args, **kwargs)

  def stop(self):
    self.__worker_thread.work = False
    self.__worker_thread.join()


  def popQueue(self):
    self.__queue_lock.acquire()
    old_queue = list(self.__queue)
    self.__queue = []
    self.__queue_lock.release()
    return old_queue

  def addTask(self, task):
    self.__queue_lock.acquire()
    self.__queue.append(task)
    self.__queue_lock.release()


  def __new__(cls, *args, **kwargs):
      if not cls.__instance: 
        cls.__instance = super(WorkerQueue, cls).__new__(cls, *args, **kwargs)
      return cls.__instance


# for i in range(20):
#   WorkerQueue().addTask(str(i))
#   t = random.randint(100, 2000)
#   sleep(float(t) / 1000)

# WorkerQueue().stop()

import sys
import unittest

class TestSingletons(unittest.TestCase):

  def test_single(self):
    print "test2"
    dbh1 = WorkerQueue()
    dbh2 = WorkerQueue()
    print id(dbh1), id(dbh2)
    self.assertEqual(id(dbh1), id(dbh2))

  def tearDown(self):
    WorkerQueue().stop()




if __name__ == "__main__":
  unittest.main()