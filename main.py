#_*_ coding: utf-8 _*_
import kivy
import os
import sqlite3
from kivy.config import Config
Config.set("graphics","width","340")
Config.set("graphics","height","640")
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen

def connect_to_database(path):
    try:
        con = sqlite3.connect(path)
        cursor = con.cursor()
        create_table_objetos(cursor)
        con.commit()
        con.close()
    except Exception as e:
        print(e)

def create_table_objetos(cursor):
    cursor.execute(
        """
        CREATE TABLE Objetos(
        ID INT PRIMARY KEY NOT NULL,
        Nombre TEXT NOT NULL,
        Forma TEXT NOT NULL,
        Tamano VARCHAR NOT NULL,
        Color TEXT NOT NULL,
        Entorno INT NOT NULL
        )
        """
    )

class MessagePopup(Popup):
    pass

class Mainwid(ScreenManager):
    def __init__(self,**kwargs):
        super(Mainwid,self).__init__()
        self.APP_PATH = os.getcwd()
        self.DB_PATH = self.APP_PATH+"/my_database.db"
        self.StartWid = StartWid(self)
        self.DataBaseWid = DataBaseWid(self)
        self.InsertDataWid = BoxLayout()
        self.UpdateDataWid = BoxLayout()
        self.Popup = MessagePopup()
           
        wid = Screen(name='start')
        wid.add_widget(self.StartWid)
        self.add_widget(wid)
        wid = Screen(name='database')
        wid.add_widget(self.DataBaseWid)
        self.add_widget(wid)
        wid = Screen(name='insertdata')
        wid.add_widget(self.InsertDataWid)
        self.add_widget(wid)
        wid = Screen(name='updatedata')
        wid.add_widget(self.UpdateDataWid)
        self.add_widget(wid)
        self.goto_start()

    def goto_start(self):
        self.current = 'start'
    
    def goto_database(self):
        self.DataBaseWid.check_memory()
        self.current = 'database'
    
    def goto_insertdata(self):
        self.InsertDataWid.clear_widgets()
        wid = InsertDataWid(self)
        self.InsertDataWid.add_widget(wid)
        self.current = 'insertdata'

    def goto_updatedata(self, data_id):
        self.UpdateDataWid.clear_widgets()
        wid = UpdateDataWid(self, data_id)
        self.UpdateDataWid.add_widget(wid)
        self.current = 'updatedata'

class StartWid(BoxLayout):
    def __init__(self,mainwid,**kwargs):
        super(StartWid,self).__init__()
        self.mainwid = mainwid
    
    def create_database(self):
        connect_to_database(self.mainwid.DB_PATH)
        self.mainwid.goto_database()

class DataBaseWid(BoxLayout):
    def __init__(self,mainwid,**kwargs):
        super(DataBaseWid,self).__init__()
        self.mainwid = mainwid

    def check_memory(self):
        self.ids.container.clear_widgets()
        con = sqlite3.connect(self.mainwid.DB_PATH)
        cursor = con.cursor()
        cursor.execute('SELECT ID, Nombre, Forma, Tamano, Color, Entorno FROM Objetos')
        for i in cursor:
            wid = DataWid(self.mainwid)
            r1 = 'ID: '+str(100000000+i[0])[1:9]+'\n'
            r2 = 'Nombre: '+i[1]+'\n'
            r3 = 'Forma del objeto: '+i[2]+'\n'
            r4 = 'Tamaño: '+str(i[3])+'\n'
            r5 = 'Color: '+i[4]+'\n'
            r6 = 'Pertenece al entorno: '+str(i[5])
            wid.data_id = str(i[0])
            wid.data = r1+r2+r3+r4+r5+r6
            self.ids.container.add_widget(wid)
        wid = NewDataButton(self.mainwid)
        self.ids.container.add_widget(wid)
        con.close()

class InsertDataWid(BoxLayout):
    def __init__(self, mainwid, **kwargs):
        super(InsertDataWid, self).__init__()
        self.mainwid = mainwid
    
    def insert_data(self):
        con = sqlite3.connect(self.mainwid.DB_PATH)
        cursor = con.cursor()
        d1 = self.ids.id.text
        d2 = self.ids.nombre.text
        d3 = self.ids.forma.text
        d4 = self.ids.tamano.text
        d5 = self.ids.color.text
        d6 = self.ids.entorno.text
        a1 = (d1,d2,d3,d4,d5,d6)
        s1 = 'INSERT INTO Objetos(ID, Nombre, Forma, Tamano, Color, Entorno)'
        s2 = 'VALUES(%s,"%s","%s","%s","%s",%s)' % a1
        try:
            cursor.execute(s1+' '+s2)
            con.commit()
            con.close()
            self.mainwid.goto_database()
        except Exception as e:
            message = self.mainwid.Popup.ids.message
            self.mainwid.Popup.open()
            self.mainwid.Popup.title = "Error de la base"
            if '' in a1:
                message.text = 'Uno o mas campos estan vacios'
            else:
                message.text = str(e)
            con.close()

    def back_to_dbw(self):
        self.mainwid.goto_database()

class UpdateDataWid(BoxLayout):
    def __init__(self, mainwid, data_id,**kwargs):
        super(UpdateDataWid, self).__init__()
        self.mainwid = mainwid
        self.data_id = data_id
        self.check_memory()

    def check_memory(self):
        con = sqlite3.connect(self.mainwid.DB_PATH)
        cursor = con.cursor()
        string = 'SELECT Nombre, Forma, Tamano, Color, Entorno FROM Objetos WHERE ID='
        cursor.execute(string+self.data_id)
        for i in cursor:
            self.ids.nombre.text = i[0]
            self.ids.forma.text = i[1]
            self.ids.tamano.text = str(i[2])
            self.ids.color.text = i[3]
            self.ids.entorno.text = str(i[4])
        con.close()
    
    def update_data(self):
        con = sqlite3.connect(self.mainwid.DB_PATH)
        cursor = con.cursor()
        d1 = self.ids.nombre.text
        d2 = self.ids.forma.text
        d3 = self.ids.tamano.text
        d4 = self.ids.color.text
        d5 = self.ids.entorno.text
        a1 = (d1,d2,d3,d4,d5)
        s1 = 'UPDATE Objetos SET'
        s2 = 'Nombre="%s", Forma="%s", Tamano=%s, Color="%s", Entorno=%s' % a1
        s3 = 'WHERE ID=%s' % self.data_id
        try:
            cursor.execute(s1+' '+s2+' '+s3)
            con.commit()
            con.close()
            self.mainwid.goto_database()
        except Exception as e:
            message = self.mainwid.Popup.ids.message
            self.mainwid.Popup.open()
            self.mainwid.Popup.title = "Error de la base"
            if '' in a1:
                message.text = 'Uno o mas campos estan vacios'
            else:
                message.text = str(e)
            con.close()

    def delete_data(self):
        con = sqlite3.connect(self.mainwid.DB_PATH)
        cursor = con.cursor()
        string = 'DELETE FROM Objetos WHERE ID='+self.data_id
        cursor.execute(string)
        con.commit()
        con.close()
        self.mainwid.goto_database()


    def back_to_dbw(self):
        self.mainwid.goto_database()

class DataWid(BoxLayout):
    def __init__(self,mainwid,**kwargs):
        super(DataWid,self).__init__()
        self.mainwid = mainwid

    def update_data(self, data_id):
        self.mainwid.goto_updatedata(data_id)

class NewDataButton(Button):
    def __init__(self, mainwid,**kwargs):
        super(NewDataButton, self).__init__()
        self.mainwid = mainwid
    
    def create_new_objeto(self):
        self.mainwid.goto_insertdata()

class MainApp(App):
    title = 'Aplicacion VA'
    def build(self):
        return Mainwid()

if __name__ == '__main__':
    MainApp().run()