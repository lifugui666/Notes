import requests
import datetime
 
# 发送HTTP请求
url = "http://www.baidu.com"  
response = requests.get(url)

if response.status_code == 200:
    server_date = datetime.datetime.strptime(response.headers['Date'], '%a, %d %b %Y %H:%M:%S %Z')
    server_date = server_date.replace(tzinfo=datetime.timezone.utc)
    
    print(f"network time: {server_date}")
else:
    print("Failed to retrieve server time")