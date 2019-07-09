import numpy as np
import matplotlib.pyplot as plt

# 滑动平均滤波器
def filter(data):
    filtered = []
    filtered.append(data[0])
    for i in np.arange(1, len(data) - 1, 1):
        data[i] = (data[i - 1] + data[i] + data[i + 1]) / 3
        filtered.append(data[i])
    filtered.append(data[len(data) - 1])
    return filtered

# 找出波峰的编号
def find_p(data):
    p = []
    for i in np.arange(20, len(data) - 20, 1):
        count = 0
        for k in np.arange(i - 20, i + 20, 1):
            if data[i] > data[k]:
                count += 1
        if count >= 39:
            p.append(i)
    return p

# 找出波谷的编号
def find_v(data):
    v = []
    for i in np.arange(20, len(data) - 20, 1):
        count = 0
        for k in np.arange(i - 20, i + 20, 1):
            if data[i] < data[k]:
                count += 1
        if count >= 39:
            v.append(i)
    return v

# 找出峰峰值
def find_pp(data):
    pp = []
    p = find_p(data)
    v = find_v(data)
    for i in range(0,min(len(p),len(v)),1):
        pp.append(data[p[i]]-data[v[i]])
    return pp

# 找出周期
def find_period(data):
    t = []
    p = find_p(data)
    for i in range(1,len(p),1):
        t.append(p[i]-p[i-1])
    ave_t = sum(t)/len(t)
    return ave_t*0.006

# 找出标准差
def find_e(data):
    ave = data.sum / len(data)
    e = data.max - ave
    return e



if __name__=="__main__":
    #print(data[0])

    alldata = []

    f = open('data1.txt')
    lines = f.readline()  # 整行读取数据
    datas = lines.split('\t')

    for i in list(range(1000)):
        data_float = float(datas[i])
        alldata.append((data_float))

    # print(alldata)

    data = np.asarray(alldata)
    f.close()



    print(find_p(filter(data)))
    print(find_v(filter(data)))
    print(find_period((data)))
    x = np.asarray(list(range(1000)))
    print(find_pp(data))
    #plt.plot(x, data)
    #plt.show()
    plt.plot(x,filter(data))
    plt.show()

    #data1,data2,data3 = depart_data(data)
    #print(data1)
    #print(data2)