from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.checkbox import CheckBox
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.graphics import Color, Line
from kivy.properties import ObjectProperty
from kivy.lang import Builder
import pandas as pd
import math

R=8.314

#Values for t<1600
tl=pd.read_excel('AFT TABLE.xlsx',"Tl")
#Values for t<6000
th=pd.read_excel('AFT TABLE.xlsx',"Th")

AH=th.loc[:,'AH'].tolist()
BH=th.loc[:,'BH'].tolist()
CH=th.loc[:,'CH'].tolist()
DH=th.loc[:,'DH'].tolist()
AL=tl.loc[:,'AL'].tolist()
BL=tl.loc[:,'BL'].tolist()
CL=tl.loc[:,'CL'].tolist()
DL=tl.loc[:,'DL'].tolist()


class MyGr(BoxLayout):
    global conditions
    conditions = {}
    def checkbox(self, instance, value, a, b):
        if value == True:
            conditions[b] = a
    fue = ObjectProperty(None) 
    com = ObjectProperty(None)
    t = ObjectProperty(None)
    te = ObjectProperty(None)
    y_ = ObjectProperty(None)
    resul = ObjectProperty(None)

    def inp(self):
        print(conditions)
        global fuel,cond,fuel_type,H2O_type,Tg,comp,temp,Y,res
        res=""
        fuel = self.fue.text
        Tg = int(self.t.text)
        cond=conditions['con']
        fuel_type=conditions['fuel_typ']+ " Fuel"
        H2O_type=conditions['h2o_typ']
        comp=list(map(int, (self.com.text).rstrip().split()))
        Y=int(self.y_.text)
        temp=self.te.text
        
        global N
        Ycc=comp[0] + (0.25*comp[1]) - (0.5*comp[2])
        Ymin=Ycc-0.5*comp[0]
        if Y==0:
            Y=Ycc
        if Ycc<=Y:
            N=[0,comp[0],0.5*comp[1],3.76*Y,Y-Ycc]
        elif Ymin<=Y:
            N=[2*(Ycc-Y),2*(Y-Ymin),0.5*comp[1],3.76*Y,0]
        
        input_=("Fuel :"+fuel+'\n'+"COndition : Constant"+cond+'\n'+"Fuel type :"+fuel_type+'\n'+"H2O type :"+H2O_type+'\n'+"Initial Temperature :"+str(Tg)+'\n'+"Composition of Fuel :"+str(comp)+'\n'+"Moles of O2 :"+str(Y))
        popup = Popup(title='', content=Label(text=input_), size_hint=(None, None), size=(800, 400))
        popup.open()
        

        def step_1():
            global Q_val
            table=pd.read_excel(cond+".xlsx",H2O_type)
            rp_val=table[table['Fuel']==fuel].iloc[0][fuel_type]
            Q_val=-rp_val-(N[0]*281600)

        def step_2(temp):
            l=math.log(temp)
            if cond=='Volume':
                if 1600<temp<6000:
                    Up=0
                    for i in range(5):
                        Up+=N[i]*(AH[i] + (BH[i]-R)*temp - (CH[i]*l))
                elif 1600>temp:
                    Up=0
                    for i in range(5):
                        Up+=N[i]*(AL[i] + (BL[i]-R)*temp - (CL[i]*l))
                return Up
            elif cond=='Pressure':
                if 1600<temp<6000:
                    Hp=0
                    for i in range(5):
                        Hp+=N[i]*(AH[i] + (BH[i])*temp - (CL[i]*l))
                elif 1600>temp:
                    Hp=0
                    for i in range(5):
                        Hp+=N[i]*(AL[i] + (BL[i])*temp - (CL[i]*l))
                return Hp

        def step_3(temp):
            if cond=='Volume':
                if 1600<temp<6000:
                    Cv=0
                    for i in range(5):
                        Cv+=N[i]*((BH[i]-R) - (CH[i]/temp))
                elif 1600>temp:
                    Cv=0
                    for i in range(5):
                        Cv+=N[i]*((BL[i]-R) - (CL[i]/temp))
                return Cv
            elif cond=='Volume':
                if 1600<temp<6000:
                    Cp=0
                    for i in range(5):
                        Cp+=N[i]*((BH[i]) - (CH[i]/temp))
                elif 1600>temp:
                    Cp=0
                    for i in range(5):
                        Cp+=N[i]*((BL[i]) - (CL[i]/temp))
                return Cp

        while True:
            global UpTr
            res+=('\n'+f"Fuel:{fuel}"+'\n'+f"Condition:Constant {cond}"+'\n'+f"Initial temperature:{Tg}"+'\n'+f"Atoms of Oxygen:{Y}"+'\n'+f"Fuel Composition:{comp}"+'\n')
            UpTr=step_2(Tg)
            break

        i=1

        while True:
            global T_new
            res+='\n'+('\n'+"--------------------"+'\n')
            res+='\n'+(f'{i} cycle')
            res+='\n'+('\n'+"--------------------"+'\n')
            temp=float(temp)
            res+='\n'+f"The assumed temperature for this cycle is {temp}"+'\n'
            step_1()
            UpT=step_2(temp)
            res+='\n'+(f"Up[{temp}={UpT}]")
            res+='\n'+(f"Up[{Tg}={UpTr}]")
            CvT=step_3(temp)
            res+='\n'+(f"Cv[{temp}={CvT}]")
            T_new=temp- ((UpT - UpTr - Q_val)/CvT)
            res+='\n'+(f"Tnew = {T_new} and Taaumed = {temp}")
            diff=T_new-temp
            i=i+1
            if abs(diff)>5:
                res+='\n'+(f"The difference in the assumed and new temperature is {diff}, which is more than 5k for the assumed temperature of{temp}. Hence another loop is done.")
                temp=T_new
            else:
                res+='\n'+('\n'+"--------------------"+'\n')
                res+='\n'+(f"The Adiabatic Flame Temperature is {T_new}")
                res+='\n'+('\n'+"--------------------"+'\n')
                break
            
    def cal(self):
        self.resul.text = res
        popup = Popup(title='', content=Label(text=f"The Adiabatic Flame Temperature is {T_new} K"), size_hint=(None, None), size=(600, 400))
        popup.open()
    
    def clear(self):
        self.fue.text = ""
        self.t.text = ""
        self.com.text = ""
        self.y_.text = ""
        self.te.text = ""
        self.resul.text = ""
        self.ids.radio_button1.active = False
        self.ids.radio_button2.active = False
        self.ids.radio_button3.active = False
        self.ids.radio_button4.active = False
        self.ids.radio_button5.active = False
        self.ids.radio_button6.active = False
    
class Exe(App):

    
    def build(self):
        self.title="AFT Calculator"
        Builder.load_string('''
<CTextInput@TextInput>:
    background_color: 0, 0, 0, 1  # Black background
    foreground_color: 1, 1, 1, 1  # White font color
    canvas.before:
        Color:
            rgba: 1, 1, 1, 1  # White outline color
        Line:
            rectangle: self.x, self.y, self.width, self.height

<MyGr>

    fue : fuel
    com : comp
    t : tg
    te : tem
    resul : result
    y_:y


    GridLayout:
        cols:1
        size: root.width,root.height
        pos:0,0
        GridLayout:
            cols:2

            Label:
                text : "Fuel :"
            CTextInput:
                id: fuel
                multiline:"False"
                
            Label:
                text : "Condition of the system :"
            GridLayout:
                cols:4
                canvas.before:
                    Color:
                        rgba: 1, 1, 1, 1  # White outline color
                    Line:
                        rectangle: self.x, self.y, self.width, self.height

                Label:   
                    text : "Volume"
                CheckBox:
                    id:radio_button1
                    group:"cond"
                    on_active: root.checkbox(self,self.active,"Volume","con")
                Label:   
                    text : "Pressure"
                CheckBox:
                    id:radio_button2
                    group:"cond"
                    on_active: root.checkbox(self,self.active,"Pressure","con")
            
            Label:
                text : "Type of fuel :"
            GridLayout:
                cols:4
                canvas.before:
                    Color:
                        rgba: 1, 1, 1, 1  # White outline color
                    Line:
                        rectangle: self.x, self.y, self.width, self.height

                Label:   
                    text : "Liquid"
                CheckBox:
                    id:radio_button3
                    group:"fuel_typ"
                    on_active: root.checkbox(self,self.active,"Liquid","fuel_typ")
                Label:   
                    text : "Gaseous"
                CheckBox:
                    id:radio_button4
                    group:"fuel_typ"
                    on_active: root.checkbox(self,self.active,"Gaseous","fuel_typ")

            
            Label:
                text : "Type of H2O :"
            GridLayout:
                cols:4
                canvas.before:
                    Color:
                        rgba: 1, 1, 1, 1  # White outline color
                    Line:
                        rectangle: self.x, self.y, self.width, self.height

                Label:   
                    text : "Liquid"
                CheckBox:
                    id:radio_button5
                    group:"h2o_typ"
                    on_active: root.checkbox(self,self.active,"Liq","h2o_typ")
                Label:   
                    text : "Gaseous"
                CheckBox:
                    id:radio_button6
                    group:"h2o_typ"
                    on_active: root.checkbox(self,self.active,"Gas","h2o_typ")


            Label:
                text : "Enter the initial temperature :"
            CTextInput:
                id: tg
                multiline:"False"
            
            Label:
                text : "Compostion of fuel (C,H,O) in the mixture:"
            CTextInput:
                id: comp
                multiline:"False"
            
            Label:
                text : "Enter if the mixture is chemically correct as '0' else enter the amount of oxygen :"
                font_size:14
            CTextInput:
                id: y
                multiline:"False"

            Label:
                text : "Assumed temperature :"
            CTextInput:
                id: tem
                multiline:"False"

        GridLayout:
            cols:2
            GridLayout:
                rows:4
                Button:
                    text:"Get Input data"
                    font_size:30
                    on_press:root.inp()            
                Button:
                    text:"Calculate AFT"
                    font_size:30
                    on_press:root.cal() 
                Button:
                    text:"Clear"
                    font_size:30
                    on_press:root.clear() 
                Button:
                    text:"Quit"
                    font_size:30
                    on_press:app.quit() 



            CTextInput:
                id:result
            ''')        

        return MyGr()

    def quit(self):
        App.get_running_app().stop()

Exe().run()
