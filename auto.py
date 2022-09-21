#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Software: PyCharm
# @Time    : 2021/10/30 18:28
# @File    : auto.py
# @Author  : XueJinLong

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from tkinter import messagebox
import tkinter
import datetime, time, threading, sys, getopt

# 此处填写谷歌驱动器路径
driverpath = "data/chromedriver.exe"
argv = sys.argv[1:]
try:
    opts, args = getopt.getopt(argv, "hp:u:t", ["user=", "password=", "time="])
except getopt.GetoptError:
    print("python auto.py -u <username> -p <password> -t <time>")
    exit(0)
user = ""
password = ""
total_time = 8
for opt, arg in opts:
    if opt == "-h":
        print("python auto.py -u <username> -p <password> -t <time>")
        exit(0)
    elif opt == "-u":
        user = arg
    elif opt == "-p":
        password = arg
    elif opt == "-t":
        total_time = arg

if user == "" or password == "":
    print("用户名或密码为空，请使用以下格式指定运行：\npython auto.py -u <username> -p <password> -t <time>")
    exit(0)
user_info = user + "#" + password

# 初始化记录
record = ""
driver = None


# 自定义打印格式
def my_print(str):
    print("┌===================================================================┐")
    print("\t" + str)
    print("└===================================================================┘")


# 计算预计剩余时间
def cal_res_time(learn_time):
    learn_time = str(learn_time)
    if "分" not in learn_time:
        learn_time = "0分" + learn_time
    if "时" not in learn_time:
        learn_time = "0时" + learn_time
    hour = int(learn_time.split("时")[0])
    minute = int(learn_time.split("时")[1].split("分")[0])
    sec = int(learn_time.split("时")[1].split("分")[1].split("秒")[0])
    if sec > 0:
        out_minute = 60 - minute - 1
    else:
        out_minute = 60 - minute
    if minute > 0:
        out_hour = total_time - hour - 1
    elif minute == 0 and sec > 0:
        out_hour = total_time - hour - 1
    else:
        out_hour = total_time - hour
    out_sec = 60 - sec

    if out_hour < 0:
        out_hour = 0
        out_minute = 0
        out_sec = 0

    return "%d时%d分%d秒" % (out_hour, out_minute, out_sec)


# 计算预计完成时间
def cal_fin_time(local_time, res_time):
    # 分别提取本地时间和剩余时间的时分秒
    local_hour = int(local_time.split(":")[0])
    local_minute = int(local_time.split(":")[1])
    local_sec = int(local_time.split(":")[2])
    res_hour = int(res_time.split("时")[0])
    res_minute = int(res_time.split("时")[1].split("分")[0])
    res_sec = int(res_time.split("时")[1].split("分")[1].split("秒")[0])
    add_day_count = 0

    # 判断是否已经学习完成
    if res_hour == 0 and res_minute == 0 and res_sec == 0:
        return "已完成学习"
    # 如果秒数相加超过最大值
    if local_sec + res_sec >= 60:
        out_sec = local_sec + res_sec - 60
        # 如果秒数相加超过最大值且分钟数相加超过最大值
        if local_minute + res_minute >= 60:
            out_minute = local_minute + res_minute + 1 - 60
            # 如果秒数相加超过最大值、分钟数相加超过最大值且小时数相加超过最大值
            if local_hour + res_hour >= 24:
                out_hour = local_hour + res_hour + 1 - 24
                add_day_count += 1
            # 如果秒数相加超过最大值、分钟数相加超过最大值且小时数相加没有超过最大值
            else:
                out_hour = local_hour + res_hour + 1
        # 如果秒数相加超过最大值、分钟数相加没有超过最大值
        else:
            out_minute = local_minute + res_minute + 1
            # 如果秒数相加超过最大值、分钟数相加没有超过最大值且小时数相加超过最大值
            if local_hour + res_hour >= 24:
                out_hour = local_hour + res_hour - 24
                add_day_count += 1
            # 如果秒数相加超过最大值、分钟数相加没有超过最大值且小时数相加没有超过最大值
            else:
                out_hour = local_hour + res_hour
    else:
        out_sec = local_sec + res_sec
        if local_minute + res_minute > 60:
            out_minute = local_minute + res_minute - 60
            # 如果小时数相加超过最大值
            if local_hour + res_hour >= 24:
                out_hour = local_hour + res_hour + 1 - 24
                add_day_count += 1

            else:
                out_hour = local_hour + res_hour + 1
        else:
            out_minute = local_minute + res_minute
            if local_hour + res_hour >= 24:
                out_hour = local_hour + res_hour - 24
                add_day_count += 1
            else:
                out_hour = local_hour + res_hour
    while out_hour >= 24:
        out_hour = out_hour - 24
        add_day_count += 1
    if add_day_count > 0:
        return "%.2d:%.2d:%.2d(+%d)" % (out_hour, out_minute, out_sec, add_day_count)
    else:
        return "%.2d:%.2d:%.2d" % (out_hour, out_minute, out_sec)


# 进行结果反馈
def record_log():
    global record, driver
    root = tkinter.Tk()
    my_print(record)
    # 将记录写入日志文件中
    try:
        file_handle = open("log.txt", mode="r+", encoding="utf-8")
        file_handle.close()
    except:
        file_handle = open("log.txt", mode="w", encoding="utf-8")
        file_handle.close()
    log_txt = "\n【执行日期：%s】\t【执行目标：%s】\n" % (str(datetime.date.today()), str(total_time))
    record = log_txt + "┌===================================================================┐\n" + record + "\n└===================================================================┘\n"
    try:
        file_handle = open("log.txt", mode="a", encoding="utf-8")
        file_handle.write(record)
    except:
        my_print("记录写入文件错误！")
    finally:
        file_handle.close()
    learn_time = driver.find_element_by_id("xuexi_online").text
    messagebox.showinfo("提示", "学习完成，共学习【%s】，运行日志已输出在后台！" % learn_time)
    root.destroy()
    driver.quit()
    sys.exit()


# 接收用户停止学习的操作线程
def stop_click():
    # root1 = tkinter.Tk()
    # messagebox.showinfo("请谨慎点击", "点击确定脚本停止检测弹窗并记录日志到后台")
    # root1.destroy()
    is_exit = ""
    while is_exit != "y" and is_exit != "Y":
        is_exit = input()
        if is_exit == "y" or is_exit == "Y":
            global record
            record = "\t本地时间\t\t已点击\t\t已学习\t\t预计剩余\t\t预计完成时间" + record + "\n->用户手动退出！脚本停止！"
            record_log()
            sys.exit()
        else:
            my_print("输入有误，继续学习，如需停止学习请输入【y】或【Y】")


# 执行后台监控自动点击的操作线程
def auto_click():
    global driver
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    # 驱动并尝试打开网页
    try:
        # driver = webdriver.Chrome(executable_path=driverpath)
        driver = webdriver.Chrome(executable_path=driverpath, options=options)
        my_print("Google驱动器驱动成功！")
    except:
        my_print("Google驱动器驱动失败，请检查文件位置以及版本号是否正确！")
        exit()
    try:
        driver.get("http://sysaq.imu.edu.cn/index.php")
        root = tkinter.Tk()
        messagebox.showinfo("提示", "驱动成功，由于校园网的卡顿，第一次打开页面可能会出现延迟，请静候！")
        root.destroy()
    except:
        my_print("打开网页超时，请检查网址是否正确！")
        exit()

    # 自动登录、打开学习页面
    pre_log = driver.find_elements_by_class_name("button_login")[0]
    pre_log.click()
    WebDriverWait(driver, 50).until(EC.element_to_be_clickable([By.CLASS_NAME, "auth_login_btn"]))
    my_print("用户【" + user_info.split('#')[0] + "】开始执行。。。")
    user_name = driver.find_element_by_id("username")
    user_name.send_keys(user_info.split("#")[0])
    password = driver.find_element_by_id("password")
    password.send_keys(user_info.split("#")[1])
    submit = driver.find_elements_by_class_name("auth_login_btn")[0]
    submit.click()
    try:
        WebDriverWait(driver, 50).until(EC.element_to_be_clickable([By.CLASS_NAME, "one"]))
        my_print("登陆成功！")
    except:
        my_print("登录失败，请检查账号密码是否正确！")
        exit()
    win1 = driver.find_elements_by_class_name("one")[0]
    win1.click()
    WebDriverWait(driver, 50).until(EC.element_to_be_clickable([By.CLASS_NAME, "zxxxy-heading"]))
    win2 = driver.find_elements_by_class_name("zxxxy-heading")[0]
    win2.click()

    # 判断是否需要学习
    learn_time = driver.find_element_by_id("xuexi_online")
    learn_time = learn_time.text
    if "分" not in learn_time:
        learn_time = "0分" + learn_time
    if "时" not in learn_time:
        learn_time = "0时" + learn_time
    if int(learn_time.split("时")[0]) >= total_time:
        root = tkinter.Tk()
        messagebox.showinfo("提示", "当前设置学习时间小于或等于实际已学习时间，无需学习。如需继续学习，请更改设置的学习时间重新运行。")
        root.destroy()
        driver.quit()
        exit()

    # # 开始学习并循环检测系统弹窗
    root = tkinter.Tk()
    messagebox.showinfo("提示", "【%s】登录成功，开始学习。\n"
                              "1. 现在可以切换到其他页面进行您其他的工作！\n"
                              "2. 请不要最小化或关闭本网页！(否则教务系统会暂停学习，不计入时长)\n"
                              "3. 如需停止学习，请在后台输入【y】或【Y】，并敲回车。\n\n"
                              "预计共为您学习【%d】小时" % (user_info.split("#")[0], total_time))
    root.destroy()
    #
    local_time = time.strftime("%H:%M:%S", time.localtime())
    res_time = cal_res_time(learn_time)
    my_print("本地时间\t\t已点击\t\t已学习\t\t预计剩余\t\t预计完成时间\n\t%s\t【0】次\t\t%s\t%s\t%s" % (
        local_time, learn_time, res_time, cal_fin_time(local_time, res_time)))
    my_print("开始学习。。。如需停止学习请输入【y】或【Y】")
    num = 0
    global record
    record = "\n\t%s\t【0】次\t\t%s\t%s\t%s" % (local_time, learn_time, res_time, cal_fin_time(local_time, res_time))
    while True:
        # 预计5分钟后多给2秒容差
        time.sleep(60.4)
        try:
            alert = driver.switch_to.alert
            alert.accept()
            # 每点击一次次数加一
            num += 1
            learn_time = driver.find_element_by_id("xuexi_online")
            local_time = time.strftime("%H:%M:%S", time.localtime())
            res_time = cal_res_time(learn_time.text)
            my_print("本地时间\t\t已点击\t\t已学习\t\t预计剩余\t\t预计完成时间\n\t%s\t【%d】次\t\t%s\t%s\t%s\n  如需停止学习请输入【y】或【Y】" % (
                local_time, num, learn_time.text, res_time,
                cal_fin_time(local_time, res_time)))
            record += "\n\t%s\t【%d】次\t\t%s\t%s\t%s" % (
                local_time, num, learn_time.text, res_time,
                cal_fin_time(local_time, res_time))

        except Exception as e:
            # 如果出现不是没有弹窗外的其它错误，则打印到日志文件中
            if "no such alert" in str(e):
                pass
            else:
                record = record + "\n\t执行出现错误，错误原因：\n\t" + str(e)
                learn_time = driver.find_element_by_id("xuexi_online")
                record = "\t本地时间\t\t已点击\t\t已学习\t\t预计剩余\t\t预计完成时间" + record
                record_log()
        finally:
            if str(learn_time).split("时")[0] == str(total_time):
                record = "\t本地时间\t\t已点击\t\t已学习\t\t预计剩余\t\t预计完成时间" + record + "\n->已完成学习"
                learn_time = driver.find_element_by_id("xuexi_online")
                record_log()


def main():
    # 一个线程执行点击操作，另一个线程接收用户停止操作
    t_click = threading.Thread(target=auto_click, daemon=True)
    t_click.start()
    t_stop = threading.Thread(target=stop_click)
    t_stop.start()


if __name__ == '__main__':
    main()
