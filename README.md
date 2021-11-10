# IntelligentChatbot
This is an intelligent bot that can help you to keep a record of your expenses.

About the program flow chart and the technology stack:
![image](https://user-images.githubusercontent.com/88467925/139779637-3945d65d-2663-46cd-a767-b46e7fe61d79.png)

#### User Guide

- If you want to add a record of expense or income, send message to it through the chat window (as the screenshot shown below). Then it will return you some response in template:

> 已记录
> 时间:2021年11月6日
> 类型:支出$666.0

- If you want to query the past record, you can ask it to check (查询) the daily/monthly/yearly records by sending it message including key words “查询” and time description.
- If you add a record by mistake and need to delete it, please ask to check the daily records of the wrong record. Use the ID to delete the record in this format: 

> delete@61838e07f13****
