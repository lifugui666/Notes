import pandas as pd
import matplotlib.pyplot as plt
import csv
import random
#from openpyxl import Workbook
import openpyxl
from openpyxl.drawing.image import Image

data_rows =[
        [100,"李老大",120],
        [101,"李老二",111],
        [102,"李老三",111],
        [103,"李老四",112],
        [104,"李老五",113],
        [105,"李老六",114],
        [106,"李老七",115],
        [107,"李老八",116],
        [108,"李老九",117],
        [109,"李老十",118],
        [110,"李十一",119],
        [111,"李十二",100],
        [112,"李十三",101],
        [113,"李十四",102],
        [114,"李十五",103],
        [115,"李十六",104],
        [116,"李十七",105],
        [117,"李十八",106],
        [118,"李十九",107],
        [119,"李二十",108],
        ] 

def write_2_csv():
    df = pd.DataFrame(data_rows, columns=["id","name","points"])
    df.to_csv("test.csv", index=False)

def generate_name():## generate 80 rows to full excel
    first_name = ["大","伟","超","爱国","抗美","援朝","中北","大学","丰亮","杰"]
    last_name = ["赵","钱","孙","李","周","吴","郑","王","刘","禄"]
    tmp_name = random.choice(last_name) + random.choice(first_name)
    return tmp_name

def write_2_excel(): # extend data to 100 
    data_form_file = pd.read_csv('test.csv')
    df = pd.DataFrame(data_form_file)
    for i in range(80):
        tmp_row = pd.DataFrame({"id":[120 + i], "name":[generate_name()],"points":[random.randrange(60,120)]})
        df = pd.concat( [df , tmp_row], ignore_index=True, axis = 0  )
    df.to_excel('test.xlsx',index = False)

def column_chart():
    df = pd.read_excel('test.xlsx', sheet_name = 'Sheet1')
    # 绘制频率直方图
    value_counts = df["points"].value_counts()
    value_counts.plot(kind = 'bar')
    plt.show()

def line_chart():
    df = pd.read_excel('test.xlsx', sheet_name = "Sheet1")
    df.plot(x = "name", y = "points", kind = "line")
    plt.show()

def gen_pic_save_to_excel():
    df = pd.read_excel('test.xlsx', sheet_name = "Sheet1")
    fig = plt.figure()
    plt.rcParams['font.sans-serif'] = ['KaiTi']
    
    value_count_frame = df["points"].value_counts().to_frame(name="count")
    value_count_frame = value_count_frame.reset_index()
    print(value_count_frame)

    plt1 = plt.subplot(2,1,1)
    plt2 = plt.subplot(2,1,2)
    
    plt1.bar(value_count_frame["points"], value_count_frame["count"])
    plt2.plot(df["id"],df["points"],)

    # save this fig
    fig.savefig('./fig.png')
    # insert fig into excel
    wb = openpyxl.load_workbook('test.xlsx')
    ws = wb.active
    img = Image('fig.png')
    ws.add_image(img,"D4")
    wb.save('test.xlsx')

    plt.show()

write_2_csv()
write_2_excel()
#column_chart()
#line_chart()
gen_pic_save_to_excel()
