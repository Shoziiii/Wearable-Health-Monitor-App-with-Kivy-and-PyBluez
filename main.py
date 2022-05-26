from kivymd.uix.datatables import MDDataTable
from kivy.metrics import dp
from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen
from bluetooth import *
from kivy.clock import Clock
import mysql.connector
import datetime,csv


class connectivity():
    def connect(self):
        self.addr = "58:BF:25:32:E4:9E"
        self.service_matches = find_service( address = self.addr )
        self.buf_size = 1024
        self.first_match = self.service_matches[0]
        self.port = self.first_match["port"]
        self.name = self.first_match["name"]
        self.host = self.first_match["host"]
        self.port=1
        self.sock=BluetoothSocket(RFCOMM)
        self.sock.connect((self.host, self.port))
    def input_and_send(self):
        print("\nType something\n")
        while True:
            data = input()
            if len(data) == 0: break
            self.sock.send(data)
            self.sock.send("\n")
    def rx_and_echo(self):
        self.sock.send("\nsend anything\n")
        while True:
            self.data_list = []
            self.return_list = []
            bpm = ""
            spo2 = ""
            temp =""
            data = self.sock.recv(self.buf_size)
            out = data.decode()
            for i in out:
                self.data_list.append(i)
            for i in self.data_list[0:5]:
                bpm+=i
            for i in self.data_list[5:10]:
                spo2+=i
            for i in self.data_list[10:15]:
                temp+=i
            step = out[15:]
            self.return_list.append(bpm)
            self.return_list.append(spo2)
            self.return_list.append(temp)
            self.return_list.append(step)
            return self.return_list


class ProfileWindow(Screen):
    def connect(self):
        self.wearable_db = mysql.connector.connect(
        host = "localhost",
        user = "root",
        passwd = "shahroz",
        database = "Health_monitor",)
        self.connection = connectivity()
        self.connection.connect()
        print("hogia connect")
        self.steps()
    def steps(self):
        Clock.schedule_interval(self.update_label,1)
    def update_label(self,*args):
        self.raw_data = self.connection.rx_and_echo()
        if len(self.raw_data[0]) == 5 and len(self.raw_data[1]) == 5 and len(self.raw_data[2]) == 5 and len(self.raw_data[3]) != 0:
            self.bpm = self.raw_data[0]
            self.spo2 = self.raw_data[1]
            self.temp = self.raw_data[2]
            self.step = self.raw_data[3]
            if self.bpm[2] == "." and self.spo2[2] == "." and self.temp[2] == ".":
                self.ids.step_progress.progress = int(self.step)
                self.ids.step_label.text = self.step
                self.ids.temp_label.text = self.temp
                self.ids.heartrate_label.text = self.bpm
                self.ids.oxygen_label.text = self.spo2
                self.current = str(datetime.datetime.now()).split(" ")
                self.wearable_cursor = self.wearable_db.cursor()
                self.data = "INSERT INTO health_data(date_, time_, bpm, spo2, temperature, steps) VALUES (%s,%s,%s,%s,%s,%s)"
                self.record = self.current[0],self.current[1][0:8],self.bpm,self.spo2,self.temp,self.step
                self.wearable_cursor.execute(self.data,self.record)
                self.wearable_db.commit()
class BluetoothWindow(Screen):
    pass
class StepsWindow(Screen):
    pass
class HeartWindow(Screen):
    pass			
class OxygenWindow(Screen):
    pass
class TemperatureWindow(Screen):
    pass
class WeightWindow(Screen):
    pass
class DataWindow(Screen):
    pass
class WindowManager(ScreenManager):
    pass



class MainApp(MDApp):
    def build(self):
        self.title='KivyMD Dashboard'
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Orange"
        # return Builder.load_file("main.kv")
    def add_datatable(self):
        self.wearable_db = mysql.connector.connect(
        host = "localhost",
        user = "root",
        passwd = "shahroz",
        database = "Health_monitor",)
        self.sql_select_Query = "select * from health_data"
        self.cursor = self.wearable_db.cursor()
        self.cursor.execute(self.sql_select_Query)
        self.records = self.cursor.fetchall()
        self.data_tables = MDDataTable(
            use_pagination=True,
            size_hint=(0.9, 0.75),
            pos_hint =  {"center_x": 0.5, "center_y": 0.45},
            column_data=[
                ("Date", dp(30)),
                ("Time", dp(30)),
                ("BPM", dp(15)),
                ("SpO2", dp(15)),
                ("Temperature", dp(25)),
                ("Steps", dp(20)),
            ],
            row_data= self.records,
            elevation = 2,
        )
        self.root.ids.data_scr.ids.data_layout.add_widget(self.data_tables)
    def print_csv(self):
        self.wearable_db = mysql.connector.connect(
        host = "localhost",
        user = "root",
        passwd = "shahroz",
        database = "Health_monitor",)
        self.sql_select_Query = "select * from health_data"
        self.cursor = self.wearable_db.cursor()
        self.cursor.execute(self.sql_select_Query)
        self.records = self.cursor.fetchall()
        fp = open('database.csv', 'w')
        myFile = csv.writer(fp)
        myFile.writerows(self.records)
        fp.close()
        print("Hogia")
MainApp().run()

