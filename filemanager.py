class File:

    lastTimeFile = 0
    samplesMax = 100 #save this number of rows in file, each time
    samples = 0
    fileName = ""
    filePath = ""
    lineToWrite=""
    totalSamples = 0
    is_file_created = False
    rowMaxEachFile = 20000

    def __init__(self, lastTimeFile, fileName, sensor_list):
        self.lastTimeFile = lastTimeFile
        self.sensor_list = sensor_list
        #the code below raise error if partition is not mounted in write
        with open("/file.txt", "w", encoding='utf-8-sig') as fp:
            pass
        self.fileName = fileName

    def createFile(self):
        if "logs" not in os.listdir():
                os.mkdir("/logs")
        for index in range(100):
            self.filePath = "/logs/"+self.fileName+str(index)+".csv"
            if self.filePath[6:] not in os.listdir("/logs/"):
                with open(self.filePath, "w", encoding='utf-8-sig') as fp:
                    fp.seek(0)
                    title=""
                    for sensor in self.sensor_list:
                        title+=sensor.get_label()+';'
                    title+="\n"
                    fp.write(title)
                    fp.flush()
                    fp.close()
                    print(self.filePath)
                    self.is_file_created = True
                return
        raise NameError('too much files in current directory')

    def saveLineToWriteOnFile(self,forceEnd):
        #for excel
        self.lineToWrite = self.lineToWrite.replace('.',',')
        with open(self.filePath, "a") as fp:
            print(self.lineToWrite)
            fp.write(self.lineToWrite)
            fp.flush()
            fp.close()
        self.samples=0
        self.lineToWrite=""
        if forceEnd or self.totalSamples >= self.rowMaxEachFile:
            self.is_file_created = False
            return True
        return False

    def createLineTOWrite(self):
        for sensor in self.sensor_list:
            self.lineToWrite += sensor.get_sensor_value_string()+';'
        self.lineToWrite+="\n"
        self.samples += 1
        self.totalSamples += 1
        return False

    def logSensors(self, delaySec, forceEnd):
        if not self.is_file_created:
            self.createFile()
        if self.samples >= self.samplesMax or forceEnd or self.totalSamples >= self.rowMaxEachFile:
            return self.saveLineToWriteOnFile(forceEnd)
        elif time.monotonic() - self.lastTimeFile >= delaySec :
            self.lastTimeFile = time.monotonic()
            return self.createLineTOWrite()

    def logSensorsNoDelay(self, forceEnd):
        if not self.is_file_created:
            self.createFile()
        if self.samples >= self.samplesMax or forceEnd or self.totalSamples >= self.rowMaxEachFile:
            return self.saveLineToWriteOnFile(forceEnd)
        else:
            return self.createLineTOWrite()

