from RepeatedTimer import RepeatedTimer


class CountdownTimer(object):
        def __init__(self, callback, *args, **kwargs):
                self.countdown_step = 0.1
                self.countdown_reset = -10

                self.rt = RepeatedTimer(self.countdown_step, self.__countdownTick)
                self.countdownTime = self.countdown_reset

                self.callback = callback
                self.args = args
                self.kwargs = kwargs

        def __countdownTick(self):
                self.countdownTime = round(self.countdownTime + self.countdown_step, 1)
                self.callback(*self.args, **self.kwargs)

        def start(self):
                self.rt.start()

        def stop(self):
                self.rt.stop()

        def reset(self):
                self.rt.stop()
                self.countdownTime = self.countdown_reset

        def getTime(self):
                return self.countdownTime

        def getTimeString(self):
                countdownTime = self.countdownTime
                sign = "+"
                if countdownTime < 0:
                        sign = "−"
                        countdownTime = -countdownTime
                hours = int(countdownTime // 3600)
                minutes = int(countdownTime % 3600 // 60)
                seconds = int(countdownTime % 60)
                milliseconds = int(countdownTime % 1 * 1000)
                hundred_milliseconds = int(milliseconds // 100)
                return "t%s %02d:%02d:%02d.%1d" % (sign, hours, minutes, seconds, hundred_milliseconds)
