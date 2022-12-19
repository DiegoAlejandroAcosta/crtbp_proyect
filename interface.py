from kivy import Config
Config.set('graphics', 'width', '1200')
Config.set('graphics', 'height', '600')
Config.set('graphics', 'minimum_width', '800')
Config.set('graphics', 'minimum_height', '650')
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
from kivymd.app import MDApp
from kivy.lang import Builder 
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.datatables import MDDataTable
from kivy.metrics import dp
from kivy.graphics import Color, Line
from kivymd.uix.dialog import MDDialog
from kivy.clock import mainthread,Clock

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sql_queries import *
from solver import *

import time
import threading 


class interface(MDApp):
    
    changed = [0,0]
    selected = [0,0,0]
    def principal_bodies(self):
        mb = main_bodies(conn).sort_values(by = ['ID body']) 
        self.principal = list(mb['Secondary'])
        self.mb = mb
        values = list(mb['Secondary'])
        self.root.ids.Principal.values = values
        self.root.ids.Secondary.text = 'Select Option'
        self.root.ids.Secondary.disabled = False
        self.root.ids.syscons.text = ''
        if self.selected[0]:
            self.root.ids.Principal.canvas.children.pop(len(self.root.ids.Principal.canvas.children)-1)
            self.selected[0] = 0
        
    def second_bodies(self):
        
        body = self.root.ids.Principal.text
        self.id = self.mb.iloc[list(self.principal).index(body)].name
        self.satelite = system(conn,self.id)
        self.root.ids.Secondary.values = list(self.satelite['Secondary'])
        if self.selected[1]:
            self.root.ids.Secondary.canvas.children.pop(len(self.root.ids.Secondary.canvas.children)-1)
            self.selected[1] = 0
    
    def family(self):
        self.families = families(conn)
        self.root.ids.family.values = self.families['family']
        if self.selected[2]:
            self.root.ids.family.canvas.children.pop(len(self.root.ids.family.canvas.children)-1)
            self.selected[2] = 0
        
    def load_orbits(self):
        body = self.root.ids.Secondary.text
        id = list(self.satelite['ID body'])[list(self.satelite['Secondary']).index(body)]
        family_id = list(self.families['id family'])[list(self.families['family']).index(self.root.ids.family.text)]
        orbits_filtered = orbits(conn,id,family_id)
        columns = list(zip(orbits_filtered.columns,[dp(40)]*len(orbits_filtered.columns)))
        rows = np.array(orbits_filtered)
        table = MDDataTable(
            check = True,
            use_pagination = True,
            rows_num = 15,
            pos_hint = {'x':0,'y':0},
            size_hint = (0.99,0.6),
            column_data = columns,
            row_data = rows)
        self.root.add_widget(table)
        
    def setsystem(self, value):
        first = self.root.ids.Principal.text 
        system = first+'-'+value
        self.root.ids.syscons.text = system
        
    def setfamily(self, value):
        self.root.ids.familycons.text = value

    def checkboxs(self, id):
        check_id = ''
        if 'range' in id:
            check_id = id.replace('range','all')
        else:
            check_id = id.replace('all','range')
        if not self.root.ids[id].active:
            self.root.ids[id].active = True
        
    def disablerange(self,id):
        if 'all' in id:
            Min = id.replace('all','min')
            Max = id.replace('all','max')
            MIN = self.root.ids[Min]
            MAX =self.root.ids[Max]
            MIN.text = ''
            MAX.text = ''
            MIN.disabled = True
            MAX.disabled = True
            if self.changed[0]:
                MIN.canvas.children.pop(len(MIN.canvas.children)-1)
            if self.changed[1]:
                MAX.canvas.children.pop(len(MAX.canvas.children)-1)
            self.changed = 0,0
        else:
            Min = id.replace('range','min')
            Max = id.replace('range','max')
            self.root.ids[Min].disabled = False
            self.root.ids[Max].disabled = False

    def thread_function(self):
        threading.Thread(target = self.validate).start()

    def load_df(self,args):
        principalDropdown = self.root.ids.Principal
        secondaryDropdown = self.root.ids.Secondary
        familyDropDown = self.root.ids.family
        if len(self.root.ids.table_pos.children) == 1:
            self.root.ids.table_pos.children.pop(len(self.root.ids.table_pos.children)-1)
        id_search =self.satelite.loc[list(self.satelite['Secondary']).index(secondaryDropdown.text)]['ID body']
        family_id = self.families.loc[list(self.families['family']).index(familyDropDown.text)]['id family']
        self.mu = self.satelite.loc[list(self.satelite['Secondary']).index(secondaryDropdown.text)]['mu']
        self.df =orbits(conn,id_search,family_id,args = args)
        df = self.df
        if len(df) == 0:
            self.dialog = MDDialog(text = 'Orbits '+principalDropdown.text+"-"+secondaryDropdown.text+' type '+familyDropDown.text+' '+
                                            'Orbits not found')
        else: 
            self.columns = df.columns
            columns = list(zip(df.columns,[dp(40)]*len(df.columns)))
            table = MDDataTable(
                    use_pagination = True,
                    check = True,
                    column_data = columns,
                    row_data = df.to_numpy(),
                    on_row_press = self.on_row_press
                )
            self.root.ids.orbits_screen.disabled = False
            self.root.ids.table_pos.add_widget(table)
            self.root.ids.loading.active = False

    def load_orbits(self,args):
        principalDropdown = self.root.ids.Principal
        secondaryDropdown = self.root.ids.Secondary
        familyDropDown = self.root.ids.family
        if len(self.root.ids.table_pos.children) == 1:
                self.root.ids.table_pos.children.pop(len(self.root.ids.table_pos.children)-1)
        id_search =self.satelite.loc[list(self.satelite['Secondary']).index(secondaryDropdown.text)]['ID body']
        family_id = self.families.loc[list(self.families['family']).index(familyDropDown.text)]['id family']
        self.mu = self.satelite.loc[list(self.satelite['Secondary']).index(secondaryDropdown.text)]['mu']
        self.df =orbits(conn,id_search,family_id,args = args)
        df = self.df
        print(len(df))
        if len(df) == 0:
            self.dialog = MDDialog(text = 'Orbits '+principalDropdown.text+"-"+secondaryDropdown.text+' type '+familyDropDown.text+' '+
                                            'Orbits not found')

        else: 
            self.root.ids.orbits_screen.disabled = False
            self.update_canvas(self.root.ids.table_pos,'','table')
            self.root.ids.loading.active = False
        
    @mainthread
    def update_canvas(self,widget,function,change):
        if change == 'table':
            df = self.df
            self.columns = df.columns
            columns = list(zip(df.columns,[dp(40)]*len(df.columns)))
            table = MDDataTable(
                    use_pagination = True,
                    check = True,
                    column_data = columns,
                    row_data = df.to_numpy(),
                    on_row_press = self.on_row_press
                )
            widget.add_widget(table)
            
        if change == 'line':
            new_widget = Line(width =  2, rectangle= (widget.x, widget.y, widget.width, widget.height))
        else:
            new_widget = Color(1,0,0,1)
        if function == 'add':
            widget.canvas.add(new_widget)
        else:
            widget.canvas.remove(new_widget)

    def validate(self, *arggs):
        total = 0
        args = []
        jacobi = self.root.ids.rangeperiod.active
        period = self.root.ids.rangejac.active
        stab = self.root.ids.rangestb.active
        jaccons,periodcons,stbcons =  self.root.ids.jaccons,self.root.ids.periodcons,self.root.ids.stbcons
        Errorlabel = self.root.ids.errorlabel
        if (jacobi) or (period) or (stab):
            minperiod, maxperiod = self.root.ids.minperiod, self.root.ids.maxperiod
            minjac, maxjac = self.root.ids.minjac, self.root.ids.maxjac
            minstb, maxstb = self.root.ids.minstb, self.root.ids.maxstb
            pairs = [[minjac,maxjac,jaccons],[minperiod,maxperiod,periodcons],[minstb,maxstb,stbcons]]
            for MIN, MAX,cons in pairs:
                
                
                if MIN.disabled:
                    
                    total +=1
                    cons.text = 'Any'
                    args.append([])
                    continue
                if (MIN.text== '' or MAX.text == ''):
                    
                    self.update_canvas(MIN,'all','color')
                    self.update_canvas(MIN,'all','line')
                    
                    self.update_canvas(MAX,'all','color')
                    self.update_canvas(MAX,'all','line')
                    
                    self.changed = 1,1
                    Errorlabel.text = 'ERROR: INVALID RANGE'
                    self.root.ids.loading.active = False
                    continue    
                if float(MIN.text) >= float(MAX.text):
                    Errorlabel.text = 'ERROR: INVALID RANGE'
                    
                    self.update_canvas(MAX,'add','color')
                    self.update_canvas(MAX,'add','line')
                    
                    self.changed = 0,1
                    self.root.ids.loading.active = False
                else:

                    cons.text=MIN.text+'-'+MAX.text
                    args.append([MIN.text,MAX.text])
                    total +=1
        else:
            jaccons.text='Any'
            periodcons.text='Any'
            stbcons.text='Any'
            total = 3
            args = [[],[],[]]
            Errorlabel.text = ''
        principalDropdown = self.root.ids.Principal
        secondaryDropdown = self.root.ids.Secondary
        familyDropDown = self.root.ids.family
        drops = [['Principal body', principalDropdown],
                 ['Secondary body',secondaryDropdown],
                 ['Family',familyDropDown]]
        
        k = 0
        for string, drop in drops:
            if drop.text == 'Select Option':
                Errorlabel.text = 'ERROR: SELECT OPTION'
                self.update_canvas(drop,'add','color')
                self.update_canvas(drop,'add','line')
                self.selected[k] = 1
                k +=1
                self.root.ids.loading.active = False
            else:
                total += 1
        if total == 6:
            self.root.ids.loading.active = True
            self.load_orbits(args)
            self.root.ids.loading.active = False

    def on_row_press(self,instance_table, instance_row):
        print(instance_row.text)
    
    def get_rows_data(self):
        self.selected_df = pd.DataFrame(self.root.ids.table_pos.children[0].get_row_checks(),
                                   columns = self.columns)
        
    def download(self):
        self.get_rows_data()
        self.selected_df.to_csv('ics.csv')
    
    def plotting(self,family = False,family_df = ''):
        self.get_rows_data()
        df = self.df
        mu = self.mu
        plot_df= self.selected_df if not family else family_df
        for ind in plot_df.index:
            Y, IS = database_orbit(df.loc[ind],mu)
            Y0 = IS["Y0"]
            P = IS["P"]
            plt.plot(Y[:,0],Y[:,1],"k",alpha = 0.5)
            plt.plot(1-mu,0,"ro",markersize = 2)
            plt.axis('equal')
        plt.show()
    
    def preview_family(self):
        df = self.df
        rows = np.zeros(10)
        row_df = []
        for i in range(1,11):
            row_df.append(df.iloc[int((len(df)//10)*i)-1])
        
        family_df = pd.DataFrame(row_df, columns = self.columns)
        self.plotting(family = True,family_df = family_df)
        
    def build(self):
        self.theme_cls.primary_palette = "Blue"
        return Builder.load_file("interface.kv")
    
       

if __name__ == '__main__':
    interface().run()



