import pandas as pd
import matplotlib.pyplot as plt
import csv
import random
import time
#from openpyxl import Workbook
import openpyxl
from openpyxl.drawing.image import Image

df = pd.DataFrame(columns=["id","name","points"])
current_time_str = ""

def generate_name():## generate 80 rows to full excel
    first_name = ["大","伟","超","爱国","抗美","援朝","中北","大学","丰亮","杰"]
    last_name = ["赵","钱","孙","李","周","吴","郑","王","刘","禄"]
    tmp_name = random.choice(last_name) + random.choice(first_name)
    return tmp_name

def write_2_excel(): # extend data to 100 
    global df
    for i in range(15):
        tmp_row = pd.DataFrame({"id":[i+1], "name":[generate_name()],"points":[random.randrange(0,100)]})
        df = pd.concat( [df , tmp_row], ignore_index=True, axis = 0  )

    ##debug
    # print(df)
    global current_time_str
    current_time = time.strftime('%Y%m%d%H%M%S', time.localtime())
    current_time_str = current_time + ".xlsx"
    ## debug
    # print(current_time_str)
    df.to_excel(current_time_str,index = False)

def line_chart():
    # fig = plt.figure()
    fig, ax = plt.subplots()
    plt.rcParams['font.sans-serif'] = ['KaiTi']
    
    value_count_frame = df["points"].value_counts().to_frame(name="count")
    value_count_frame = value_count_frame.reset_index()
    print(value_count_frame)

    max_value = max(df["points"])
    # max_index = df["points"].index(max_value)

    max_value = df["points"].max()
    max_index = df["points"].idxmax()

    plt.bar(value_count_frame["points"], value_count_frame["count"])
    ax.annotate(f'Max: {max_value}', xy=(max_index, max_value), xytext=(max_index, max_value + 1),arrowprops=dict(facecolor='black', shrink=0.05))
    ax.set_title('Bar Plot with Max Value Annotation')
    ax.set_xlabel('points')
    ax.set_ylabel('person')
    
    fig.savefig('./fig.png')
    # insert fig into excel
    wb = openpyxl.load_workbook(current_time_str)
    ws = wb.active
    img = Image('fig.png')
    ws.add_image(img,"D4")
    wb.save(current_time_str)

    plt.show()

write_2_excel()
line_chart()