import serial
import numpy as np
import time

alldata = []

f = open('data.txt')
lines = f.readline()  # 整行读取数据
datas1 = lines.split('\t')
f.close()

f = open('data1.txt')
lines1 = f.readline()  # 整行读取数据
datas2 = lines1.split('\t')
f.close()

f = open('data2.txt')
lines2 = f.readline()  # 整行读取数据
datas3 = lines2.split('\t')
f.close()
#for i in list(range(1000)):
    #data_float = float(datas[i])
    #alldata.append((data_float))
data=[]

for i in range(0,len(datas1)-1,1):
    data.append(datas2[i])
    data.append(datas1[i])
    data.append(datas3[i])


print(len(data))
print(len(datas1))
print(len(datas2))
print(len(datas3))

#data = np.asarray(alldata)


serialPort = 'COM2'
baudRate=9600       #波特率


if __name__ == "__main__":
    ser=serial.Serial(serialPort,baudRate,timeout=0.5)
    count = 0
    for i in range(0,len(data),1):
        count+=1
        ser.write(data[i].encode())
        time.sleep(0.002)
    print(count)
    ser.close