import time
current_time = time.strftime('%Y%m%d%H%M%S', time.localtime())
file_path = current_time + ".txt"
## debug
print(file_path)
fp = open(file_path, "w")
def main():
   for row in range(1, 10):
       for column in range(1, row+1):
           #fp.write("%d * %d = %d ", row+1, column+1, (row+1) * (column+1))
           result_str = "" + str(row) + "*" + str(column) + "=" + str(row * column) + " "
           fp.write(result_str)
       fp.write("\n")
   fp.close()
main()