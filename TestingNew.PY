try:
    import Tkinter as tk
    from tkFileDialog import askopenfilename
    import cgi
    print('Using Python 2')
except:
    import tkinter as tk
    from tkinter.filedialog import askopenfilename
    import html as cgi
    print('Using Python 3')

import math
import numpy
import random

import os
import re

import UI_Settings

from UI_Settings import *

### Main
class UI_Master_Class(tk.Tk):
    '''Master UI: Contains all TDX_Editor UI elements (except some Tab-specific UI classes)'''
    def __init__(self, FileDirectory = r'C:\Users\GEX\Desktop\testing'):
        tk.Tk.__init__(self)
        self.InitialDirectory = FileDirectory

        self.Create_Center()

        self.Open_TDX_File()

        print('WAIT: start self.mainloop()')
        self.mainloop()
        print('EXIT: end self.mainloop()\n')
        ###
        ###


    ### Center window
    def Create_Center(self):
        '''The UI Center contains all other UI elements. It contains two windows Window_Buttons, which is static and Window_Tab, which changes depending on the active Tab'''

        self.UI_Settings = UI_Settings()
        self.title("TDX Editor")
        # Tab Order determined by order of the tuples (Lookup name, Displayed name) from Tab_Names_Combined. 
        # Do not change "Lookup name" ("tab_XXX" in self.Tab_lookups), unless it is changed throughout the file.
        # See Create_Tabs() or Update_TDX_File() for implementation of the ordering.
        Tab_Names_Combined = [('tab_INTRO','Intro'), ('tab_RENAME','Rename'), ('tab_DATA','Data Gen'), ('tab_TABLE','Add Table'), ('tab_FB','Multi-Part FB'), ('tab_SP','Clean/SP Gen')]
        self.Tab_lookups, self.Tab_Names = zip(*Tab_Names_Combined)

        # Initialize values
        self.ACTIVE_TAB_ROW = 12    # Constant
        self.ACTIVE_TAB_COL = 0     # Constant
        self.ActivePageN = 0
        self.ActiveTabN  = 0
        self.RecentEdits = False

        # Creates two main windows
        self.Window_Buttons = tk.Frame(self, bg=self.UI_Settings.ColorBGdkGrey)  # bg color is between tab buttons
        self.Window_Tab     = tk.Frame(self, bg=self.UI_Settings.ColorBack1)

        self.Window_Buttons.grid(row=0, column=0, sticky=tk.NSEW)
        self.Window_Tab.grid(    row=1, column=0, sticky=tk.NSEW)

        # Expands self.Window_Tab
        self.columnconfigure(0, weight=1)
        self.rowconfigure(   1, weight=1)


        # Setup Tab_Buttons inside Window_Buttons
        Max_Tab_Name_Spacing = max([len(X) for X in self.Tab_Names]) + 4
        self.Tab_Buttons = [tk.Button(self.Window_Buttons, 
            bd=4, 
            text='{NM: ^{L}}'.format(NM=NAME, L=Max_Tab_Name_Spacing), 
            bg=self.UI_Settings.ColorBGltGrey) \
            for index, NAME in enumerate(self.Tab_Names)]

        [B.grid(row=0, column=index, sticky=tk.EW+tk.S, padx=3, pady=5, ipady=1) for index, B in enumerate(self.Tab_Buttons)]

        # Setup additional Window_Buttons buttons (save, load, exit)
        self.Button_Load = tk.Button(self.Window_Buttons, 
            text="Load File", 
            bg=self.UI_Settings.ColorLoad, 
            fg     = 'white',
            command=self.Open_TDX_File, 
            bd=5, relief="ridge")
        self.Button_Save = tk.Button(self.Window_Buttons, 
            text="Save File", 
            bg=self.UI_Settings.ColorSave, 
            fg     = 'white',
            command=self.Save_Process, 
            bd=5, relief="ridge",
            state=tk.DISABLED)
        self.Button_Quit = tk.Button(self.Window_Buttons, 
            text="Exit", 
            bg=self.UI_Settings.ColorExit, 
            fg     = 'white',
            command=self.QUIT, 
            bd=5, relief="ridge")

        Spacing = 3
        self.Button_Quit.grid(row=0, column=101, padx=Spacing*2, pady=Spacing, sticky=tk.NSEW, ipadx=15)
        self.Button_Load.grid(row=0, column=102, padx=Spacing*1, pady=Spacing, sticky=tk.NSEW, ipadx=5, ipady=3)
        self.Button_Save.grid(row=0, column=103, padx=Spacing*1, pady=Spacing, sticky=tk.NSEW, ipadx=5)

        # Horizontally expand Window_Buttons (includes: additional and Tab_Buttons)
        [self.Window_Buttons.columnconfigure(COLUMN, weight=1) for COLUMN in range(len(self.Tab_Names)+2)]

        # Expands Window_Tab (includes: active Tab)
        self.Window_Tab.columnconfigure(self.ACTIVE_TAB_COL, weight=1)
        self.Window_Tab.rowconfigure(   self.ACTIVE_TAB_ROW, weight=11)

        self.Size_Window()



    def Size_Window(self):
        '''Sets minimum size, current size, and forces active window'''
        self.minsize(800, 700)
 
        w, h = max(10,self.winfo_screenwidth()-100), max(10,self.winfo_screenheight()-200)
        self.geometry("%dx%d+30+30" % (w, h))

        self.lift()
        self.focus_force()

    ### Tabs
    def Create_Tabs(self):
        '''Activates each Tab Creation method, self.Create_Tab_xxx'''
        # Creates self.Show_CMD_closure() command and tk.Frame for each Tab
        self.Tabs_List = [tk.Frame(self.Window_Tab, bg=self.UI_Settings.ColorBGdkGrey) for NAME in self.Tab_Names]
        self.ActiveTabCMD = [self.Show_CMD_closure('Tab', index, self.Tabs_List, self.Tab_Buttons) for index in range(len(self.Tab_Names))]

        [TAB.grid(
            row=self.ACTIVE_TAB_ROW, 
            column=self.ACTIVE_TAB_COL, 
            padx=0, pady=0, 
            sticky=tk.NSEW) for index, TAB in enumerate(self.Tabs_List)]

        [TAB.columnconfigure(self.ACTIVE_TAB_COL, weight=1) for TAB in self.Tabs_List]
        [TAB.rowconfigure(   self.ACTIVE_TAB_ROW, weight=1) for TAB in self.Tabs_List]

        # Implementation of the ordering for Tabs
        self.Create_Tab_Splash(   self.Tab_lookups.index('tab_INTRO'))
        self.Create_Tab_Renamer(  self.Tab_lookups.index('tab_RENAME'))
        self.Create_Tab_Table(    self.Tab_lookups.index('tab_TABLE'))
        self.Create_Tab_Generator(self.Tab_lookups.index('tab_DATA'))
        self.Create_Tab_SPgen(    self.Tab_lookups.index('tab_SP'))
        self.Create_Tab_MPart(    self.Tab_lookups.index('tab_FB'))
        # Sets active tab to N=[self.ActiveTabN] (N=0, 'tab_INTRO' for first run)
        self.ActiveTabCMD[self.ActiveTabN]()
        # Sets self.Button_Save to inactive (until Commit)
        [XXX.configure(state=tk.NORMAL) for XXX in self.Tab_Buttons]
        self.RecentlyUpdated(False)

    def Create_Tab_Splash(self, N):
        ''' The Splash Tab contains introduction data, a sample button legend, and TDX step/interaction data'''
        #self.Window_Tab.bind_all("<MouseWheel>", self._on_mousewheel)  # Enables mousewheel scrolling in tab_INTRO

        self.Splash_Tab = tk.Frame(self.Tabs_List[N], bg=self.UI_Settings.ColorBack1) #VerticalScrolled
        self.Splash_Tab.grid(row=self.ACTIVE_TAB_ROW, column=self.ACTIVE_TAB_COL, padx=0, pady=0, sticky=tk.NSEW)

        self.Splash_Button_Region = tk.LabelFrame(self.Tabs_List[N], text='Select type of Intro information', bg=self.UI_Settings.ColorBGltGrey)
        self.Splash_Button_Region.grid(row=0, column=0, padx=0, pady=0, sticky=tk.NSEW)

        self.Splash_Page_Names = ['Program', 'File', 'None']
        self.Splash_Pages = [tk.LabelFrame(self.Splash_Tab, bg=self.UI_Settings.ColorBack1, text=NAME) for NAME in self.Splash_Page_Names]
        [XXX.grid(row=0, column=0, sticky=tk.NSEW) for XXX in self.Splash_Pages]

        self.Splash_Tab.columnconfigure(0, weight=1)
        self.Splash_Tab.rowconfigure(   0, weight=1)

        Max_Splash_Name_Spacing = max([len(X) for X in self.Splash_Page_Names]) + 4
        self.Splash_Buttons = [tk.Button(self.Splash_Button_Region, bd=4, text='{NM: ^{L}}'.format(NM=NAME, L=Max_Splash_Name_Spacing), bg=self.UI_Settings.ColorBGltGrey) for index, NAME in enumerate(self.Splash_Page_Names)]
        [BUTTON.grid(row=0, column=index, padx=2, pady=2) for index, BUTTON in enumerate(self.Splash_Buttons)]

        self.ActiveSplashCMD = [self.Show_CMD_closure('Splash', index, self.Splash_Pages, self.Splash_Buttons) for index in range(len(self.Splash_Page_Names))]
        self.ActiveSplashCMD[0]()

        self.Splash_Program = self.Splash_Pages[self.Splash_Page_Names.index('Program')]
        self.Splash_File    = self.Splash_Pages[self.Splash_Page_Names.index('File')]
        self.Splash_None    = self.Splash_Pages[self.Splash_Page_Names.index('None')]

        # Introduction Data
        chars = ['_','*']
        Input_Data = [
            (self.Splash_Program, ['***Basic Program Information'],0,'light blue'),
            (self.Splash_Program, ['*Only the "Save" button will edit the actual TDX file.'.format(chars[0]*3), '*Each "Commit" button updates information from the active tab to all others.', '*Non-Committed data will not be saved. Commit before saving or before editing another tab.', '*A Commit will clear most inputs (not Table/dataGen). A Load/Save will clear all inputs'],1,'lemon chiffon'),
            (self.Splash_Program, ['{}Tab Descriptions'.format(chars[1]*3)],0,'light blue'),
            (self.Splash_Program, ['Rename: Rename any item (var, array,...). \n\t*Makes edits manually, with regex, or using a common root (plus an index number)', 'Add Table: Add a table or a data table, or arrays. \n\t*Set the row separator (tab, comma, space), transpose the data, or view a test table.', 'Data Generator: Creates TDX variables from a list of values. \n\t*Set name stem, type, format, and an equation for min/max from value. \n\t*Shift data using equation, min/max, mean/standard deviation.\n\t*Generate data from an equation, a sample, or a distribution function.','Clean/SP generator: Combination of common SP preparations\n\t*Deletes feedbacks\n\t*Pauses all steps, except first and last\n\t*Removes unused interactions\n\t*Removes import from steps', 'Multi-Part Feedback: Automatically generates feedbacks (Your first answer is correct, but...) for 2 to 8 parts\n\t*Set part names (1st, 2nd,...) and general or part specific feedbacks\n\t*Displays interaction names in selected step and has copy buttons for "Interaction Names" and paste buttons for "Input Names"'],1,'lemon chiffon'), 
            (self.Splash_Program, ['{}Button Legend (Sample button colors)'.format(chars[1]*3)],0,'light blue'),
            ]

        # TDX step/interaction data
        Input_Data += [(self.Splash_File, ['{}Unused interactions: List'.format(chars[1]*3)], 0,'light green'),]
        if len(self.DISINTEGRATE.RemovableInteractions)==0:
            Inter_Unused = [(self.Splash_File, ('__None__',), 1,'white'),]
        else:
            REMOVABLE = self.DISINTEGRATE.RemovableInteractions
            Inter_Unused = [(self.Splash_File, [', '.join(REMOVABLE),], 1,'white')]
        Input_Data += Inter_Unused

        Input_Data +=[(self.Splash_File, ['{}Used interactions: By step'.format(chars[1]*3)],0,'light green')]
        if len(self.DISINTEGRATE.D_Step_to_Inter.items())==0:
            Inter_used = [(self.Splash_File, ('__None__',), 1,'white'),]
        else:
            USED = self.DISINTEGRATE.D_Step_to_Inter.items()
            Inter_used = [(self.Splash_File, ['{}: '.format(A)+', '.join(B),], 1,'white') for A,B in USED]
        Input_Data += Inter_used



        indent_len = 40
        for index, (LOC, DATA, INDENT_VAL, COLOR) in enumerate(Input_Data):
            A = tk.Label(LOC, bg=COLOR) #, justify=tk.LEFT)
            A.grid(row=index, column=0, padx=10+indent_len*INDENT_VAL, pady=(2*(1-index%2)), sticky=tk.NSEW)
            A.rowconfigure(0, weight=1)
            A.columnconfigure(0, weight=1)
            for ROW, DATUM in enumerate(DATA):
                B = tk.Label(A, 
                        text=DATUM, 
                        bg=COLOR, 
                        anchor=tk.W, 
                        justify=tk.LEFT)
                B.grid(row=ROW+1, 
                        column=0, 
                        padx=5, 
                        pady=0, 
                        sticky=tk.NSEW)

        # sample button legend
        Button_Info = [ 
                        ('Tab (in-Active)',            'black', self.UI_Settings.ColorPassive, 4, "raised", (0,0)),
                        ('Tab (Active)',               'black', self.UI_Settings.ColorActive,  4, "raised", (0,1)),

                        ('Exit',                       'white', self.UI_Settings.ColorExit,    5, "ridge",  (1,0)),
                        ('Load',                       'white', self.UI_Settings.ColorLoad,    5, "ridge",  (1,1)),
                        ('Save',                       'white', self.UI_Settings.ColorSave,    5, "ridge",  (1,2)),
                        ('Commit',                     'black', self.UI_Settings.ColorCommit,  5, "ridge",  (1,3)),

                        ('Clear or Reset inputs',      'black', self.UI_Settings.ColorClear,   2, "raised", (2,0)),
                        ('View/test',                  'black', self.UI_Settings.ColorTest ,   2, "raised", (2,1)), 
                        ('Copy output',                'black', self.UI_Settings.ColorCopy,    2, "raised", (2,2)),
                        ('Edit inputs',                'black', self.UI_Settings.ColorEdit,    2, "raised", (2,3)),
                        ]
        ABC = tk.Frame(self.Splash_Pages[self.Splash_Page_Names.index('Program')], bg=self.UI_Settings.ColorText) #, bg='red')
        ABC.grid(row=100, column=0, padx=5+indent_len*1, pady=5, ipadx=0, ipady=2, sticky=tk.NSEW)

        ### relief = flat, raised, sunken, groove, ridge
        Max_Button_Name_Length = max(  [len(X) for X in list(zip(*Button_Info))[0]]   )
        for index, (Button_Name, Button_FG, Button_COLOR, Button_BD, Button_relief, (ROW,COL)) in enumerate(Button_Info):
            Button_New = tk.Button(ABC, 
                text   = '{NM: ^{L}}'.format(NM=Button_Name, L=Max_Button_Name_Length), 
                bg     = Button_COLOR, 
                fg     = Button_FG,
                bd     = Button_BD, 
                relief = Button_relief)

            Button_New.grid(row=ROW, column=COL, padx=5, pady=5, sticky=tk.NSEW, ipadx=10, ipady=0)

    def Create_Tab_Renamer(self, N):
        # Button Frame
        self.PG_name_Buttons = tk.LabelFrame(self.Tabs_List[N], text='Select Rename type:', bg=self.UI_Settings.ColorBGltGrey)
        self.PG_name_Buttons.grid(row=0,  column=0,ipadx=5, pady=0, sticky=tk.NSEW)

        # Pages
        self.Page_Colors = ['light cyan', 'sky blue', 'light yellow', 'khaki']
        self.Pages = [tk.Frame(self.Tabs_List[N], bg=COLOR) for COLOR in self.Page_Colors]

        [XXX.grid(
            row=self.ACTIVE_TAB_ROW, 
            column=self.ACTIVE_TAB_COL, 
            padx=0, pady=0, 
            sticky=tk.NSEW) for XXX in self.Pages]
        [XXX.rowconfigure(   self.ACTIVE_TAB_ROW, weight=1) for XXX in self.Pages]
        [XXX.columnconfigure(self.ACTIVE_TAB_COL, weight=1) for XXX in self.Pages]
        self.PG_name_Buttons.columnconfigure(4, weight=1)



        # Buttons
        self.Rename_Apply_Button = tk.Button(self.PG_name_Buttons, bg=self.UI_Settings.ColorCommit, text='Commit: Rename all', bd=5, relief="ridge", command=self.Rename_All)


        self.Page_Names = ['Variables', 'Steps', 'Interactions', 'Other']
        self.Rename_Buttons = [tk.Button(self.PG_name_Buttons, text=NAME, bd=4) for NAME in self.Page_Names]

        [BUTTON.grid(row=0, column=index, ipadx=20, padx=10*((1+index)%2), pady=5, sticky=tk.EW+tk.S) for index, BUTTON in enumerate(self.Rename_Buttons)]
        self.Rename_Apply_Button.grid(row=0, column=5, ipadx=20, padx=10, pady=5, sticky=tk.EW, ipady=5)


        # Fill Pages 
        self.Create_Pages()

    def Create_Pages(self):
        '''Creates Pages in tab_RENAME. Uses ScrolledNameListsREGEX() to create a Page for each list of [list of Names].
        First [list of [lists]]==[Vars, Arrays, Formulas]'''
        self.EX_Page_Var = ScrolledNameListsREGEX(self.Pages[self.Page_Names.index('Variables')], self.UI_Settings, Data_Lists = self.DISINTEGRATE.Lists_Names_VAFxy, Data_Labels=['Variable', 'Array', 'Formula'])
        self.EX_Page_Var.grid(row=self.ACTIVE_TAB_ROW, column=self.ACTIVE_TAB_COL, padx=5, pady=5, sticky=tk.NSEW)

        self.EX_Page_Step = ScrolledNameListsREGEX(self.Pages[self.Page_Names.index('Steps')], self.UI_Settings, 
                Data_Lists = [self.DISINTEGRATE.List_Steps, self.DISINTEGRATE.List_Feedbacks, self.DISINTEGRATE.List_Popups], 
                Data_Labels=['Step', 'Feedback', 'Popup'])
        self.EX_Page_Step.grid(row=self.ACTIVE_TAB_ROW, column=self.ACTIVE_TAB_COL, padx=5, pady=5, sticky=tk.NSEW)

        try:
            LIST1, DATA1 = zip(*[XXX for XXX in zip(self.DISINTEGRATE.Lists_Names_Inter, self.DISINTEGRATE.Search_Inter) if len(XXX[0])>0])
        except:
            LIST1, DATA1 = (), ()
        self.EX_Page_Other = ScrolledNameListsREGEX(self.Pages[self.Page_Names.index('Interactions')], self.UI_Settings, Data_Lists = LIST1, Data_Labels= DATA1)
        self.EX_Page_Other.grid(row=self.ACTIVE_TAB_ROW, column=self.ACTIVE_TAB_COL, padx=5, pady=5, sticky=tk.NSEW)

        try:
            LIST2, DATA2 = zip(*[XXX for XXX in zip(self.DISINTEGRATE.Lists_Names_Other, self.DISINTEGRATE.Search_Other) if len(XXX[0])>0])
        except:
            LIST2, DATA2 = (), ()
        self.EX_Page_Inter = ScrolledNameListsREGEX(self.Pages[self.Page_Names.index('Other')], self.UI_Settings, Data_Lists = LIST2, Data_Labels= DATA2)
        self.EX_Page_Inter.grid(row=self.ACTIVE_TAB_ROW, column=self.ACTIVE_TAB_COL, padx=5, pady=5, sticky=tk.NSEW)

        self.ActivePageCMD = [self.Show_CMD_closure('Page', index, self.Pages, self.Rename_Buttons) for index in range(len(self.Rename_Buttons))]

        self.ActivePageCMD[0]()

    def Create_Tab_Table(self, N):
        # Largely self contained TableInput UI and Table_Gen algorithm, except self.master.Update_TDX_File()
        self.TBL = TableInput(self.Tabs_List[N], self, self.DISINTEGRATE.Text_Input, self.UI_Settings)
        self.TBL.grid(row=self.ACTIVE_TAB_ROW, column=self.ACTIVE_TAB_COL, sticky=tk.NSEW)

    def Create_Tab_Generator(self, N):
        # Largely self contained DataGen UI and Data_Gen algorithm, except self.master.Update_TDX_File()
        self.GEN = DataGen(self.Tabs_List[N], self, self.DISINTEGRATE.Text_Input, self.UI_Settings)
        self.GEN.grid(row=self.ACTIVE_TAB_ROW, column=self.ACTIVE_TAB_COL, sticky=tk.NSEW)

    def Create_Tab_SPgen(self, N):
        '''Deletes all feedbacks and feedback links from steps.
        Removes import_from_excercise.
        Pauses all steps except first and last.
        Deletes all unused student interactions.
        Sets variables initial value, if there is one.'''
        # Creates Create_Tab_SPgen UI
        self.SPgen_Frame = tk.LabelFrame(self.Tabs_List[N], text='SPgen_Frame', bg=self.UI_Settings.ColorBack1)
        self.SPgen_Frame.grid(row=self.ACTIVE_TAB_ROW, column=self.ACTIVE_TAB_COL, sticky=tk.NSEW)



        SP_Gen_Button = tk.Button(self.SPgen_Frame, command=self.Generate_SP_from_GS, bd=5, relief="ridge", padx=5, pady=5, justify=tk.LEFT)
        SP_Gen_Button.grid(row=0, column=10, sticky=tk.NSEW, columnspan=2)

        CleanUp_Button = tk.Button(self.SPgen_Frame, bg=self.UI_Settings.ColorCommit, bd=5, relief="ridge", command=self.Clean_TDX, justify=tk.LEFT)
        CleanUp_Button.grid(row=0, column=0, sticky=tk.NSEW)

        Spacing = tk.Label(self.SPgen_Frame, text='', bg=self.UI_Settings.ColorBack1)
        Spacing.grid(row=1, column=1, sticky=tk.NSEW, ipadx=10)

        # Controls button label/Disable, depending on filetype (self.File_Just_Extension).
        if   'tdxex' in self.File_Just_Extension:
            SP_Gen_Button.config(state=tk.DISABLED, bg=self.UI_Settings.ColorDisabled, text=u'Convert GS\u2192SP\n***Not a GS file')
            CleanUp_Button.config(text='Commit: (EX)\n Clean unused')
        elif 'tdxgs' in self.File_Just_Extension:
            SP_Gen_Button.config(state=tk.NORMAL, bg=self.UI_Settings.ColorSave, text=u'Commit/Save as SP:\nConvert GS\u2192SP\n\nClean unused\nClean Import/Pause Steps\nSet values to initial')
            CleanUp_Button.config(text='Commit: (GS)\n Clean unused')
        elif 'tdxsp' in self.File_Just_Extension:
            SP_Gen_Button.config(state=tk.DISABLED, bg=self.UI_Settings.ColorDisabled, text=u'Convert GS\u2192SP\n***Not a GS file')
            CleanUp_Button.config(text='Commit: (SP) \nClean Unused interactions\nClean Import/Pause Step\nClean/Set initial values')


        # Shows List of Un-used interactions
        Num_Inter = len(self.DISINTEGRATE.RemovableInteractions)
        Header = tk.Label(self.SPgen_Frame,
            text=u'\u2193 {N} unused interaction{PLURAL} \u2193'.format(N=Num_Inter, 
                PLURAL='' if Num_Inter==1 else 's'), 
            bd=5, 
            relief='ridge', 
            bg=self.UI_Settings.ColorBack1)
        Header.grid(row=2, column=0, sticky=tk.NSEW)

        self.Label_Unused = [tk.Label(self.SPgen_Frame, text=INTER, bg=self.UI_Settings.ColorBack1) for INTER in self.DISINTEGRATE.RemovableInteractions]
        [XXX.grid(row=index+10, column=0, sticky=tk.W) for index, XXX in enumerate(self.Label_Unused)]

        # Shows List of Used interactions
        D_Step_to_Inter = self.DISINTEGRATE.D_Step_to_Inter.items()
        D_Step_to_Inter_lengths = [len(X) for X in self.DISINTEGRATE.D_Step_to_Inter.values()]
        D_Step_to_Inter_length_max = max([0]+list(D_Step_to_Inter_lengths))
        Num_Inter2 = sum(D_Step_to_Inter_lengths)
        Header2 = tk.Label(self.SPgen_Frame, text=u'\u2193 {N} used interaction{PLURAL} \u2193'.format(N=Num_Inter2, PLURAL='' if Num_Inter2==1 else 's'), bd=5, relief='ridge', bg=self.UI_Settings.ColorBack1)
        Header2.grid(row=2, column=10, sticky=tk.EW, columnspan=D_Step_to_Inter_length_max+1)

        self.Label_Used = [tk.Label(self.SPgen_Frame, text=INTER, bg=self.UI_Settings.ColorBack1) for INTER in self.DISINTEGRATE.RemovableInteractions]
        [XXX.grid(row=index+10, column=0, sticky=tk.W) for index, XXX in enumerate(self.Label_Used)]

        for index, (KEY, VALUE) in enumerate(D_Step_to_Inter):
            Row_Header = tk.Label(self.SPgen_Frame, text=u'\u2192 {STEP}'.format(STEP = KEY), bd=2, relief='ridge', anchor=tk.W, bg=self.UI_Settings.ColorText)
            Row_Header.grid(row=10+index, column=10, sticky=tk.EW, padx=5, ipadx=5)
            self.Label_Unused2 = [tk.Label(self.SPgen_Frame, text=INTER, bg=self.UI_Settings.ColorText, anchor=tk.W) for INTER in VALUE]
            [XXX.grid(row=10+index, column=11+index2, sticky=tk.NSEW, padx=1, pady=2) for index2, XXX in enumerate(self.Label_Unused2)]
        self.SPgen_Frame.columnconfigure(0, weight=1)
        for index in range(10,50):
            self.SPgen_Frame.columnconfigure(index, weight=1)

    def Create_Tab_MPart(self, N):
        # Largely self contained TableInput UI and Table_Gen algorithm, except self.MASTERui.Update_TDX_File()
        self.MultiPart = FB_MultiPart(self.Tabs_List[N], self, self.DISINTEGRATE.Text_Input, self.DISINTEGRATE.List_Steps, self.DISINTEGRATE.D_Step_to_Inter, self.UI_Settings)
        self.MultiPart.grid(row=self.ACTIVE_TAB_ROW, column=self.ACTIVE_TAB_COL, sticky=tk.NSEW)

    ### File operations
    def Open_TDX_File(self, Set_FileLocation = None):
        if self.RecentEdits:
            print('Error: Load with current TDX_Edits') 
            TEXTpop = 'Unsaved TDX_Edits have been made in the editor.\nAre you sure you want to load a new file?'
            TEXTyes = 'Yes.\nLoad new file: Cancel any TDX_Edits'
            COLORyes = self.UI_Settings.ColorLoad,
            TEXTno  = 'No.\nCancel: Keep TDX_Edits and return to editor'
            COLORno = self.UI_Settings.ColorClear
            A = ForcePopup(self, TEXTpop,  [(TEXTyes, COLORyes), (TEXTno, COLORno)]  )
            A_SELECTION = A.SELECTION
            if A_SELECTION==None:
                print('Error interaction: No selection made')
            elif A_SELECTION==0:
                print('Error interaction: User selected load and clear unsaved TDX_Edits') 
                self.Open_TDX_File_operations(Set_FileLocation)
            elif A_SELECTION==1:
                print('Error interaction: User selected return to file with unsaved TDX_Edits') 
                pass
            else:
                print('Error: ForcePopup() return value')
        else:
            self.Open_TDX_File_operations(Set_FileLocation)


    def Open_TDX_File_operations(self, Set_FileLocation):

        '''Opens a TDX file (using askopenfilename to locate) and sends its text to self.Disintegrate_TDX_File(), after passing basic checks'''
        if Set_FileLocation==None:
            self.FileLocation = askopenfilename(initialdir = self.InitialDirectory, filetypes = (("TDX files","*.tdx*"),("all files","*.*")))
        else:
            self.FileLocation = Set_FileLocation

        self.FileName = self.FileLocation.split("/")[-1]
        self.FolderName = "/".join(self.FileLocation.split("/")[:-1])

        self.File_Just_Name, self.File_Just_Extension = os.path.splitext(self.FileName)
        print('OPEN: FileType= {TYPE}\t"{NAME}"'.format(
            NAME=self.File_Just_Name, 
            TYPE=self.File_Just_Extension[4:].upper()))



        if self.FileLocation=='':
            print ('No file selected')
        elif 'tdx' not in self.File_Just_Extension:
            self.Clear_Tabs()
            print ('Not a TDX file')
        else:
            #print('self.FileLocation FILE_OPEN', self.FileLocation)
            self.Clear_Tabs()
            self.InitialDirectory = self.FileLocation[:]
            with open(self.FileLocation) as FILE_OPEN:
                self.ORIGINAL_TEXT = FILE_OPEN.read()
                if len(self.ORIGINAL_TEXT)==0:
                    print('No data in file')
                else:
                    self.Disintegrate_TDX_File(self.ORIGINAL_TEXT)
                    self.Create_Tabs()



    def Disable_Tabs(self):
        [XXX.configure(state=tk.DISABLED) for XXX in self.Tab_Buttons]


    def Clear_Tabs(self):
        self.Disable_Tabs()
        try:
            [TAB.grid_remove() for TAB in self.Tabs_List]
        except:
            try:
                self.Load_Count += 1
                print('Clear_Tabs(self)": Probably an error for Loading #{}'.format(self.Load_Count))
            except:
                self.Load_Count = 1
                #print('Clear_Tabs(self)": First loading')


    def Disintegrate_TDX_File(self, Load_File):
        '''DisintegrateTDX finds steps, interactions, and other TDX file components'''
        self.DISINTEGRATE = DisintegrateTDX(FILE=Load_File)
        self.title("TDX Editor ({})".format(self.FileName))

    def Update_TDX_File(self, Load_File):
        '''Updates each Tab to use most recent file. Occurs after Commit'''
        # Passes edited Load_File to update all UI Tabs
        self.Disintegrate_TDX_File(Load_File)
        self.RecentlyUpdated(True)

        # Splash Tab update
        self.Splash_Tab.grid_forget()
        self.Create_Tab_Splash(self.Tab_lookups.index('tab_INTRO'))

        # Rename Tab update
        self.PG_name_Buttons.grid_forget()
        N = self.ActivePageN
        self.Create_Tab_Renamer(self.Tab_lookups.index('tab_RENAME'))
        self.ActivePageCMD[N]()     # Resets active Page, when refreshing

        #Table Tab update
        self.TBL.Update_Table(Load_File)

        #Data Gen Tab update
        self.GEN.Update_TDX(Load_File)

        #SP Gen Tab update
        self.SPgen_Frame.grid_forget()
        self.Create_Tab_SPgen(self.Tab_lookups.index('tab_SP'))

        #MultiPart FB Tab update
        self.MultiPart.grid_forget()
        self.Create_Tab_MPart(self.Tab_lookups.index('tab_FB'))



    ### Save file operations
    def Save_Get_Backup_Name(self):
        ### Get self.copy_Name and basic data
        Files_In_Folder = os.listdir(self.FolderName)
        #print('Saved 1.1', Files_In_Folder)
        version_Prefix = r'_V' # _Version
        Similar_FileNames = ['.'.join(XXX.split('.')[:-1]) for XXX in Files_In_Folder if self.File_Just_Name in XXX]
        #print('Saved 1.2', Similar_FileNames)

        File_Numbers = [re.findall('(?<={NAME}{EDIT})\d+'.format(NAME=re.escape(self.File_Just_Name), EDIT=re.escape(version_Prefix)), XXX) for XXX in Similar_FileNames]
        #print('Saved 1.3', File_Numbers)
        File_Nums_INT = [-1,]
        for NUM in File_Numbers:
            try:
                File_Nums_INT.append(int(NUM[0]))
            except:
                pass
        File_Num_Integer = max(File_Nums_INT)+1
        #print('Saved 1.4', File_Num_Integer, File_Nums_INT)
        self.copy_Name = (
            self.FolderName + r'/' + 
            self.File_Just_Name + 
            version_Prefix + 
            str(File_Num_Integer) + 
            self.File_Just_Extension)
        # This asserts that the .copy_Name is unique, which the File_Num_Integer should guarantee
        assert (not os.path.exists(self.copy_Name)), 'Backup copy: potential-overwrite error in Save_Get_Backup_Name()'

    def CreateBackup(self):
        #print('Saved 1.0', self.FolderName)
        self.Save_Get_Backup_Name()
        #print('Saved 1.5', self.copy_Name)
        with open(self.copy_Name, 'w+') as BACKUP_FILE:
            BACKUP_FILE.write(self.ORIGINAL_TEXT)
        print("Created backup of original text:\t\t[#print('Saved 1.9')]\n\t{}".format(self.copy_Name))

    def Save_Process_Inputs(self, Text_to_Write, fileType_override):
        #print('Saved 2.0', Text_to_Write==False)
        if Text_to_Write==False:
            self.Text_to_Write = self.DISINTEGRATE.Text_Input
        else:
            self.Text_to_Write = Text_to_Write

        #print('Saved 2.1', fileType_override!=False)
        if fileType_override!=False:
            #print('Saved 2.1a', self.FolderName, self.File_Just_Name, fileType_override)
            self.NewFileLocation = r'{PATH}/{NAME}.{TYPE}'.format(
                    PATH=self.FolderName, 
                    NAME=self.File_Just_Name, 
                    TYPE=fileType_override)
        else:
            self.NewFileLocation = self.FileLocation
        #print('Saved 2.9', self.NewFileLocation)
        pass

    def Save_Check_No_Edits(self):
        ### Check for No_Edits
        #print('Saved 3.0')
        OLD = self.ORIGINAL_TEXT
        #print('Saved 3.1')
        with open(self.FileLocation, 'r') as NEW_FILE:
            NEW = NEW_FILE.read()
        #print('Saved 3.2')
        CHECK = (NEW==OLD)
        #print('Saved 3.9', CHECK)
        return (CHECK)

    def Save_TDX_File(self):
        #print('Saved 9.0')
        with open(self.NewFileLocation, 'w') as NEW_FILE:
            #print('Saved 9.1')
            NEW_FILE.write(self.Text_to_Write)
            #print('Saved 9.2')
            self.ORIGINAL_TEXT = self.Text_to_Write
            self.RecentlyUpdated(False)
        #print('Saved 9.3')
        print("Save Complete:\t\t\t\t[#print('Saved 9.9')]\n\t{}".format(self.NewFileLocation))



    def Save_Process(self, Text_to_Write=False, fileType_override=False):
        'Saves the edited TDX file, and makes a copy of the original file (with version_Prefix(#File_Num_Integer#) appended to name)'
        # For debugging
        # REGEX Search  ===> #(print\('Saved.*?\d\.\d\w*)'
        # REGEX replace ===> \1  OR  #\1
        self.CreateBackup()                                                 # Saved 1.#
        try:
            self.Save_Process_Inputs(Text_to_Write, fileType_override)      # Saved 2.#
            if self.Save_Check_No_Edits():                                  # Saved 3.#
                self.Save_TDX_File()                                        # Saved 9.#
            else:
                print('Error: File has been edited since loading.') 
                TEXTpop = 'The current TDX file has been edited outside this program since it was loaded.\nDo you want to keep the TDX_Edits made in this editor?'
                TEXTyes = 'Yes.\nSave: Overwrite current file with these TDX_Edits'
                COLORyes = self.UI_Settings.ColorCommit
                TEXTno  = 'No.\nCancel: Cancel TDX_Edits and load in the current file'
                COLORno = self.UI_Settings.ColorLoad
                A = ForcePopup(self, TEXTpop,  [(TEXTyes, COLORyes), (TEXTno, COLORno), ]  )
                A_SELECTION = A.SELECTION
                if A_SELECTION==None:
                    print('Error interaction: No selection made')
                elif A_SELECTION==0:
                    print('Error interaction: User selected clear TDX_Edits') 
                    self.Open_TDX_File(self.FileLocation)
                elif A_SELECTION==1:
                    print('Error interaction: User selected overwrite') 
                    self.Save_TDX_File()
                else:
                    print('Error: ForcePopup() return value')

        except: 
            print('Error: General save-exception; check Save_Process()')


    ### Helper operations
    def QUIT(self):
        if self.RecentEdits:
            print('Error: Quit with current TDX_Edits') 
            TEXTpop = 'Unsaved TDX_Edits have been made in the editor.\nAre you sure you want to quit?'
            TEXTyes = 'Yes.\nQuit: Cancel any TDX_Edits'
            COLORyes = self.UI_Settings.ColorExit
            TEXTno  = 'No.\nCancel: Keep TDX_Edits and return to editor'
            COLORno = self.UI_Settings.ColorCommit
            A = ForcePopup(self, TEXTpop,  [(TEXTyes, COLORyes), (TEXTno, COLORno)]  )
            A_SELECTION = A.SELECTION
            if A_SELECTION==None:
                print('Error interaction: No selection made')
            elif A_SELECTION==0:
                print('Error interaction: User selected quit and clear unsaved TDX_Edits') 
                self.DESTROY()
            elif A_SELECTION==1:
                print('Error interaction: User selected return to file with unsaved TDX_Edits') 
                pass
            else:
                print('Error: ForcePopup() return value')

        else:
            self.DESTROY()


    def DESTROY(self):
        self.destroy()

    def Duplicate_Check_TDX(self, TDXtext):
        '''Creates a list of duplicate named objects in the TDX, object types listed in NamedSearches'''
        # Generates list of REGEX searches using object types listed in NamedSearches
        NamedSearches = ["var", "array", "formula", "figure", "collection", "xygraph", "NumberLine", "BarChart",
        "piechart", "field", "multchoice", "sdgrapher", "xycursor", "nlcursor", "fillin", "Timeline", "image", 
        "datatable", "realtimedata", "acctable", "essay", "draganddrop"]

        # Performs REGEX Searches 
        SEARCH2 = '(?:{}) name=\"(\w+)\"'.format('|'.join(NamedSearches))
        ListSearches2 = [re.findall(SEARCH2 , TDXtext , flags=re.IGNORECASE)][0]
        ListSearches2.sort()

        return self.Duplicate_Check_list(ListSearches2)

    def Duplicate_Check_list(self, CheckList):
        CheckList = [NAME.lower() for NAME in CheckList]
        singles = set()
        doubles = set()
        for name in CheckList:
            if name in singles:
                doubles.add(name)
            else:
                singles.add(name)
        DoublesList = sorted(list(doubles))
        return DoublesList

    def Test_Print(self):
        try:
            self.EX_Page_Var.GET_names()
            #A = [zip(XXX.names_old_flat, XXX.names_new_flat) for XXX in self.EX_Page_Var]
            print (zip(self.EX_Page_Var.names_old_flat, self.EX_Page_Var.names_new_flat))
        except:
            print ('No Data')

    def _on_mousewheel(self, event):
        '''Enables scrolling in Splash_Tab: Deprecated'''
        self.Splash_Tab.canvas.yview_scroll(-1*int((event.delta/120)), "units")

    def Show_CMD_closure(self, 
                        ACTIVE_TYPE, N, 
                        TABS_List, TAB_Buttons, ):
        'Uses closure to create functions to display each Tab in TABS_List and colors active Button in TAB_Buttons'

        #ERROR: consider creating/linking CMDs, windows, and buttons here
        def Tab_Show_closed():

            [TAB.grid() if (N==index) else TAB.grid_remove() for index, TAB in enumerate(TABS_List)]
            [TAB.configure(bg=self.UI_Settings.ColorActive) if N==index else TAB.configure(bg=self.UI_Settings.ColorPassive) for index, TAB in enumerate(TAB_Buttons)]
            if   ACTIVE_TYPE == 'Tab':
                self.ActiveTabN  = N
            elif ACTIVE_TYPE == 'Page':
                self.ActivePageN = N
        
        TAB_Buttons[N].configure(command=Tab_Show_closed)

        return Tab_Show_closed

    def RecentlyUpdated(self, EditState):
        if EditState == self.RecentEdits:
            pass
        else:
            self.RecentEdits = EditState
            if EditState==True:
                # active save button
                self.Button_Save.configure(state=tk.NORMAL, bg=self.UI_Settings.ColorSave)
            else:
                # disabled save button
                self.Button_Save.configure(state=tk.DISABLED, bg=self.UI_Settings.ColorDisabled)
                pass

    ### Main operations
    def Clean_TDX(self):
        '''Uses SP_Cleaner() to prepare file. Has different operations, depending on filetype (Extension_lower)'''
        print('Loading new SP data')

        Extension_lower = self.File_Just_Extension.lower()
        # Passes edited TEXT to parent class, to update all UI Tabs
        if   'tdxex' in Extension_lower:
            TEXT = SP_Cleaner(self.DISINTEGRATE.Text_Input, self.DISINTEGRATE.RemovableInteractions)
            self.Update_TDX_File(TEXT)
            print('Commit: Clean_TDX: filetype = EX')
        elif 'tdxgs' in Extension_lower:
            TEXT = SP_Cleaner(self.DISINTEGRATE.Text_Input, self.DISINTEGRATE.RemovableInteractions)
            self.Update_TDX_File(TEXT)
            print('Commit: Clean_TDX: filetype = GS')
        elif 'tdxsp' in Extension_lower:
            TEXT = SP_Cleaner(self.DISINTEGRATE.Text_Input, self.DISINTEGRATE.RemovableInteractions, SPtype=True)
            self.Update_TDX_File(TEXT)
            print('Commit: Clean_TDX: filetype = SP')
        else:
            print('filetype error')
        self.ActiveTabCMD[self.Tab_lookups.index('tab_SP')]

    def Generate_SP_from_GS(self):
        '''Applies all SP_Cleaner() operations and saves a GS file as an SP'''
        self.Clean_TDX()
        Extension_lower = self.File_Just_Extension.lower()
        TEXT = SP_Cleaner(self.DISINTEGRATE.Text_Input, self.DISINTEGRATE.RemovableInteractions, SPtype=True)

        # Passes edited TEXT to parent class, to update all UI Tabs
        self.Update_TDX_File(TEXT)
        self.Save_Process(Text_to_Write=TEXT, fileType_override='tdxsp')
        print('Commit: Generate_SP_from_GS')

    def Rename_All(self):
        '''Renames all items listed in rename pages (self.List_of_Pages)'''
        self.List_of_Pages = [self.EX_Page_Var, self.EX_Page_Step, self.EX_Page_Other, self.EX_Page_Inter]
        [XXX.GET_names() for XXX in self.List_of_Pages]

        #### Uses VAF_Renamer() function to rename all Variables, Arrays, Formulas
        ###Data001 = VAF_Renamer(self.DISINTEGRATE.Text_Input, self.EX_Page_Var.names_old_flat, self.EX_Page_Var.names_new_flat)


        # Uses OTHER_Renamer() function to rename all other items
        Other_Names_Old = tuple(self.EX_Page_Step.names_old_flat) + tuple(self.EX_Page_Other.names_old_flat) + tuple(self.EX_Page_Inter.names_old_flat)
        Other_Names_New = tuple(self.EX_Page_Step.names_new_flat) + tuple(self.EX_Page_Other.names_new_flat) + tuple(self.EX_Page_Inter.names_new_flat)

        ###Data002 = OTHER_Renamer(Data001, Other_Names_Old, Other_Names_New)


        Renamed_Data = Complete_Renamer(self.DISINTEGRATE.Text_Input, self.EX_Page_Var.names_old_flat, self.EX_Page_Var.names_new_flat, Other_Names_Old, Other_Names_New)

        # Updates file, if there are no duplicates
        dupes = self.Duplicate_Check_TDX(Renamed_Data)
        print('dupes', dupes)
        if len(dupes)==0:
            # Passes edited Data002 to parent class, to update all UI Tabs
            self.Update_TDX_File(Renamed_Data)
            self.ActiveTabCMD[self.Tab_lookups.index('tab_RENAME')]
            print('Commit: Rename_All()')
        else:
            [XXX.Highlight_Dupes(dupes) for XXX in self.List_of_Pages]

class DisintegrateTDX():
    'Disintegrates a TDX and extracts relevant information (step names, interactions...)'
    #ERROR: add extract array data, DT_data, table_data, show (original/edited text)
    def __init__(self, FILE):
        self.Text_Input = FILE
        print('LOADING: DisintegrateTDX')

        self.Update_Data()

    ### Main functions
    def Update_Data(self):
        self.Extract_Names()
        self.Extract_Steps()
        self.Extract_Interactions()
        self.GetAllUsedNames()

    def Extract_Names(self):
        # Lists of object names
        self.Search_VAFxy = ["var", "array", "formula"]
        self.Search_Inter = ["field", "multchoice", "fillin", "draganddrop",
                                    "nlcursor", "xycursor", "sdgrapher", 
                                    "acctable", "realtimedata", "essay"]
        self.Search_Other = ["figure", "image", "datatable", 
                                    "xygraph", "BarChart", "piechart", "NumberLine", 
                                    "Timeline", "collection"]


        # Creates lists of [var, array, formula] , [inter-actions], [other] from the tdx FILE
        self.Lists_Names_VAFxy = [self.Search_This(search) for search in self.Search_VAFxy]
        self.Lists_Names_Inter = [self.Search_This(search) for search in self.Search_Inter]
        self.Lists_Names_Other = [self.Search_This(search) for search in self.Search_Other]
        self.List_Names_V, self.List_Names_A, self.List_Names_F = self.Lists_Names_VAFxy


        self.List_Flat_TDXsort = [str(item).lower() for sublist in [self.Lists_Names_VAFxy + self.Lists_Names_Other + self.Lists_Names_Inter] for item in sublist]
        self.List_Flat_TDXsort.sort()
        self.List_Flat_TDXsort.sort(key=len, reverse=True)

    def GetAllUsedNames(self):
        self.UsedNames = re.findall('(?<=name=\")(\w+)', self.Text_Input, flags=re.IGNORECASE)
        self.UsedNames = [name.lower() for name in self.UsedNames]

    def Extract_Steps(self):
        Windows = re.findall('(?<=<window name=\")\w+(?=\")', self.Text_Input)
        Window_Locations = [self.Text_Input.find('<window name=\"{}\"'.format(Name)) for Name in Windows] + [self.Text_Input.find('</windows>')]

        Steps_by_Window = [re.findall("(?<=<step name=\")\w+(?=\")" , 
                            self.Text_Input[a:b] , 
                            flags=re.IGNORECASE
                            ) for (a,b) in zip(Window_Locations,Window_Locations[1:])]

        Window_Step_Lists = [(a,b) for (a,b) in zip(Windows, Steps_by_Window)]

        self.List_Feedbacks = Steps_by_Window[Windows.index('feedback')] if 'feedback' in Windows else ['']
        self.List_Popups    = Steps_by_Window[Windows.index('popups')]   if 'popups'   in Windows else ['']
        self.List_Steps     = re.findall(
                "(?<=<display step=\")\w+(?=\")" , 
                self.Text_Input[self.Text_Input.find("<controller>"):self.Text_Input.find("</controller>")] , 
                flags=re.IGNORECASE)

        self.List_All_Steps = self.List_Steps + self.List_Feedbacks + self.List_Popups

    def Extract_Interactions(self):
        '''Given text from a TDX file, finds (unused interactions) along with (used interactions and what step they appear)'''

        self.List_Flat_Inter    = [item for sublist in self.Lists_Names_Inter for item in sublist]
        self.List_Flat_Inter    = [X.lower() for X in self.List_Flat_Inter]
        self.List_Inter_byType  = [(TYPE,INTER) for TYPE,INTER in zip(self.Search_Inter,self.Lists_Names_Inter) if len(INTER)!=0]
        self.Used_Inter         = [b for b in self.Lists_Names_Inter if len(b)>0]
        self.Used_Inter_by_type = [(a,b) for a,b in zip(self.Search_Inter, self.Lists_Names_Inter) if len(b)>0]



        # A list of all step names (and MCs that could contain a FR) in the tdx file
        AllSteps =  re.findall('<step name=\"(\w+)".*?</step>',             self.Text_Input, flags=re.DOTALL)
        StepText = [re.findall('<step name=\"({}".*?)</step>'.format(STEP), self.Text_Input, flags=re.DOTALL)[0] for STEP in AllSteps]

        AllMultC = self.Lists_Names_Inter[self.Search_Inter.index("multchoice")]
        StepMult = [re.findall('<multchoice name=\"({}".*?)</multchoice>'.format(MULT), self.Text_Input, flags=re.DOTALL)[0] for MULT in AllMultC]




        AllSteps += AllMultC
        StepText += StepMult

        # A list of interactions, for each step
        Items_All_ByStep = [re.findall('>(\w+)(?:\.output)?(?:\.response)?</control>',ST, flags=re.DOTALL) for ST in StepText]
        #print(Items_All_ByStep)
        #print(self.List_Flat_Inter)

        Interactions_by_Step = [[item for item in List if item.lower() in self.List_Flat_Inter] for List in Items_All_ByStep]
        #print(Interactions_by_Step)
        Interactions_by_Step_Flat = [item for List in Interactions_by_Step for item in List]



        # A dictionary of {step : [interactions in the step]} trimmed to only those actually used in the tdx file
        self.D_Step_to_Inter = {a: b for a,b in zip(AllSteps,Interactions_by_Step) if len(b)!=0}

        # A dictionary of {interaction : [step(s) it appears in]}
        self.D_Inter_to_Step = {a: [] for a in Interactions_by_Step_Flat}
        for STEP in self.D_Step_to_Inter.keys():
            for inter in self.D_Step_to_Inter[STEP]:
                self.D_Inter_to_Step[inter] += [STEP]

        # A list of interactions that do not appear in any step
        self.RemovableInteractions = list(set(self.List_Flat_Inter)-set([XXX.lower() for XXX in Interactions_by_Step_Flat]))


    ### Helper functions
    def Search_This(self,NAME):
        #print('self.Text_Input XXX', self.Text_Input)
        Found_Names = re.findall('(?<={} name=\")\w+(?=\")'.format(NAME), self.Text_Input, flags=re.IGNORECASE)
        Found_Names.sort(key=str.lower)
        return (Found_Names)

    def duplicates(self, DUPES):
        #*** Used to create list of duplicate named objects
        ListNamesAll = [XXX.lower() for XXX in DUPES]
        
        singles = set()
        doubles = set()
        for name in ListNamesAll:
            if name in singles:
                doubles.add(name)
            else:
                singles.add(name)
        doubles = sorted(list(doubles))
        return doubles

### Tab internals
class TableInput(tk.Frame):
    'Defines and launches TableInput UI in Table-Tab (plus table creation methods)'
    def __init__(self, parent, master, TEXT, SELF_SETTINGS, *args, **kw):
        tk.Frame.__init__(self, parent)
        parent.master.bind_class("Text","<Control-a>", self.selectall)

        self.UI_Settings = SELF_SETTINGS

        self.InputText = TEXT
        self.master = master
        self.DTnames = self.master.DISINTEGRATE.Lists_Names_Other[self.master.DISINTEGRATE.Search_Other.index("datatable")]

        self.index = 1
        self.Create_UI()

    def Create_UI(self):
        self.SeparatorDict = {'Tab':'\t', 'Space':' ', 'Comma':','}
        self.OptionMenuValueSet = 'Tab'

        ### Main section
        self.configure(bg=self.UI_Settings.ColorBack1)
        Page_Left  = tk.LabelFrame(self, bg=self.UI_Settings.ColorBack1, text='Data Input')
        Page_Right = tk.LabelFrame(self, bg=self.UI_Settings.ColorBack1, text='Data Output')
        Page_Lower = tk.LabelFrame(self, bg=self.UI_Settings.ColorBack1, text=u'\u2193\u2193\u2193 \tEnter Data\t \u2193\u2193\u2193')

        Page_Left.grid( row=0, column=0, ipady=5, padx=5, sticky=tk.NSEW)
        Page_Right.grid(row=0, column=1, ipady=5, padx=5, sticky=tk.NSEW)
        Page_Lower.grid(row=1, column=0, ipady=5, padx=5, sticky=tk.NSEW, columnspan=2)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=4)
        self.rowconfigure(1, weight=1)

        ### Page_Left
        # Tab seperator
        self.Separate = tk.StringVar(self.master)
        self.Separate.set('Tab') 
        self.SeparateEnter = tk.OptionMenu(Page_Left, self.Separate, *(self.SeparatorDict.keys()), command=self.func)
        self.SeparateEnter.configure(bg=self.UI_Settings.ColorInputFL)
        self.SepLabel = tk.Label(Page_Left, text=u"Each newline is a Row-Separator.\n\u2193\u2193 Choose a Column-Separator \u2193\u2193", justify=tk.LEFT, bg=self.UI_Settings.ColorBack1)
        # Transpose Box
        self.BoxVarTranspose = tk.IntVar()
        self.TransBoxToggle  = tk.Checkbutton(Page_Left, highlightcolor='green', selectcolor="white", text='Transpose Data', variable=self.BoxVarTranspose, bg=self.UI_Settings.ColorBack1, anchor=tk.W)

        self.Test_button = tk.Button(Page_Left, text="View Test Table", bg=self.UI_Settings.ColorTest , command=self.Sample_Popup)

        # locations
        self.SepLabel.grid(      row=0, column=0, ipady=0,  sticky=tk.W)
        self.SeparateEnter.grid( row=1, column=0, ipady=3, sticky=tk.NSEW)
        self.TransBoxToggle.grid(row=3, column=0, ipady=0, sticky=tk.NSEW, padx=5)
        self.Test_button.grid(   row=4, column=0,  pady=3, sticky=tk.NSEW, padx=5)

        Page_Left.columnconfigure(0, weight=1)
        Page_Left.rowconfigure(   2, weight=1)

        ### Page_Right
        # insert
        self.orig_color = self.SeparateEnter.cget("background")
        self.Insert_Table_button = tk.Button(Page_Right, text="Commit: Insert Table", bg=self.UI_Settings.ColorDisabled, state=tk.DISABLED, command=self.InsertTable, bd=5, relief="ridge") 
        self.Insert_Table_button.grid(row=0, column=3, pady=0, padx=2, sticky=tk.EW)

        self.Insert_Array_button = tk.Button(Page_Right, text="Commit: Insert Array(s)", bg=self.UI_Settings.ColorCommit, command=self.InsertArray, bd=5, relief="ridge")
        self.Insert_Array_button.grid(row=1, column=3, pady=0, padx=2, sticky=tk.EW)

        self.Insert_DT_button = tk.Button(Page_Right, text="Commit: Insert Data Table", bg=self.UI_Settings.ColorCommit, command=self.InsertDT, bd=5, relief="ridge")
        self.Insert_DT_button.grid(row=2, column=3, pady=0, padx=2, sticky=tk.EW)

        # select step, dropdown
        self.ListedVar = tk.StringVar(self)
        self.ListedVar.set('Select a step') 
        self.StepEnter = tk.OptionMenu(Page_Right, self.ListedVar, '')
        self.StepEnter.configure(bg=self.UI_Settings.ColorInputFL)

        self.StepEnter.grid(row=0, column=0, sticky=tk.EW)
        self.ListedVar.trace('w',self.Activator)


        #copyable
        self.Table_button = tk.Button(Page_Right, text="Copyable Table", bg=self.UI_Settings.ColorCopy, command=self.CopyableTable)
        self.Table_button.grid(row=0, column=2, sticky=tk.NSEW, pady=2, ipady=2)

        self.Array_button = tk.Button(Page_Right, text="Copyable Array(s)", bg=self.UI_Settings.ColorCopy, command=self.CopyableArray)
        self.Array_button.grid(row=1, column=2, sticky=tk.NSEW, pady=2, ipady=2)

        self.DT_button = tk.Button(Page_Right, text="Copyable Data Table", bg=self.UI_Settings.ColorCopy, command=self.CopyableDT)
        self.DT_button.grid(row=2, column=2, sticky=tk.NSEW, pady=2, ipady=2)

        self.InfoLabel1 = tk.Label(Page_Right, text='Each row is an array. Add quotes around array text.\nThe First column=Array names (Blue in Test Table)', justify=tk.LEFT, bg=self.UI_Settings.ColorBack1)
        self.InfoLabel1.grid(row=1, column=0, ipadx=5, sticky=tk.E, columnspan=2)

        self.InfoLabel2 = tk.Label(Page_Right, text='The data table name will be generated ("DTgen###")', bg=self.UI_Settings.ColorBack1)
        self.InfoLabel2.grid(row=2, column=0, ipadx=5, sticky=tk.E, columnspan=2)

        #Delete button and completed info label
        self.delete_button = tk.Button(Page_Right, text="Clear Entered Data", bg=self.UI_Settings.ColorClear, command=self.delete)
        self.delete_button.grid( row=3, column=0, sticky=tk.EW, padx=2)

        self.FinalLabel = tk.Label(Page_Right, text='', bg=self.UI_Settings.ColorBack1)
        self.FinalLabel.grid(row=4, column=0, columnspan=5, sticky=tk.W)

        Page_Right.columnconfigure(0, weight=1)
        Page_Right.columnconfigure(1, weight=9)
        Page_Right.columnconfigure(2, weight=1)
        Page_Right.columnconfigure(3, weight=1)

        # lower section
        Page_Lower.columnconfigure(0, weight=1)
        Page_Lower.rowconfigure(1, weight=1)

        self.AllEnter = tk.Text(Page_Lower, undo=True)
        self.AllEnter.grid(row=1, column=0, pady=10, padx=10, ipadx=20, columnspan=2, sticky=tk.NSEW)


        # tries to get text, if a TDX file is active in notepad++
        self.FirstTextTF = True
        self.TextInitial = True

        self.Reset_DropDown_Names()

    ### Basic functionality
    def delete(self):               # deletes entered text
        self.AllEnter.delete("1.0",'end')

    def func(self,value):           # sets variable to separator selection
        self.OptionMenuValueSet = value

    def selectall(self, event):     # allows ctrl+a (select all) to work in text box
        event.widget.tag_add("sel","1.0","end")

    def Activator(self,*args):      # activates "Insert Table" button after a step is chosen
        self.Insert_Table_button.configure(state=tk.NORMAL, bg=self.UI_Settings.ColorCommit)

    def Print2clip(self,text):      # Print to clipboard
        clippy = tk.Tk()
        clippy.withdraw()
        clippy.clipboard_clear()
        clippy.clipboard_append(text)
        clippy.update()
        clippy.destroy()

    def Update_Table(self,New_File):# Updates file, that table will be added to
        self.InputText = New_File
        self.DTnames = self.master.DISINTEGRATE.Lists_Names_Other[self.master.DISINTEGRATE.Search_Other.index("datatable")]
        self.Reset_DropDown_Names()

    def Sample_Popup(self):         # Popup table example
        self.PopupGen = tk.Toplevel(self.master)
        self.PopupGen.minsize(400, 200) 
        self.PopupGen.geometry("%dx%d+30+30" % (900, 600))

        TITLE = 'Test Table (Transposed)' if self.BoxVarTranspose.get() else 'Test Table'
        self.Popup_Scroll = ScrolledFrameXY(self.PopupGen, TitleX = TITLE)

        self.Popup_Scroll.grid(sticky=tk.NSEW, row=0, column=0)
        self.PopupGen.rowconfigure(0, weight=1)
        self.PopupGen.columnconfigure(0, weight=1)
        
        self.Text_2_Matrix()
        max_col = 0
        for INDEX_row, DATA_row in enumerate(self.CellMatrix):
            Row_Header = tk.Label(self.Popup_Scroll.interior, text='#{}'.format(INDEX_row+1), anchor=tk.W, bg='black', fg='white')
            Row_Header.grid(row=1+INDEX_row, column=0, padx=5, pady=1, sticky=tk.E)
            for INDEX_col, DATA_cell in enumerate(DATA_row):
                A = tk.Label(self.Popup_Scroll.interior, text=DATA_cell, anchor=tk.W)
                A.grid(row=1+INDEX_row, column=1+INDEX_col, padx=1, pady=1, ipadx=5, sticky=tk.NSEW)
                if INDEX_col==0:
                    A.configure(bg='light blue')
                max_col = max(max_col, INDEX_col)
        for INDEX_col in range(1,max_col+1):
            Col_Header = tk.Label(self.Popup_Scroll.interior, text='#{}'.format(1+INDEX_col), bg='black', fg='white')
            Col_Header.grid(row=0, column=1+INDEX_col, padx=1, pady=5, sticky=tk.EW)
        Col_Header = tk.Label(self.Popup_Scroll.interior, text='Array Names', bg='black', fg='light blue')
        Col_Header.grid(row=0, column=1, padx=1, pady=5, sticky=tk.EW)


    ### Name information
    def Reset_DropDown_Names(self):
        self.ListedVar.set('Select a step') 
        self.StepEnter['menu'].delete(0, 'end')
        self.Insert_Table_button.configure(bg=self.UI_Settings.ColorDisabled, state=tk.DISABLED)
        for NAME in self.master.DISINTEGRATE.List_All_Steps:
            self.StepEnter["menu"].add_command(label=NAME, command=lambda NAME0=NAME: self.ListedVar.set(NAME0))



    ### Text editing
    def cell2(self, CELL):
        '''
        input : text string for a cell. 
        output: cell data wrapped in XML tags for text or variable
        '''
        list_data = re.findall('([^~\n\r]+|~\w+\.?[\d\{\}]*)', CELL)
        new_data = []
        for R in list_data:
            R = cgi.escape(R)
            if R[0] == '~':
                new_data.append(' <control br="0" vshiftabs="1" spacing="1" textstyle="Normal" data="">' + R[1:] + '</control> ')
            else:
                new_data.append(' <text br="0">' + R + '</text> ')
        return ' <cell width="75"> ' + ''.join(new_data) + ' </cell> '

    def AddObjects(self,OBJECT):        # closes open "object/" tag, and adds OBJECT to list of meta_name="objects"
        if self.EditText.find('<objects>') == -1:
            self.EditText = self.EditText.replace('<objects/>',' <objects>  </objects>')

        if self.EditText.find('<meta name="objects" value') == -1:
            self.EditText = self.EditText.replace('<toolbuttons names="', '<meta name="objects" value="{}"/> \r <toolbuttons names="'.format(OBJECT))
        else:
            FileObjects = re.findall('(?<=\<meta name\=\"objects\" value\=\")([\w,]+)"',self.InputText)[0]
            NewObjects = FileObjects.split(',')
            NewObjects = set(NewObjects)
            NewObjects.add(OBJECT)
            NewObjects = (',').join(list(NewObjects))
            self.EditText = self.EditText.replace('<meta name="objects" value="{}"'.format(FileObjects),'<meta name="objects" value="{}"'.format(NewObjects))

    def Text_2_Matrix(self):
        text = self.AllEnter.get("1.0",'end')
        
        text = cgi.escape(text)
        text = text.replace('"','&#39;')
        text = text.replace("'",'&#39;')
        text = re.sub('[\n\r]+$','',text)

        Rows = text.split('\n')
        self.CellMatrix = [row.split(self.SeparatorDict[self.OptionMenuValueSet]) for row in Rows]

        self.Rows_Length = len(Rows)
        self.Col_Lengths = [len(XXX) for XXX in self.CellMatrix]
        self.Cols_Length = max(self.Col_Lengths)
        self.CellMatrix = [ROW+['']*(self.Cols_Length-len(ROW)) for ROW in self.CellMatrix]

        if self.BoxVarTranspose.get():
            self.CellMatrix = list(zip(*self.CellMatrix))

    ### Arrays
    def ArrayGen(self):         # generates arrays from the entered text
        self.Text_2_Matrix()


        CellMatrix = list(zip(*self.CellMatrix))

        self.ArrayNames  = [array[0]  for array in self.CellMatrix]
        self.ArrayValues = [array[1:] for array in self.CellMatrix]

        self.NameCheck = all([re.search('^[a-zA-Z]\w*$', NAME)  for NAME in self.ArrayNames])
        if self.NameCheck:
            aNames = [' <array name="{}"> '.format(name) for name in self.ArrayNames]
            aValues = [' '.join(['<data expr="{}"/>'.format(data) for data in arr] + [' </array> ']) for arr in self.ArrayValues]
            #print(aValues)
            ListOfArrays = [names+value for (names,value) in zip(aNames,aValues)]
            FinalText = ' '.join(ListOfArrays)
            self.ans = FinalText.replace("&amp;",'')
        else:
            print('Array Name Error')
            self.FinalLabel.configure(text='Array Name Error. View names (blue in the Test Table)', bg='red')

    def CopyableArray(self):    # copies array to clipboard
        self.ArrayGen()
        if self.NameCheck:
            self.Print2clip(self.ans)

            # Adds label to note that array is in clipboard
            self.FinalLabel.configure(text="#{}: An array has been copied to the clipboard. Paste it into the TDX file.".format(self.index), bg=self.UI_Settings.ColorText)
            self.index += 1

    def InsertArray(self):      # inserts array into file
        self.ArrayGen()

        if self.NameCheck:
            PreUsedNames = [str(name) for name in self.ArrayNames if name.lower() in self.master.DISINTEGRATE.UsedNames]
            TF = len(PreUsedNames)>0
            if TF:
                self.DATA = (TF, "The names below are already used in the TDX file. Pick new array names\r{}".format(PreUsedNames))
                self.FinalLabel.configure(text="The names below are already used in the TDX file. Pick new names\r{}".format(PreUsedNames), bg='red', justify=tk.LEFT)
            else:
                self.EditText = self.InputText[:]
                self.AddObjects('array')

                #*** creates FinalText with the inserted array
                self.FinalText = re.sub('(<objects>)',r'\1\r {} \r'.format(self.ans), self.EditText, count=1, flags = re.DOTALL|re.IGNORECASE)
                self.DATA = (TF, self.FinalText)
                # Passes edited self.FinalText to parent class, to update all UI Tabs
                self.master.Update_TDX_File(self.FinalText)


                # Adds label to note that table is in TDX file
                self.FinalLabel.configure(text="#{}: Array(s) added to the TDX file.".format(self.index), bg=self.UI_Settings.ColorText)
                self.index += 1
                print('Commit: InsertArray')

    ### Tables
    def TableGen(self):     # generates table from entered text
        # splits table by row and then by tabs (or whatever is selected in OptionMenuValueSet)
        self.Text_2_Matrix()


        # Uses function "cell2()" to wrap each cell in XML tags
        wrapped_cells = [' '.join([self.cell2(CELL) for CELL in row]) for row in self.CellMatrix]

        # ans: joins all cells into rows and then all rows into a table.
        header = '<table rows="{}" cols="{}" borderstyle="color" cellborderstyle="color" color="clNone">'.format(self.Rows_Length,max([len(XXX) for XXX in self.CellMatrix]))

        ans = ' '.join([' <row> ' + CELL + ' </row> ' for CELL in wrapped_cells])
        self.ans = header + ans + '</table>'

    def CopyableTable(self):    # copies table to clipboard
        self.TableGen()
        self.Print2clip(self.ans)

        # Adds label to note that table is in clipboard
        self.FinalLabel.configure(text="#{}: A table has been copied to the clipboard. Paste it into the TDX file.".format(self.index), bg=self.UI_Settings.ColorText)
        self.index += 1

    def InsertTable(self):      # inserts table into TDX file at selected step
        self.TableGen()

        Step_for_Table = self.ListedVar.get()
        self.FinalText = re.sub('(step name="{}".*?rvxml.*?document stringtags="0">.*?)(</document>)'.format(Step_for_Table),r'\1\r {} \r\2\r'.format(self.ans), self.InputText, flags = re.DOTALL|re.IGNORECASE)

        # Passes edited self.FinalText to parent class, to update all UI Tabs
        self.master.Update_TDX_File(self.FinalText)
        self.FinalLabel.configure(text="#{}: A Table has added to the TDX file in ({}).".format(self.index, Step_for_Table), bg=self.UI_Settings.ColorText)
        print('Commit: InsertTable in ({})'.format(Step_for_Table))


    ### Data Tables
    def DTgen(self, DTname='DTgen001'):
        # splits table by row and then by tabs (or whatever is selected in OptionMenuValueSet)
        self.Text_2_Matrix()

        CellMatrix = zip(*self.CellMatrix)

        DT = ' '.join([" <columns> \r <column>" + ' '.join(['<item value="{}"/>'.format(cell) for cell in row]) + "</column> \r </columns> " for row in CellMatrix])
        self.DT = ' <datatable name="{}" tooltiptext=""> '.format(DTname) + DT + ' </datatable> '

    def CopyableDT(self):    # copies DT to clipboard
        self.DTgenNameCopy = 'DTgen{}'.format(str(random.randint(1,999)).zfill(3))
        self.DTgen(self.DTgenNameCopy)
        self.Print2clip(self.DT)

        # Adds label to note that table is in clipboard
        self.FinalLabel.configure(text="#{}: A Data Table has been copied to the clipboard. Paste it into the TDX file.".format(self.index), bg=self.UI_Settings.ColorText)
        self.InfoLabel2.configure(text='The copyable data table name is "{}"'.format(self.DTgenNameCopy))
        self.index += 1

    def GetDTname(self):
        DTnumbers = [re.findall("(?<=DTgen)(\d+)", NAME)[0] for NAME in self.DTnames]
        if len(DTnumbers)==0:
            self.DTname = 'DTgen1'
        else:
            self.DTname = 'DTgen{}'.format(max([int(XXX) for XXX in DTnumbers])+1)

    def InsertDT(self):
        self.GetDTname()
        self.DTgen(self.DTname)

        self.EditText = self.InputText[:]
        self.AddObjects('datatable')

        self.FinalText = re.sub('(<objects>)',r'\1\r {} \r'.format(self.DT), self.EditText, flags = re.DOTALL|re.IGNORECASE)
        # Passes edited self.FinalText to parent class, to update all UI Tabs
        self.master.Update_TDX_File(self.FinalText)
        self.FinalLabel.configure(
            text="#{}: A Data Table has added to the TDX file.".format(self.index, self.ListedVar.get()), 
            bg=self.UI_Settings.ColorText)
        self.InfoLabel2.configure(text='The inserted data table name is "{}"'.format(self.DTname))

        print('Commit: InsertDT')


class DataGen(tk.Frame):
    'Defines and launches DataGen UI in DataGen-Tab (plus data creation/editing methods)'
    #ERROR Separate UI from calculations
    def __init__(self, master, top_master, InputText, SELF_SETTINGS, *args, **kw):
        tk.Frame.__init__(self, master, *args, **kw)
        self.master     = master
        self.top_master = top_master
        self.InputText  = InputText
        self.UI_Settings = SELF_SETTINGS

        self.master.bind_class("Text","<Control-a>", self.selectall)    # enables select_all, 
        self.ActiveAddress = r"C:\Users\GEX\Desktop"                    # sets initial TDX file location
        self.CurrentError  = True                                       # ensures error checks will be started
    
        self.SetupMainWindow()
        self.GridMainWindow()
        self.SetupWindow_Toggled()
        self.ClearErrors()              # hides errors until needed

        self.columnconfigure(0, weight=100)
        self.rowconfigure(   5, weight=100)



    ### UI methods
    def SetupMainWindow(self):            # Creates main UI window
        ### Creates and places Main regions
        self.Window_DataEntry, self.Window_Buttons, self.Window_ButtonX, self.Window_Errors, self.Window_Toggled = [tk.Canvas(self, bd=0, highlightthickness=0, relief='ridge', bg=self.UI_Settings.ColorBack1) for N in range(5)]
        self.AllEnter = tk.Text(self, undo=True)
        self.configure(bg=self.UI_Settings.ColorBack1)

        self.Window_Toggled_Color = 'light yellow'
        self.Window_Toggled.configure(bg=self.Window_Toggled_Color)

        self.Window_DataEntry.grid(row=0, column=0, sticky=tk.NSEW, pady=0, ipadx=10, rowspan=9)
        self.Window_ButtonX.grid(  row=0, column=9, sticky=tk.EW + tk.N)
        self.Window_Toggled.grid(  row=1, column=0, sticky=tk.NSEW, ipady=0, padx=0, columnspan=10)
        self.Window_Errors.grid(   row=5, column=9, sticky=tk.EW + tk.N)
        self.Window_Buttons.grid(  row=6, column=9, sticky=tk.EW + tk.S)
        self.AllEnter.grid(        row=5, column=0, sticky=tk.NSEW, pady=5, padx=5, rowspan=2)


        ### 
        [self.Window_DataEntry.columnconfigure( col, weight=10) for col in range(8)]
        self.Window_Buttons.columnconfigure(      0, weight=10)
        self.Window_ButtonX.columnconfigure(      0, weight=10)

        # buttons
        self.OpenTDXButton      = tk.Button(self.Window_ButtonX, text="Commit:\rAdd Variables to TDX", bg=self.UI_Settings.ColorCommit, command=self.AddVariables, bd=5, relief="ridge")
        self.Toggle_button      = tk.Button(self.Window_ButtonX, text="Toggle: Data Generator", bg=self.Window_Toggled_Color, command=self.Toggle)

        self.TEST_button        = tk.Button(self.Window_Buttons, text="TEST", bg=self.UI_Settings.ColorTest, command=self.TEST)
        self.Summary_button     = tk.Button(self.Window_Buttons, text="Review\rVariables", bg=self.UI_Settings.ColorTest, command=self.DisplaySummary)
        self.copyable_button    = tk.Button(self.Window_Buttons, text="Copy Variables\rto Clipboard", bg=self.UI_Settings.ColorCopy, command=self.CopyAble)
        self.Clear_button       = tk.Button(self.Window_Buttons, text="Clear Data", bg=self.UI_Settings.ColorClear, command=self.ClearData)





        # data entry and their labels
        self.NameStemLabel      = tk.Label(self.Window_DataEntry, text='Name Stem\r(a-Z)', bg=self.UI_Settings.ColorBack1)
        self.NameStemEntry      = tk.Entry(self.Window_DataEntry, bg=self.UI_Settings.ColorInput)
        self.NameStemEntry.insert(tk.END, 'vData')

        self.CommentLabel       = tk.Label(self.Window_DataEntry, text='Comment\r(for all)', bg=self.UI_Settings.ColorBack1)
        self.CommentEntry       = tk.Entry(self.Window_DataEntry, bg=self.UI_Settings.ColorInput)

        self.Type               = tk.StringVar(self.Window_DataEntry)
        self.Type.set('real' )
        self.TypeEntry          = tk.OptionMenu(self.Window_DataEntry, self.Type, *('int','real'))
        self.TypeEntry.configure(bg=self.UI_Settings.ColorInputFL)
        self.TypeLabel          = tk.Label(self.Window_DataEntry, text='Type\r(Integer/Real)', bg=self.UI_Settings.ColorBack1)

        self.FormatLabel        = tk.Label(self.Window_DataEntry, text='Format\r ', bg=self.UI_Settings.ColorBack1)
        self.FormatEntry        = tk.Entry(self.Window_DataEntry, bg=self.UI_Settings.ColorInput)
        self.FormatEntry.insert(tk.END, '#.#')

        self.Round              = tk.IntVar(self.Window_DataEntry)
        self.Round.set(-1) 
        self.RoundEntry         = tk.OptionMenu(self.Window_DataEntry, self.Round, *(range(-9,10)))
        self.RoundEntry.configure(bg=self.UI_Settings.ColorInputFL)
        self.RoundLabel         = tk.Label(self.Window_DataEntry, text='Rounding\r(for min/max)', bg=self.UI_Settings.ColorBack1)

        self.PercentLabel       = tk.Label(self.Window_DataEntry, text=u'Set \u00B1Delta\rX=value, N=index', bg=self.UI_Settings.ColorBack1)
        self.PercentEntry       = tk.Entry(self.Window_DataEntry, bg=self.UI_Settings.ColorInput)
        self.PercentEntry.insert(tk.END, 'X*.01')

        self.Order              = tk.StringVar(self.Window_DataEntry)
        self.Order.set('input' )
        self.OrderEntry         = tk.OptionMenu(self.Window_DataEntry, self.Order, *('input','reverse','ascending','descending','bell', 'random'))
        self.OrderEntry.configure(bg=self.UI_Settings.ColorInputFL)
        self.OrderLabel         = tk.Label(self.Window_DataEntry, text='Var Order\r ', bg=self.UI_Settings.ColorBack1)

        self.DeltaMinEntry      = tk.Entry(self.Window_DataEntry, bg=self.UI_Settings.ColorInput)
        self.DeltaMinLabel      = tk.Label(self.Window_DataEntry, text=u'Minimum\r\u00B1Delta', bg=self.UI_Settings.ColorBack1)
        self.DeltaMinEntry.insert(tk.END, '0')

        # error labels
        self.ErrorLabel         = tk.Label(self.Window_Errors, bg='red', padx=2, pady=2, text='*** Fix errors ***')
        self.ErrorLabelA        = tk.Label(self.Window_Errors, bg='red', padx=2, pady=2, text='* Data must be numbers')
        self.ErrorLabelB        = tk.Label(self.Window_Errors, bg='red', padx=2, pady=2, text='* Format must have more decimal\rplaces than rounding\r*Add #/- to format\r*Or increase rounding')
        self.ErrorLabelC        = tk.Label(self.Window_Errors, bg='red', padx=2, pady=2, text='* Integers must have rounding>=0\r*increase rounding')
        self.ErrorLabelD        = tk.Label(self.Window_Errors, bg='red', padx=2, pady=2, text='* Enter At least one value')
        self.ErrorLabelE        = tk.Label(self.Window_Errors, bg='yellow', padx=2, pady=2, text='* Min=Max')
        self.ErrorLabelF        = tk.Label(self.Window_Errors, bg='red', padx=2, pady=2, text='* Variable name\ris already used')
        self.ErrorLabelX        = tk.Label(self.Window_Errors, padx=2, pady=2, text='', bg=self.UI_Settings.ColorBack1)
        self.ShiftErrorLabel    = tk.Label(self.Window_Errors, bg='red', text='Standard deviation of data\nmust be non-zero')

    def GridMainWindow(self):
        # .grid() locations for UI
        self.OpenTDXButton.grid(    row=0, padx=3, pady=6, ipady=2, sticky=tk.NSEW)
        self.Toggle_button.grid(    row=1, padx=3, pady=0, ipady=2, sticky=tk.NSEW)

        self.TEST_button.grid(      row=2, padx=3, pady=3, ipady=4, sticky=tk.NSEW)
        self.Summary_button.grid(   row=3, padx=3, pady=3, ipady=2, sticky=tk.NSEW)
        self.copyable_button.grid(  row=4, padx=3, pady=3, ipady=2, sticky=tk.NSEW)
        self.Clear_button.grid(     row=5, padx=3, pady=6, ipady=2, sticky=tk.NSEW)


        self.ErrorLabel.grid(       row=0, sticky=tk.NSEW)
        self.ErrorLabelA.grid(      row=1, sticky=tk.NSEW)
        self.ErrorLabelB.grid(      row=2, sticky=tk.NSEW)
        self.ErrorLabelC.grid(      row=3, sticky=tk.NSEW)
        self.ErrorLabelD.grid(      row=4, sticky=tk.NSEW)
        self.ErrorLabelE.grid(      row=5, sticky=tk.NSEW)
        self.ErrorLabelF.grid(      row=6, sticky=tk.NSEW)
        self.ErrorLabelX.grid(      row=7, sticky=tk.NSEW)

        self.NameStemLabel.grid(    row=0, column=0, ipady=1, sticky=tk.NSEW, ipadx=2)
        self.NameStemEntry.grid(    row=1, column=0, ipady=1, sticky=tk.NSEW, padx=2, ipadx=20)
        self.TypeLabel.grid(        row=0, column=1, ipady=1, sticky=tk.NSEW, ipadx=25)
        self.TypeEntry.grid(        row=1, column=1, ipady=5, sticky=tk.NSEW, padx=2)
        self.FormatLabel.grid(      row=0, column=2, ipady=1, sticky=tk.NSEW)
        self.FormatEntry.grid(      row=1, column=2, ipady=1, sticky=tk.NSEW, padx=2)
        self.RoundLabel.grid(       row=0, column=3, ipady=1, sticky=tk.NSEW, ipadx=10)
        self.RoundEntry.grid(       row=1, column=3, ipady=5, sticky=tk.NSEW, padx=2)
        self.PercentLabel.grid(     row=0, column=4, ipady=1, sticky=tk.NSEW)
        self.PercentEntry.grid(     row=1, column=4, ipady=1, sticky=tk.NSEW, padx=2)
        self.DeltaMinLabel.grid(    row=0, column=5, ipady=1, sticky=tk.NSEW)
        self.DeltaMinEntry.grid(    row=1, column=5, ipady=1, sticky=tk.NSEW, padx=2)
        self.CommentLabel.grid(     row=0, column=6, ipady=1, sticky=tk.NSEW, ipadx=40)
        self.CommentEntry.grid(     row=1, column=6, ipady=1, sticky=tk.NSEW, padx=2)
        self.OrderLabel.grid(       row=0, column=7, ipady=1, sticky=tk.NSEW, ipadx=40)
        self.OrderEntry.grid(       row=1, column=7, ipady=1, sticky=tk.NSEW, padx=2)

    def SetupWindow_Toggled(self):         # Creates UI to be toggled by the method Toggle(self)
        label_frame_text = ['Sample','Equation','Probability/Cumulative density','Shift data','Binned data']

        self.ToggledSample, self.ToggledEQ, self.ToggledXDF, self.ToggledScale, self.ToggledBin = toggle_x = [tk.LabelFrame(self.Window_Toggled, text=LABEL, relief='ridge', bd=2, bg=self.UI_Settings.ColorBack1) for LABEL in label_frame_text] #,  bd=0, highlightthickness=0, relief='ridge'

        pad_toggle = 2
        self.ToggledSample.grid( row=10, column=1, 
            padx=(2*pad_toggle, pad_toggle), 
            pady=(2*pad_toggle, int(pad_toggle/2)), 
            sticky=tk.NSEW)
        self.ToggledEQ.grid( row=12, column=1, 
            padx=(2*pad_toggle, pad_toggle), 
            pady=(0, pad_toggle), 
            sticky=tk.NSEW)
        self.ToggledXDF.grid( row=14, column=1,
            padx=(2*pad_toggle, pad_toggle),
            pady=(2*pad_toggle, 2*pad_toggle), 
            sticky=tk.NSEW)

        self.ToggledScale.grid(  row=10, column=3,
            padx=(pad_toggle, 3*pad_toggle),
            pady=(2*pad_toggle, pad_toggle), 
            sticky=tk.NSEW,
            rowspan=3)
        self.ToggledBin.grid( row=14, column=3,
            padx=(pad_toggle, 3*pad_toggle),
            pady=(2*pad_toggle, 2*pad_toggle), 
            sticky=tk.NSEW)

        [self.Window_Toggled.columnconfigure(col, weight=10) for col in [1,3]]
        [self.ToggledSample.columnconfigure( col, weight=10) for col in range(1,5)]
        [self.ToggledEQ.columnconfigure(     col, weight=10) for col in (1,2)]
        [self.ToggledXDF.columnconfigure(    col, weight=10) for col in (1,2)]
        [self.ToggledScale.columnconfigure(  col, weight=10) for col in (5,6)]


        ###
        self.ToggleData = False
        self.StaticDistributionInfo()
        # Activate each area
        self.disSample()
        self.disEQ()
        self.disShift()
        self.disXDF()
        self.disBin()

    def disSample(self):                   # Displays/Creates sample region
        ### sample
        # buttons
        self.Add_button = tk.Button(self.ToggledSample, text="Add\rSample Data", bg=self.UI_Settings.ColorEdit, command=self.AddSampleData)
        # inputs
        self.DistributionInput  = tk.Entry(self.ToggledSample, bg=self.UI_Settings.ColorInput)
        self.Distribution       = tk.StringVar(self.ToggledSample)
        self.Distribution.set('binomial distribution')
        self.DistributionEntry  = tk.OptionMenu(self.ToggledSample, self.Distribution, *(self.DistText), command=self.UpdatePopup)
        self.DistributionEntry.configure(bg=self.UI_Settings.ColorInput)
        # labels
        self.DistributionLabel1 = tk.Label(self.ToggledSample, text='Draw samples from a ', anchor=tk.E, bg=self.UI_Settings.ColorBack1)
        self.DistributionLabel3 = tk.Label(self.ToggledSample, anchor=tk.E, bg=self.UI_Settings.ColorBack1)
        self.UpdatePopup('force event')     # calls UpdatePopup() to add text to DistributionLabel3
        self.DistributionLabel4 = tk.Label(self.ToggledSample, text=' )', anchor=tk.W, bg=self.UI_Settings.ColorBack1)


        self.Add_button.grid(        row=0, column=0, rowspan=2, padx=5, pady=5, sticky=tk.NSEW)
        self.DistributionLabel1.grid(row=0, column=1, sticky=tk.NSEW)
        self.DistributionLabel3.grid(row=1, column=1, ipadx=5, sticky=tk.NSEW)
        self.DistributionEntry.grid( row=0, column=2, columnspan=5, padx=5, pady=5, sticky=tk.NSEW)
        self.DistributionInput.grid( row=1, column=2, columnspan=5, ipadx=50, padx=5, sticky=tk.NSEW)
        self.DistributionLabel4.grid(row=1, column=6, sticky=tk.NSEW)

    def disEQ(self):
        ### equations
        # buttons
        self.Add_eq_button = tk.Button(self.ToggledEQ, text="Add N values\rfrom Equation", bg=self.UI_Settings.ColorEdit, command=self.AddEqData)
        # inputs
        self.EqInput  = tk.Entry(self.ToggledEQ, bg=self.UI_Settings.ColorInput)
        self.EqInput.insert(0, 'X**2')
        self.NumInput  = tk.Entry(self.ToggledEQ, bg=self.UI_Settings.ColorInput)
        self.NumInput.insert(0, '10')
        # labels
        self.EQLabel1 = tk.Label(self.ToggledEQ, text='N_max', bg=self.UI_Settings.ColorBack1)
        self.EQLabel2 = tk.Label(self.ToggledEQ, text=u'EQ for (0\u2264X\u003CN_max)', bg=self.UI_Settings.ColorBack1)


        self.Add_eq_button.grid(     row=1, column=0, rowspan=2, sticky=tk.NSEW, padx=5, pady=5)
        self.EQLabel1.grid(          row=1, column=1, sticky=tk.EW)
        self.EQLabel2.grid(          row=1, column=2, sticky=tk.EW)
        self.NumInput.grid(          row=2, column=1, sticky=tk.EW, padx=10)

    def disShift(self):
        ### shift EQ
        # buttons
        self.Shift_button = tk.Button(self.ToggledScale, text="Scale values\rby equation", bg=self.UI_Settings.ColorEdit, command=self.ShiftEquation)
        # inputs
        self.EqInput2  = tk.Entry(self.ToggledScale, bg=self.UI_Settings.ColorInput)
        self.EqInput2.insert(0, 'X*2+0')
        # labels
        self.ShiftLabel1 = tk.Label(self.ToggledScale, text='Shift equation: X=value, N=index', bg=self.UI_Settings.ColorBack1)

        ### shift Mean/SD
        # buttons
        self.ShiftMean_button = tk.Button(self.ToggledScale, text="Scale values\rby Mean/SD", bg=self.UI_Settings.ColorEdit, command=self.ShiftMeanSD)
        # inputs
        self.MeanInput  = tk.Entry(self.ToggledScale, bg=self.UI_Settings.ColorInput)
        self.MeanInput.insert(0, '100')
        self.SDevInput  = tk.Entry(self.ToggledScale, bg=self.UI_Settings.ColorInput)
        self.SDevInput.insert(0, '10')
        # labels
        self.ShiftMeanLabel  = tk.Label(self.ToggledScale, text='New Mean', bg=self.UI_Settings.ColorBack1)
        self.ShiftSDevLabel  = tk.Label(self.ToggledScale, text='New Standard Deviation', bg=self.UI_Settings.ColorBack1)

        ### shift Min/Max
        # buttons
        self.ShiftMax_button = tk.Button(self.ToggledScale, text="Scale values\rby Min/Max", bg=self.UI_Settings.ColorEdit, command=self.ShiftMinMax)
        # inputs
        self.MinInput  = tk.Entry(self.ToggledScale, bg=self.UI_Settings.ColorInput)
        self.MinInput.insert(0, '0')
        self.MaxInput  = tk.Entry(self.ToggledScale, bg=self.UI_Settings.ColorInput)
        self.MaxInput.insert(0, '10')
        # labels
        self.ShiftMinLabel  = tk.Label(self.ToggledScale, text='New Min', bg=self.UI_Settings.ColorBack1)
        self.ShiftMaxLabel  = tk.Label(self.ToggledScale, text='New Max', bg=self.UI_Settings.ColorBack1)


        [self.ToggledScale.rowconfigure(     row, weight=10) for row in range(10)]


        #
        self.ShiftLabel1.grid(       row=1, column=5, columnspan=2, sticky=tk.EW)
        self.Shift_button.grid(      row=1, column=4, rowspan=2, ipadx=15, sticky=tk.EW, padx=5, pady=5)

        self.ShiftMean_button.grid(  row=5, column=4, rowspan=2, sticky=tk.EW, padx=5, pady=5)
        self.ShiftMeanLabel.grid(    row=5, column=5, sticky=tk.EW)
        self.ShiftSDevLabel.grid(    row=5, column=6, sticky=tk.EW)
        self.MeanInput.grid(         row=6, column=5, sticky=tk.EW, padx=2, pady=2)
        self.SDevInput.grid(         row=6, column=6, sticky=tk.EW, padx=2, pady=2)


        self.ShiftMax_button.grid(   row=8, column=4, rowspan=2, sticky=tk.EW, padx=5, pady=5)
        self.MinInput.grid(          row=9, column=5, sticky=tk.EW, padx=2, pady=2)
        self.ShiftMinLabel.grid(     row=8, column=5, sticky=tk.EW)
        self.MaxInput.grid(          row=9, column=6, sticky=tk.EW, padx=2, pady=2)
        self.ShiftMaxLabel.grid(     row=8, column=6, sticky=tk.EW)

        self.EqInput.grid(           row=2, column=2, sticky=tk.EW, padx=10)
        self.EqInput2.grid(          row=2, column=5, ipadx=20, columnspan=2, sticky=tk.EW, padx=2, pady=2)

    def disBin(self):
        self.Bin_button = tk.Button(self.ToggledBin, text="Binned Data\rGenerator Popup", bg=self.UI_Settings.ColorEdit, command=self.ShowBinnedData)
        self.Bin_button.grid(sticky=tk.NSEW, padx=5, pady=5, ipady=10)

    def disXDF(self):
        ### Density function

        self.Add_CDF_Button = tk.Button(self.ToggledXDF, text="Generate CDF Data", bg=self.UI_Settings.ColorEdit, command=self.GenerateCDFdata)
        self.Add_PDF_Button = tk.Button(self.ToggledXDF, text="Generate PDF Data", bg=self.UI_Settings.ColorEdit, command=self.GeneratePDFdata)

        self.CDFeqInput = tk.Entry(self.ToggledXDF, bg=self.UI_Settings.ColorInput)
        self.CDFeqInput.insert(0, 'X**3')
        self.CDFeqLabel = tk.Label(self.ToggledXDF, text='CDF Equation: ', bg=self.UI_Settings.ColorBack1)

        self.PDFeqInput = tk.Entry(self.ToggledXDF, bg=self.UI_Settings.ColorInput)       # (1/[SD*@rt{2*pi}]) * e^(-[x-Mean]^2/[2*SD^2])
        self.PDFeqInput.insert(0, 'math.exp(-((X+0)**2)/2.0)')  # '(1.0/(2*math.pi)**.5) * math.exp(-(X**2)/2.0)' : SD=1, Mean=0
        self.PDFeqLabel = tk.Label(self.ToggledXDF, text='PDF Equation: ', bg=self.UI_Settings.ColorBack1)

        self.XDFnInput = tk.Entry(self.ToggledXDF, bg=self.UI_Settings.ColorInput)
        self.XDFnInput.insert(0, '20')
        self.XDFnLabel = tk.Label(self.ToggledXDF, text='N values: ', bg=self.UI_Settings.ColorBack1)

        self.LimitAInput = tk.Entry(self.ToggledXDF, bg=self.UI_Settings.ColorInput)
        self.LimitAInput.insert(0, '-10')

        self.LimitBInput = tk.Entry(self.ToggledXDF, bg=self.UI_Settings.ColorInput)
        self.LimitBInput.insert(0, '10')

        self.LimitABLabel = tk.Label(self.ToggledXDF, text='Min/Max X', bg=self.UI_Settings.ColorBack1)

        self.ExactEdge = tk.IntVar()
        self.ExactEdgeCheck = tk.Checkbutton(self.ToggledXDF, highlightcolor='green', selectcolor="white", text='Exact Edges', variable=self.ExactEdge, bg=self.UI_Settings.ColorBack1)

        #
        self.ExactEdgeCheck.grid(    row=1, column=0, ipadx=10, ipady=2, sticky=tk.W)
        self.XDFnLabel.grid(         row=1, column=1, sticky=tk.E)
        self.XDFnInput.grid(         row=1, column=2, sticky=tk.EW, padx=2, pady=2)
        self.LimitAInput.grid(       row=2, column=1, sticky=tk.EW, padx=2, pady=2)
        self.LimitABLabel.grid(      row=2, column=0, sticky=tk.EW)
        self.LimitBInput.grid(       row=2, column=2, sticky=tk.EW, padx=2, pady=2)
        self.Add_CDF_Button.grid(    row=5, column=0, sticky=tk.EW, padx=5, pady=5)
        self.CDFeqInput.grid(        row=5, column=1, sticky=tk.NSEW, columnspan=2, padx=2, pady=2, ipadx=130)
        self.Add_PDF_Button.grid(    row=6, column=0, sticky=tk.EW, padx=5, pady=5)
        self.PDFeqInput.grid(        row=6, column=1, sticky=tk.NSEW, columnspan=2, padx=2, pady=2)

    def Toggle(self):                       # Toggles region to select a distribution and create/shift data
        if self.ToggleData:
            self.Window_Toggled.grid()
        else:
            self.Window_Toggled.grid_remove()

        self.ToggleData = not self.ToggleData

    def DisplaySummary(self):               # Displays values, statistics, and bar chart
        self.CalcData()

        self.Popup_Digits = self.ROUND

        print('self.Popup_Digits', self.Popup_Digits)

        if self.CurrentError:
            print('Show Error')
            self.ErrorLabel.grid()
        else:
            NumberOfValues = len(self.data)
            if NumberOfValues < 100:
                self.MaxPerColumn = min(20,len(self.data))
            else:
                self.MaxPerColumn = (NumberOfValues+1)//1

            self.PopupGen = tk.Toplevel(self.master)
            self.PopupGen.rowconfigure(   0, weight=1)
            self.PopupGen.columnconfigure(0, weight=1)

            w, h = max(121,self.master.winfo_screenwidth()), max(200,self.master.winfo_screenheight())
            self.PopupGen.geometry("%dx%d+70+70" % (w-170, h-270))

            self.frame1R = VerticalScrolledFrame(self.PopupGen)
            self.frame1R.grid(row=0, column=10, ipady=10, ipadx=10, sticky=tk.NSEW)

            self.frame1L = tk.Label(self.PopupGen)
            self.frame1L.grid(row=0, column=0, sticky=tk.NSEW)

            self.Popup = tk.LabelFrame(self.frame1R.interior, text='Data Values')
            self.Popup.pack(side=tk.RIGHT, fill=tk.BOTH, expand=tk.TRUE)


            Sumry = tk.LabelFrame(self.frame1L, text='Summary Statistics')
            Sumry.grid(row=0, column=0, padx=5, pady=5)

            self.Histo = tk.Canvas(self.frame1L)
            self.Histo.grid(row=1, column=0, sticky=tk.NSEW)


            self.frame1L.rowconfigure(    1, weight=1)
            self.frame1L.columnconfigure( 0, weight=1)


            self.HistoButtonLabel = tk.Button(self.Histo, text="Update Histogram [3,300]", bg='sky blue', command=self.CreateHistogram)
            self.HistoBinInput    = tk.Entry(self.Histo, bg=self.UI_Settings.ColorInput)
            self.HistoBinInput.insert(0, '10')          # bin initial input
            self.HistoBinInput.bind('<Return>', self.CreateHistogram)


            self.HistoButtonLabel.grid(row=0, column=1, sticky=tk.EW)
            self.HistoBinInput.grid(   row=0, column=0, sticky=tk.EW)


            MIN, MAX = min(self.data),max(self.data)
            print('MIN, MAX', MIN, MAX)
            Quartiles = (numpy.percentile(self.data, [25, 50, 75])).tolist()
            Quartiles_Text = '[{}, {}, {}]'.format(*[self.Text_Round(Q,self.Popup_Digits) for Q in Quartiles])
            Stats_label_data = (('# Values', NumberOfValues), 
                               ('Min, Max'   , '[{}, {}]'.format(self.Text_Round(MIN,self.Popup_Digits), self.Text_Round(MAX,self.Popup_Digits))), 
                               ('Range'      , self.Text_Round(MAX-MIN,self.Popup_Digits)), 
                               ( 'Quartiles' , Quartiles_Text), 
                               ('IQR'        , self.Text_Round(Quartiles[2]-Quartiles[0],self.Popup_Digits)), 
                               ('Mean'       , self.Text_Round(numpy.mean(self.data),self.Popup_Digits)), 
                               ('Std Dev'    , self.Text_Round(numpy.std(self.data),self.Popup_Digits)))

            #print(Stats_label_data)
            Stats_label, Stats_data = zip(*Stats_label_data)

            self.StatisticLabels  = [tk.Label(Sumry, text='{}: '.format(datum)) for datum in Stats_label]
            self.StatisticValues  = [tk.Label(Sumry, text='{}'.format(datum)) for datum in Stats_data]


            [Label.grid(row=101+index, column=10, columnspan=30, sticky=tk.E) for index, Label in enumerate(self.StatisticLabels)]
            [Value.grid(row=101+index, column=41, columnspan=30, sticky=tk.W) for index, Value in enumerate(self.StatisticValues)]
            self.CreateHistogram(initial=True)
            self.Create_Popup()

    def Text_Round(self, VAL, DIG):
        DIG = max(0,DIG)
        Rounded_Return = '{V:0<{D}.{D}f}'.format(V=VAL, D=DIG)
        return Rounded_Return

    def CreateHistogram(self, initial=False):
        NumberOfBins = self.HistoBinInput.get()
        if not (2<float(self.HistoBinInput.get())<301):
            print ('The Number Of Bins entered is not an integer from 3 to 300: {X}'.format(X=self.HistoBinInput.get()))
        NumberOfBins = min(300,max(3,int(float(NumberOfBins))))

        if initial:
            pass
        else:
            try:
                print('Forget Histogram: Try')
                self.Bars._G_.grid_forget()
            except:
                print('Forget Histogram: Error')

        bin_values, bin_edges = numpy.histogram(self.data, bins=NumberOfBins)
        print('bin_values={}'.format(bin_values))

        self.Bars = BarGraph(MASTER=self.master, parent=self.Histo, y=bin_values, TITLEx='{} bins'.format(NumberOfBins))
        self.Bars._G_.grid(row=10, column=0, columnspan=2, sticky=tk.NSEW)

        self.Histo.columnconfigure(0, weight=10)
        self.Histo.rowconfigure(  10, weight=10)

    def Create_Popup(self,Max_Length=1000):
        Data_Length = len(self.minimums)
        LENGTH = min(Data_Length, Max_Length)
        # Column headers (and seperators) for the right side of the "Variable Review" popup
        for index, title in  enumerate(['index','Input','Min','Max','Delta2']):
            PADx = 5 if title=='index' else 0
            DataColumnTitle = tk.Label(self.Popup, text=title, relief=tk.RAISED, underline=0)
            DataColumnTitle.grid(column=101+10*index, row=99, sticky=tk.NSEW,  padx=PADx)


        # Labels/Data for "Data Values" in right side of the "Variable Review" popup
        Data_4_Labels = [self.Text_Round(X, self.Popup_Digits) for X in self.data[:LENGTH]]
        self.DataLabels = [tk.Label(self.Popup, text='{:}'.format(datum), relief=tk.GROOVE) for datum in Data_4_Labels]
        self.indexLabels= [tk.Label(self.Popup, text='{}:'.format(datum), relief=tk.SUNKEN, anchor=tk.E) for datum in range(1,1+LENGTH)]
        self.MinLabels  = [tk.Label(self.Popup, text=datum, relief=tk.GROOVE) for datum in self.minimums[:LENGTH]]
        self.MaxLabels  = [tk.Label(self.Popup, text=datum, relief=tk.GROOVE) for datum in self.maximums[:LENGTH]]
        self.DelLabels  = [tk.Label(self.Popup, text=datum, relief=tk.GROOVE) for datum in self.DeltaCalc[:LENGTH]]

        [labelI.grid(row=101+index, column=101, sticky=tk.NSEW,  padx=5) for index, labelI in enumerate(self.indexLabels)]
        [labelD.grid(row=101+index, column=111, sticky=tk.NSEW, ipadx=5) for index, labelD in enumerate(self.DataLabels)]
        [Min.grid(   row=101+index, column=121, sticky=tk.NSEW, ipadx=5) for index, Min    in enumerate(self.MinLabels)]
        [Max.grid(   row=101+index, column=131, sticky=tk.NSEW, ipadx=5) for index, Max    in enumerate(self.MaxLabels)]
        [Del.grid(   row=101+index, column=141, sticky=tk.NSEW, ipadx=5) for index, Del    in enumerate(self.DelLabels)]

        if LENGTH==Max_Length:
            length_note = tk.Label(self.Popup, bg='red', text='Only displaying {}/{} data values'.format(LENGTH, Data_Length))
            length_note.grid(row=0, column=101, columnspan=41, sticky=tk.W)

        [label.configure(bg='red') for label, data in zip(self.DelLabels,self.DeltaCalc) if float(data) == 0]
        self.ErrorLabel.grid_remove()

    ### Test and/or unused
    def TEST(self):                         # Prints testing data to console
        self.CalcData()

        print ('--- New print ---')
        print ('DecPlacesFormat={}'.format(len(re.findall('#|-',self.FormatEntry.get().split('.')[-1]))))
        print ('self.data={}'.format(self.data))
        print ('self.DELTA={}'.format(self.DELTA))
        print ('self.minCalc={}'.format(self.minCalc))
        print ('self.maxCalc={}'.format(self.maxCalc))
        print ('self.DeltaCalc={}'.format(self.DeltaCalc))

    def MathInput(self,inputString):   # not implemented,      
        #should convert common math syntax to python math module syntax
        '''
        math.exp(x)
        math.log(x[, base])

        math.cos(x)
        math.sin(x)
        math.tan(x)

        math.degrees(x)
        math.radians(x)

        math.pi
        math.e

        .replace('N_max','{MAX}').replace('n_max','{MAX}').replace('N','{N}')

        (?<!\w)e(?!\w)
        '''
        pass

    ### Utility methods
    def InsertData(self, Data):             # inserts [generated Data] into main entry box
        Data = '\n' + '\n'.join([str(XXX) for XXX in Data]) + '\n'
        self.AllEnter.insert(tk.END,Data)

    def ClearData(self):                    # Clears main data entry box
        self.AllEnter.delete('1.0', tk.END)
        self.ClearErrors()

    def ClearErrors(self):                  # Clears error displays on main window
        self.ErrorLabel.grid_remove()
        self.ErrorLabelA.grid_remove()
        self.ErrorLabelB.grid_remove()
        self.ErrorLabelC.grid_remove()
        self.ErrorLabelD.grid_remove()
        self.ErrorLabelE.grid_remove()
        self.ErrorLabelF.grid_remove()
        self.ShiftErrorLabel.grid_remove()

    def selectall(self, event):             # allows ctrl+a (select all) to work in text box
        event.widget.tag_add("sel","1.0","end")

    def Print2clip(self,text):              # Print to clipboard (general)
        clippy = tk.Tk()
        clippy.withdraw()
        clippy.clipboard_clear()
        clippy.clipboard_append(text)
        clippy.update()
        clippy.destroy()

    def CopyAble(self):                     # Actually adds new .TDX variables to clipboard
        self.CreateVariableData()
        self.ArrayGen()

        self.Print2clip(self.FinalArr + self.createdVariableText)

    def UpdatePopup(self, event):           # Updates sample distribution input info to match selected distribution
        self.DistributionLabel3.configure(text='inputs: ' + self.DistInput[self.DistText.index(self.Distribution.get())]+ ' = (')

    def StaticDistributionInfo(self):       # Distributions for generating data
        DistData = [('beta', '(a, b[, size])', 'Beta distribution'), ('binomial', '(n, p[, size])', 'binomial distribution'), ('chisquare', '(df[, size])', 'chi-square distribution'), ('dirichlet', '(alpha[, size])', 'Dirichlet distribution'), ('exponential', '([scale, size])', 'exponential distribution'), ('f', '(dfnum, dfden[, size])', 'F distribution'), ('gamma', '(shape[, scale, size])', 'Gamma distribution'), ('geometric', '(p[, size])', 'geometric distribution'), ('gumbel', '([loc, scale, size])', 'Gumbel distribution'), ('hypergeometric', '(ngood, nbad, nsample[, size])', 'Hypergeometric distribution'), ('laplace', '([loc, scale, size])', 'Laplace with specified location (or mean) and scale (decay)'), ('logistic', '([loc, scale, size])', 'logistic distribution'), ('lognormal', '([mean, sigma, size])', 'log-normal distribution'), ('logseries', '(p[, size])', 'logarithmic series distribution'), ('multinomial', '(n, pvals[, size])', 'multinomial distribution'), ('multivariate_normal', '(mean, cov[, size, ...)', 'multivariate normal distribution'), ('negative_binomial', '(n, p[, size])', 'negative binomial distribution'), ('noncentral_chisquare', '(df, nonc[, size])', 'noncentral chi-square distribution'), ('noncentral_f', '(dfnum, dfden, nonc[, size])', 'noncentral F distribution'), ('normal', '([loc, scale, size])', 'normal (Gaussian) distribution'), ('pareto', '(a[, size])', 'Pareto II or Lomax distribution with specified shape'), ('poisson', '([lam, size])', 'Poisson distribution'), ('power', '(a[, size])', 'power distribution in [0, 1] with positive exponent a - 1'), ('rayleigh', '([scale, size])', 'Rayleigh distribution'), ('standard_cauchy', '([size])', 'standard Cauchy distribution with mode = 0'), ('standard_exponential', '([size])', 'standard exponential distribution'), ('standard_gamma', '(shape[, size])', 'standard Gamma distribution'), ('standard_normal', '([size])', 'standard Normal distribution (mean=0, stdev=1)'), ('standard_t', '(df[, size])', "standard Student's t distribution with df degrees of freedom"), ('triangular', '(left, mode, right[, size])', 'triangular distribution over the interval [left, right]'), ('uniform', '([low, high, size])', 'uniform distribution'), ('vonmises', '(mu, kappa[, size])', 'von Mises distribution'), ('wald', '(mean, scale[, size])', 'Wald, or inverse Gaussian, distribution'), ('weibull', '(a[, size])', 'Weibull distribution'), ('zipf', '(a[, size])', 'Zipf distribution')]

        self.Distributions, self.DistInput, self.DistText = zip(*DistData)

    ### Add data methods
    def AddSampleData(self):                # generates data based on selected distribution
        dist = self.Distributions[self.DistText.index(self.Distribution.get())]
        input = self.DistributionInput.get()

        NewData = eval('numpy.random.{}({})'.format(dist,input))
        NewData = NewData.tolist()

        print('Sample Data', NewData)
        self.InsertData(NewData)

    def AddEqData(self):                    # generates data based on equation
        Equation = self.EqInput.get()
        Equation = Equation.replace('X','{X}')
        Equation = Equation.replace('N_max','{MAX}')
        self.Nmax = int(self.NumInput.get())

        newData = [eval(Equation.format(X=index, MAX=self.Nmax)) for index in range(self.Nmax)]
        print('Equation Data', newData)
        self.InsertData(newData)

    ### Probability/Cumulative Distribution Function methods
    def GetXDF(self, xDivisions=1000):  # Creates x-values evenly distributed along x-axis
        self.N = int(self.XDFnInput.get())
        Limits = [eval(self.LimitAInput.get()), eval(self.LimitBInput.get())]

        self.deltaX     = float(Limits[1]-Limits[0])/xDivisions           # delta per xDivision
        self.xValues    = [Limits[0] + self.deltaX*X for X in range(xDivisions+1)]
        #print ('xValues',len(self.xValues),self.xValues)

    def PDFtoCDF(self):                     # Generates a CDF from given PDF
        ''' Returns approximation of the integral for each XVAL in (xValues)
        CDFyValues[index] = integral(PDFfunction) on [xValues[0], xValues[index]]
        '''
        self.GetXDF()

        PDFfunction = self.PDFeqInput.get()
        PDFfunction = PDFfunction.replace('X','({X})')

        print('PDFfunction: {}'.format(PDFfunction))
        PDFyValues  = [eval(PDFfunction.format(X=XVAL)) for XVAL in self.xValues]
        assert min(PDFyValues) >= 0, 'Probability Density (PDFfunction) must be non-negative'
        print('PDFyValues {}'.format(PDFyValues),   'width={}'.format(self.deltaX)   )

        CDFyValues = [0]
        for index, __ in enumerate(PDFyValues[:-1]):               # uses Trapezoidal rule to approximate areas
            CDFyValues.append(CDFyValues[-1] + self.deltaX*(PDFyValues[index]+PDFyValues[index+1])/2.0)

        self.CDFyValues = CDFyValues
        print('CDFyValues (x,y) from PDFtoCDF',len(CDFyValues),zip(self.xValues,CDFyValues))

    def GetCDF(self):                       # Generates CDF
        self.GetXDF()
        CDFfunction = self.CDFeqInput.get()
        CDFfunction = CDFfunction.replace('X','{X}')
        print('CDFfunction: {}'.format(CDFfunction))

        CDFyValues = [eval(CDFfunction.format(X=XVAL)) for XVAL in self.xValues]
        print('CDFyValues (x,y) from GetCDF',len(CDFyValues),list(zip(self.xValues,CDFyValues)))
        assert CDFyValues==sorted(CDFyValues), 'Cumulative Density (CDFfunction) must have a non-negative slope'
        self.CDFyValues = CDFyValues

    def Interpolate(self,dataX, dataY, vX_input):    # Interpolates vY_output at each vX_input between points (dataX,dataY)
        '''Interpolates the (vY_output) of each value in (vX_input), between the given (X,Y) points of (dataX,dataY)
        Uses min/max (dataX) and respective (dataY) coordinates to create a line for extrapolating
        '''
        # Duplicate (dataX) values will use the first/last associated (dataY) value for before/after ranges'
        assert len(dataX) == len(dataY),      'Unpaired (X,Y) data. "len(dataX)" should equal "len(dataY)"'

        dataX, dataY = zip(*sorted(zip(dataX, dataY)))          # sorts data_X/Y based on dataX
        dataX, dataY, vX_input = [[float(VALUE) for VALUE in LIST] for LIST in (dataX, dataY, vX_input)]

        vY_output = []
        for vX_value in vX_input:                               # loops through (vX_input) to create (vY_output)
            if vX_value in dataX:                               # avoids calculation if (vX_value) is a given x-coordinate
                vY_output.append(dataY[dataX.index(vX_value)])
            else:
                if vX_value > dataX[-1]:                        # sets IndexA/B to be first/last indices (extrapolate +)
                    IndexA = 0
                    IndexB = len(dataX)-1
                elif vX_value < dataX[0]:                       # sets IndexA/B to be first/last indices (extrapolate -)
                    IndexA = 0
                    IndexB = len(dataX)-1
                else:                                           # sets IndexA/B so vX_value is between A/B (interpolate)
                    for index, v in enumerate(dataX):
                        if v > vX_value:
                            IndexB = index
                            break
                    IndexA = IndexB - 1

                vYmin = dataY[IndexA]                                                   # Minimum y-value for bin
                vYper = 1.0*(vX_value-dataX[IndexA])/(dataX[IndexB]-dataX[IndexA])      # Vertical/Horizontal % into bin
                vYdel = dataY[IndexB]-dataY[IndexA]                                     # Vertical deltaY for bin
                vY_output.append(vYmin + vYper*vYdel)           # Y = y_1 + [(X - x_1)/(x_2 - x_1)] * (y_2 - y_1)

        return vY_output

    def GetDistributedXcoordinates(self):      ### Creates x-values to match the distribution
        # if(ExactEdge,   [min/max xValues] == [given Limits],   min/max shifted in by (delta/2) )
        # for N=3, Limits=[0,6] ---> if(ExactEdge,   [0,3,6],   [1,3,5])
        if self.ExactEdge.get():
            deltaDen = self.N-1
            delta    = float(self.CDFyValues[-1]-self.CDFyValues[0]) / deltaDen
            Base     = self.CDFyValues[0]
        else:
            deltaDen = self.N
            delta    = float(self.CDFyValues[-1]-self.CDFyValues[0]) / deltaDen
            Base     = self.CDFyValues[0] + delta/2.0

        #print('height={}'.format(delta))
        distributedYcoordinates = [Base + delta*Y for Y in range(self.N)]

        # Note: X and Y are intentionally reversed as Interpolate() assumes to interpolate y-values given x
        distributedXcoordinates = self.Interpolate(dataX=self.CDFyValues, dataY=self.xValues, vX_input=distributedYcoordinates)
        self.InsertData(distributedXcoordinates)

    def GeneratePDFdata(self):              # Calls PDF and then GetDistributedXcoordinates method
        self.PDFtoCDF()
        self.GetDistributedXcoordinates()

    def GenerateCDFdata(self):              # Calls CDF and then GetDistributedXcoordinates method
        self.GetCDF()
        self.GetDistributedXcoordinates()

    ### Binned data methods
    def CreateBinnedData(self):
        self.a    = float(self.BinMinInput.get())
        self.b    = float(self.BinMaxInput.get())
        bins      =   int(self.BinBinInput.get())
        subs      =   int(self.BinSubInput.get())
        data      =   int(self.BinDatInput.get())
        EQ        =      (self.BinEq1Input.get()).replace('X','{X}')
        used_bins = bins*subs

        self.BinXvalues  = [self.a+(self.b-self.a)*(1.0*N/used_bins)      for N in range(used_bins)]
        self.BinX2values = [self.a+(self.b-self.a)*(1.0*N/bins)           for N in range(bins)]

        
        if subs==1:
            self.BinYgen = [eval(EQ.format(X=val)) for val in self.BinXvalues]
        else:
            self.BinYgen = [eval(EQ.format(X=val)) for val in self.BinX2values]
            self.BinYgen = [val for val in self.BinYgen for __ in range(subs)]


        BinGenSum = sum(self.BinYgen)
        self.BinYdec = [(1.0*data*val/BinGenSum) for val in self.BinYgen]

        self.BinYint   = [round(val,0) for val in self.BinYdec]
        self.BinYDelta = [d-i for d,i in zip(self.BinYdec, self.BinYint)]

        self.Indices = []
        if self.BoxVar.get():       # ensures number of values is equal to input: BinIntSum == data
            BinIntSum = sum(self.BinYint)
            print('pre while-loop')
            while BinIntSum!=data:
                print('delta=',self.BinYDelta)
                self.BinYDelta = [d-i for d,i in zip(self.BinYdec, self.BinYint)]
                if BinIntSum<data:
                    self.BinYint[self.BinYDelta.index(max(self.BinYDelta))] += 1
                elif BinIntSum>data:
                    self.BinY0Delta = [Delta if Yint0!=0 else 99 for Delta, Yint0 in zip(self.BinYDelta, self.BinYint)]
                    self.Indices.append(self.BinY0Delta.index(min(self.BinY0Delta)))
                    self.BinYint[self.Indices[0]] -= 1
                BinIntSum = sum(self.BinYint)

        self.BinYvalues = [int(XXX) for XXX in self.BinYint]

    def ShowBinnedData(self):
        self.PopupBinGen = tk.Toplevel()
        self.PopupBinGen.rowconfigure(   0, weight=1)
        self.PopupBinGen.columnconfigure(0, weight=1)

        self.frame2 = VerticalScrolledFrame(self.PopupBinGen)
        self.frame2.grid(row=0, column=0, rowspan=20, ipady=200, sticky=tk.NSEW)

        tk.Grid.rowconfigure(   self.frame2, 0, weight=1)
        tk.Grid.columnconfigure(self.frame2, 0, weight=1)



        self.PopupBin = tk.Canvas(self.frame2.interior)
        self.PopupBin.pack(fill=tk.BOTH, expand=tk.TRUE)

        self.BinDataSmooth               = tk.StringVar(self.PopupBin)
        self.BinDataSmooth.set('random' )
        self.BinDataSmoothEntry          = tk.OptionMenu(self.PopupBin, self.BinDataSmooth, *('random','even'))
        self.BinDataSmoothEntry.configure(bg=self.UI_Settings.ColorInputFL)
        self.BinDataSmoothLabel          = tk.Label(self.PopupBin, text='Type: ')


        self.Add_Bin_Button              = tk.Button(self.PopupBin, text="Add Binned Data", bg='green', command=self.AddBinnedData)
        self.Update_Bin_Button           = tk.Button(self.PopupBin, text="Update Bin Counts (below) from equation (above)", bg='sky blue', command=self.UpdateBinData)

        self.BinEq1Input = tk.Entry(self.PopupBin, bg=self.UI_Settings.ColorInput)
        self.BinEq1Input.insert(0, 'X')
        self.BinEq1Label = tk.Label(self.PopupBin, text='PDF/Bin Equation: ')


        self.BinBinInput = tk.Entry(self.PopupBin, bg=self.UI_Settings.ColorInput)
        self.BinBinInput.insert(0, '5')
        self.BinBinLabel = tk.Label(self.PopupBin, text='Number of bins')

        self.BinSubInput = tk.Entry(self.PopupBin, bg=self.UI_Settings.ColorInput)
        self.BinSubInput.insert(0, '1')
        self.BinSubLabel = tk.Label(self.PopupBin, text='Number of sub-intervals')

        self.BinMinInput = tk.Entry(self.PopupBin, bg=self.UI_Settings.ColorInput)
        self.BinMinInput.insert(0, '0')
        self.BinMinLabel = tk.Label(self.PopupBin, text='Min cutoff')

        self.BinMaxInput = tk.Entry(self.PopupBin, bg=self.UI_Settings.ColorInput)
        self.BinMaxInput.insert(0, '2')
        self.BinMaxLabel = tk.Label(self.PopupBin, text='Max Cutoff')

        self.BinDatInput = tk.Entry(self.PopupBin, bg=self.UI_Settings.ColorInput)
        self.BinDatInput.insert(0, '20')
        self.BinDatLabel = tk.Label(self.PopupBin, text='Number of data values')

        self.BinXLabel   = tk.Label(self.PopupBin, text='Bin Domain')
        self.BinYLabel   = tk.Label(self.PopupBin, text='Bin Count')

        self.BoxVar = tk.IntVar()
        self.BoxToggle = tk.Checkbutton(self.PopupBin, bg='light sea green', highlightcolor='green', selectcolor="white", text='Ensure # of values', variable=self.BoxVar)
        self.BoxToggle.invoke()



        self.Add_Bin_Button.grid(    row=205, column=10, columnspan=3, sticky=tk.NSEW)
        self.Update_Bin_Button.grid( row=101, column=10, columnspan=3, sticky=tk.NSEW)

        self.BinDataSmoothEntry.grid(row=202, column=11, columnspan=3, sticky=tk.NSEW)
        self.BinDataSmoothLabel.grid(row=202, column=10, columnspan=1, sticky=tk.E)

        #[ttk.Separator(self.PopupBin).grid(row=ROW, columnspan=1000, pady=5, sticky=tk.EW) for ROW in [99,100,199,200,300]]


        self.BinBinLabel.grid(   row=10, column=10, sticky=tk.EW)
        self.BinBinInput.grid(   row=11, column=10, sticky=tk.EW)

        self.BinSubLabel.grid(   row=10, column=11, sticky=tk.E)
        self.BinSubInput.grid(   row=11, column=11, sticky=tk.EW)

        self.BinDatLabel.grid(   row=10, column=12, sticky=tk.E)
        self.BinDatInput.grid(   row=11, column=12, sticky=tk.EW)
        self.BoxToggle.grid(     row=12, column=12, sticky=tk.EW)


        self.BinMinLabel.grid(   row=12, column=10, sticky=tk.EW)
        self.BinMinInput.grid(   row=13, column=10, sticky=tk.EW)

        self.BinMaxLabel.grid(   row=12, column=11, sticky=tk.EW)
        self.BinMaxInput.grid(   row=13, column=11, sticky=tk.EW)


        self.BinEq1Input.grid(   row=14, column=11, columnspan=3, sticky=tk.EW)
        self.BinEq1Label.grid(   row=14, column=10, sticky=tk.E)

        self.BinXLabel.grid(     row=305, column=10, sticky=tk.EW)
        self.BinYLabel.grid(     row=305, column=11, sticky=tk.EW)

        self.UpdateBinData()

    def UpdateBinData(self):
        self.CreateBinnedData()
        try:
            [L.grid_remove() for L in self.BinSetLabels]
            [L.grid_remove() for L in self.BinSetInput]
        except:
            print('Initial run (or Bin Data clearing error)')

        self.Length = len(self.BinXvalues)
        self.Domain = self.BinXvalues + [float(self.BinMaxInput.get())]

        self.BinSetLabels = [tk.Label(self.PopupBin, text='[{A},{B}]'.format(A=self.Domain[index], B=self.Domain[index+1])) for index in range(self.Length)]
        self.BinSetInput  = [tk.Entry(self.PopupBin, bg=self.UI_Settings.ColorInput) for index in range(self.Length)]
        [Input.insert(0, Y) for Input, Y in zip(self.BinSetInput, self.BinYvalues)]

        [X.grid( row=310+index, column=10, sticky=tk.EW) for index, X in enumerate(self.BinSetLabels)]
        [Y.grid( row=310+index, column=11, sticky=tk.EW) for index, Y in enumerate(self.BinSetInput)]
        [self.BinSetInput[index].configure(bg='light sea green') for index in self.Indices]

    def AddBinnedData(self):
        self.UpdateBinData()

        if self.BinDataSmooth.get() == 'random':
            NewData = [numpy.random.uniform(low=self.BinXvalues[index], high=self.BinXvalues[index+1], size=self.BinYvalues[index]) for index in range(self.Length-1)]
        elif self.BinDataSmooth.get() == 'even':
            NewData = []
            for BinNumber, (LimA,LimB,Count) in enumerate(zip(self.BinXvalues, self.BinXvalues[1:]+[float(self.BinMaxInput.get())], self.BinYvalues)):
                if Count==0:
                    NewRowData = []
                else:
                    DELTA = float(LimB-LimA)/(Count)
                    NewRowData = [LimA+DELTA/2+DELTA*index for index in range(Count)]
                NewData.append(NewRowData)


        print ('NewData = {}'.format(NewData))
        NewData = [item for sublist in NewData for item in sublist]

        self.InsertData(NewData)

    ### Shift/Scale methods
    def ShiftEquation(self):
        self.GetData()
        #self.AllEnter.edit_modified(arg=False)  # (no effect) tries to combine delete/paste into one undo action
        self.ClearData()
        Equation = self.EqInput2.get()
        Equation = Equation.replace('N','{N}')
        Equation = Equation.replace('X','{X}')

        NewData = [eval(Equation.format(X=datum, N=index)) for index, datum in enumerate(self.data)]
        print('Shifted EQ Data', Equation, list(zip(self.data, NewData)))
        self.InsertData(NewData)

    def ShiftMeanSD(self):
        self.GetData()
        MeanX, Std = float(numpy.mean(self.data)), float(numpy.std(self.data))
        NewMean, NewStd = float(eval(self.MeanInput.get())), float(eval(self.SDevInput.get()))
        if Std == 0:
            self.ShiftErrorLabel.grid(row=361, sticky=tk.EW)
        else:
            self.GetData()
            self.ClearData()
            self.ShiftErrorLabel.grid_remove()


            print('Mean asd', MeanX)
            NewData = [((float(datum)-MeanX)*(NewStd/Std)+NewMean) for index, datum in enumerate(self.data)]
            print('Shifted Mean/SD Data', (MeanX, Std), list(zip(self.data, NewData)))
            self.InsertData(NewData)

    def ShiftMinMax(self):
        self.GetData()
        Min   , Max    = min(self.data), max(self.data)
        NewMin, NewMax = float(self.MinInput.get()) , float(self.MaxInput.get())

        if Min==Max or NewMin==NewMax:
            self.ShiftErrorLabel.grid(row=361, sticky=tk.EW)
        else:
            self.ClearData()
            NewData = [(datum-Min)*(1.0*(NewMax-NewMin)/(Max-Min)) + NewMin for datum in self.data]
            print('Shifted Min/Max Data', list(zip(self.data, NewData)))
            self.InsertData(NewData)
            self.ShiftErrorLabel.grid_remove()

    ### Large entry box to min/max data methods
    def GetData(self):                  # generates list of numeric values from large entry box
        text = self.AllEnter.get("1.0",'end')
        text = re.sub('[\n\r\s]+$','',text)

        self.dataInit = text.split('\n')
        self.dataInit = [x for x in self.dataInit if x!='']
        self.OrderType = self.Order.get()

        try:                # tries to convert string data to numerical float; and if float=int, then integers
            self.dataInit = [float(XXX) for XXX in self.dataInit]
            try:
                DataInt = [int(XXX) for XXX in self.dataInit]
                if all([a==b for a,b in zip(DataInt,self.dataInit)]):
                    self.dataInit = DataInt
            except:
                pass

                # orders data based on selected OrderType
            if self.OrderType == 'input':
                self.data = self.dataInit[:]
            elif self.OrderType == 'reverse':
                self.data = self.dataInit[::-1]
            elif self.OrderType == 'ascending':
                self.data = sorted(self.dataInit)
            elif self.OrderType == 'descending':
                self.data = sorted(self.dataInit, reverse=True)
            elif self.OrderType == 'random':
                self.data = self.dataInit[:]
                numpy.random.shuffle(self.data)
            elif self.OrderType == 'bell':
                dataSorted = sorted(self.dataInit)
                self.data = dataSorted[0::2] + dataSorted[1::2][::-1]

            self.ErrorLabelA.grid_remove()
        except:
            self.ErrorLabelA.grid()
            self.data = []

    def CalcData(self):                 # calculates min and max for each value in self.data
        self.GetData()

        ### user input values, in order
        # self.NameStemEntry.get()
        # self.Type.get()
        # self.FormatEntry.get()
        # self.Round.get()
        # self.PercentEntry.get()
        # self.DeltaMinEntry.get()
        # self.CommentEntry.get()
        # self.Order.get()

        self.ROUND = ROUND = int(-self.Round.get())
        DIGITS = max(0,ROUND)
        PercentENTRY = self.PercentEntry.get()
        FormatEntryText = self.FormatEntry.get()
        if '.' in FormatEntryText:
            DecPlacesFormat = len(re.findall('#|-',FormatEntryText.split('.')[-1]))
        else:
            DecPlacesFormat = 0
        try:
            self.DeltaMin = float(self.DeltaMinEntry.get())
        except:
            self.DeltaMin = 0

        self.ErrorRounding = (ROUND>0 and DecPlacesFormat < DIGITS)
        self.ErrorIntRound = (ROUND>0 and self.Type.get() == 'int')
        self.CurrentError = True

        if self.ErrorRounding:
            self.ErrorLabelB.grid()
            self.ErrorLabel.grid()
        elif self.ErrorIntRound:
            self.ErrorLabelC.grid()
            self.ErrorLabel.grid()
        else:
            self.ErrorLabelB.grid_remove()
            self.ErrorLabelC.grid_remove()
            try:
                self.DELTA    = [max(abs(self.DeltaMin),abs(eval(PercentENTRY))) for N,X in enumerate(self.data)]

                self.minCalc  = [round(X-delta,ROUND) for delta, X in zip(self.DELTA,self.data)]
                self.maxCalc  = [round(X+delta,ROUND) for delta, X in zip(self.DELTA,self.data)]

                self.minimums = ['{number:.{digits}f}'.format(number=MinValue, digits=DIGITS) for MinValue in self.minCalc]
                self.maximums = ['{number:.{digits}f}'.format(number=MaxValue, digits=DIGITS) for MaxValue in self.maxCalc]

                if self.Type.get() == 'int' or ROUND < 0:
                    self.minimums = [int(math.ceil(X)) for X in self.minCalc]
                    self.maximums = [int(math.floor(X)) for X in self.maxCalc]



                self.DeltaCalc = [round(b-a,ROUND) for a,b in zip(self.minCalc,self.maxCalc)]
                self.ErrorLabel.grid()
                if len(self.DeltaCalc) == 0:
                    self.ErrorLabelD.grid()
                    self.ErrorLabelE.grid_remove()
                elif min(self.DeltaCalc) == 0:
                    self.ErrorLabelD.grid_remove()
                    self.ErrorLabelE.grid()
                    self.ErrorLabelE.configure(text='Min=Max for {n} Var{s}'.format(n=sum([X==0 for X in self.DeltaCalc]), s='' if sum==1 else 's'))
                    self.ErrorLabel.grid_remove()
                    self.CurrentError = False
                else:
                    self.ErrorLabelD.grid_remove()
                    self.ErrorLabelE.grid_remove()
                    self.ErrorLabel.grid_remove()
                    self.CurrentError = False

            except:
                self.CurrentError = True
                print('CalcData error')
                self.ErrorLabel.grid()

    ### .TDX methods
    def CreateVariableData(self):       # generates .TDX variables from self.data
        self.createdVariableText = ''
        self.CalcData()

        if self.CurrentError:
            self.ErrorLabel.grid()
            self.createdVariableText = ''
        elif len(self.data) == 0:
            self.ErrorLabel.grid()
        else:
            varString = '<var name="{}" common="1" comments="{}" type="{}" format="{}">  <constraint>    <limits>      <limit type="ge">{}</limit>      <limit type="le">{}</limit>    </limits>  </constraint>  <initvalues> <expr>{}</expr> </initvalues>  </var>'

            self.NameStem = re.sub('\W', '', self.NameStemEntry.get())
            Zeros = int(math.ceil(math.log(len(self.data)+1,10)))
            self.NameWsuffixes = [self.NameStem + str(item).zfill(Zeros) for item in range(1,len(self.data)+1)]



            CurrentComment = self.CommentEntry.get()
            CurrentType = self.Type.get()
            CurrentFormat = self.FormatEntry.get()
            ROUND = int(-self.Round.get())


            createdVariableList = [varString.format(NAME, CurrentComment, CurrentType, CurrentFormat, MIN, MAX, round(INIT,ROUND)) for NAME, MIN, MAX, INIT in zip(*(self.NameWsuffixes,self.minimums,self.maximums, self.data))]

            self.createdVariableText = ' '.join(createdVariableList)

    def ArrayGen(self):                 # generates .TDX array of variables created from self.data
        aName   = ' <array name="{}"> '.format(self.NameStem)
        aValues = ' '.join(['<data expr="~{}"/>'.format(data) for data in self.NameWsuffixes])

        self.FinalArr = aName + aValues + ' </array> '

    def AddObjects(self,OBJECT):        # closes open "object/" tag, and adds OBJECT to list of meta_name="objects"
        if self.EditText.find('<objects>') == -1:
            self.EditText = self.EditText.replace('<objects/>',' <objects>  </objects>')

        if self.EditText.find('<meta name="objects" value') == -1:
            self.EditText = self.EditText.replace('<toolbuttons names="', '<meta name="objects" value="{}"/> \r <toolbuttons names="'.format(OBJECT))
        else:
            FileObjects = re.findall('(?<=\<meta name\=\"objects\" value\=\")[\w,]+"',self.InputText)[0]
            NewObjects  = FileObjects.split(',')
            NewObjects  = set(NewObjects)
            NewObjects.add(OBJECT)
            NewObjects  = (',').join(list(NewObjects))
            self.EditText = self.EditText.replace('<meta name="objects" value="{}"'.format(FileObjects),'<meta name="objects" value="{}'.format(NewObjects))

    def AddVariables(self):                # Actually edits the .TDX file, after checks
        self.CreateVariableData()


        SetOfUsedName = set([x.lower() for x in re.findall('(?<=name=\")\w+(?=\W)',self.InputText)])
        SetOfAddNames = set([x.lower() for x in self.NameWsuffixes + [self.NameStem]])

        NumberOfNames = len(SetOfUsedName)
        NumberOfAdded = len(SetOfAddNames)
        NumberOfCombo = len(SetOfUsedName | SetOfAddNames)

        if NumberOfCombo == NumberOfNames + NumberOfAdded:
            self.ErrorLabelF.grid_remove()
            self.EditText = self.InputText[:]
            self.AddObjects('var')
            self.ArrayGen()

            self.FinalText = re.sub('(<objects>)',r'\1\r {} \r'.format(self.FinalArr + self.createdVariableText), self.EditText, count=1, flags = re.DOTALL|re.IGNORECASE)

            # Passes edited self.FinalText to parent class, to update all UI Tabs
            self.top_master.Update_TDX_File(self.FinalText)
            self.InputText = self.FinalText
            self.NameStemEntry.configure(bg='white')
            print("Commit: AddVariables")

        else:
            self.ErrorLabelF.grid()
            self.NameStemEntry.configure(bg='red')

    def Update_TDX(self, New_File):
        self.InputText = New_File


def SP_Cleaner(TEXT, RemovableInteractions, SPtype=False):
    'Defines and launches SP Cleaner UI in tab_SP (plus SP creation/cleaning methods)'
    Text = TEXT
    # Remove unused Interactions
    for N in RemovableInteractions:
        Text = re.sub('<(\w+) name="{}".*?/>[(\\r)(\\n)]*'.format(N), '', Text, flags=re.IGNORECASE)
    for N in RemovableInteractions:
        Text = re.sub('<(?P<quote>\w+) name="{}".*?</(?P=quote)>'.format(N), '', Text, flags=re.IGNORECASE|re.DOTALL)

    if SPtype:
        #*** Deletes all feedbacks
        feedback = "(?<=<window name=\"feedback\">).+?(?=</window>)"
        Text = re.sub(feedback, " ", Text, 1, flags=re.DOTALL)

        #*** Deletes all feedbacks links from steps
        msg = "(<msgwrong).+?(/msgwrong>)"
        Text = re.sub(msg, " ", Text, flags=re.DOTALL)


        #*** Removes import_from_excercise
        Text = Text.replace('import="1"', "")


        #*** Pauses all steps
        str_pause = 'pause="1"'
        steps = "(<step name=)(\"\w+\")([^u]*?)>"
        stepsP = "\g<1>\g<2>\g<3> {}>".format(str_pause)
        Text = re.sub(steps, stepsP, Text, flags=re.IGNORECASE)

        #*** Un-pauses all popups
        Position   = Text.find('<window name="feedback')
        Text = Text[:Position] + Text[Position:].replace(str_pause,"")

        #*** Un-pauses 1st step and last step
        Text = Text.replace(str_pause,"",1)
        Text = Text[::-1].replace(str_pause[::-1],"",1)[::-1]

        #*** Set type as SP
        Text = Text.replace(
            '<meta name="problemtype" value="guided"/>', 
            '<meta name="problemtype" value="sample"/>')
        Text = Text.replace(
            '<meta name="problemtype" value="exercise"/>', 
            '<meta name="problemtype" value="sample"/>')

        #*** sets each variable to its initial value
        VARtext = re.findall('<var name=.*?/var>', Text, flags=re.DOTALL)
        print('VarText', VARtext)

        # list of "initial" values, for each variable
        VarInitial = [re.findall('(?:<initvalues>(\r|\n|\\n|\\r)*<expr>)([^/]+?)(?:</expr>)',V, flags=re.DOTALL) for V in VARtext]
        print('VarInitial', VarInitial)
        VarInitial = [XXX[0][1] if len(XXX)>0 else False for XXX in VarInitial]
        print('VarInitial', VarInitial)

        # list of "inclusion" values, for each variable
        VarIncText   = [''.join(re.findall('(?<=<incl>)(.+?)(?=</incl>)', V, flags=re.DOTALL)) for V in VARtext]
        VarInclusion = [        re.findall('(?<=<expr>)(.+?)(?=</expr>)', V, flags=re.DOTALL)  for V in VarIncText]

        # deletes current "inclusion" values
        ShouldDelete = [Vinit and len(Vincl)!=1 for Vinit,Vincl in zip(VarInitial,VarInclusion)]
        NewVarText   = [re.sub('<incl>.*?</incl>','',TEXT, flags=re.DOTALL) if DELETE else TEXT \
                        for TEXT, DELETE in zip(VARtext,ShouldDelete)]



        # adds "initial" value as "inclusion"
        NewVarText =   [re.sub('(?<=<constraint>)',
                        ' <incl> \r\n <expr>{}</expr> \r\n </incl> '.format(InitialV), 
                        TEXT, 
                        flags=re.DOTALL) \
                        if ADD else TEXT for (TEXT, InitialV, ADD) in zip(NewVarText,VarInitial,ShouldDelete)]

        #print('NewVarText', NewVarText)
        for A, B in zip(VARtext, NewVarText):
            Text = re.sub(re.escape(A),B,Text, flags=re.DOTALL)

    return (Text)


def Complete_Renamer(Input_Text, OLD_LIST_VAF, NEW_LIST_VAF, OLD_LIST_OTHER, NEW_LIST_OTHER):
    'Renames all items in a TDX file'
    TextNew = Input_Text

    # Sorts VAF lists based on OLD_List_VAF's name length (long to short)
    # This is necessary to match TDX interpretation (otherwise renaming ~x would affect ~x123 or ~xVar)
    Old_List_VAF, New_List_VAF = [list(x) for x in zip(*sorted(zip(OLD_LIST_VAF, NEW_LIST_VAF), key=lambda pair: len(pair[0]), reverse=True))]

    # Static search data
    NamePost = "(?=[\"<\.])"
    # Variables (in step text) use "data="; Collections use "enumvar=" and "object name="
    Name_Prefix_List = ["(?<=var name=\")","(?<=array name=\")","(?<=formula name=\")","(?<=data=\"\">)","(?<=enumvar=\")","(?<=<object name=\")"]

    ### Does replacement ###

    ### Replacement VAF: OLD->MID (MID used to avoid overwriting)
    MID_List_VAF = ['_ALPHA_{}_OMEGA_'.format(x) for x in Old_List_VAF]
    for old, mid in zip(Old_List_VAF, MID_List_VAF):
        for Name_PRE in Name_Prefix_List:
            #Error: could be optimized to only use actual Name_PRE (or ~) instead of trying all
            TextNew  = re.sub(Name_PRE + old + NamePost, mid, TextNew, flags = re.IGNORECASE)
        # Replaces variables references (with prefix "~")
        TextNew  = re.sub("(?<=\~)"+old, mid, TextNew, flags=re.IGNORECASE)

    ### Replacement Other: OLD->MID (MID used to avoid overwriting)
    MID_List_Other  = ['ALPHA_{}_OMEGA'.format(x) for x in OLD_LIST_OTHER]
    for old, mid  in zip(OLD_LIST_OTHER, MID_List_Other):
        TextNew = re.sub('(?<=(\"|\>)){}(?=(\"|\<))'.format(old), mid, TextNew, flags=re.IGNORECASE)


    ### Replacement VAF: MID->NEW
    for mid, new in zip(MID_List_VAF, New_List_VAF):
        TextNew     = re.sub(mid, new, TextNew, flags=re.IGNORECASE)

    ### Replacement Other: MID->NEW
    for mid, new in zip(MID_List_Other, NEW_LIST_OTHER):
        TextNew = re.sub('(?<=(\"|\>)){}(?=(\"|\<))'.format(mid), new, TextNew, flags=re.IGNORECASE)

    return TextNew


class FB_MultiPart(tk.Frame):
    'UI and methods for FB_MultiPart-Tab, adds feedbacks in TDX steps with multiple interactions'
    def __init__(self, master, ActualMaster, TEXT, STEPS, INTER_dict, SELF_SETTINGS, *args, **kw):
        tk.Frame.__init__(self, master, *args, **kw)
        self.master = master            # Should be .parent
        self.MASTERui = ActualMaster
        self.Initial_Text = TEXT
        self.Initial_Steps = STEPS
        self.Interactions_By_Step = INTER_dict
        self.MaxInteractions = 8     # limited by OptionsList(n)
        self.order = ['first', 'second', 'third', 'fourth', 'fifth', 'sixth', 'seventh', 'eighth']

        self.UI_Settings = SELF_SETTINGS

        self.configure(bg=self.UI_Settings.ColorBack1)
        self.region_upper = tk.LabelFrame(self, text='Settings', bg=self.UI_Settings.ColorBack1)
        self.region_lower = tk.LabelFrame(self, text='Feedback Input', bg=self.UI_Settings.ColorBack1)

        self.region_upper.grid(row=0, column=0, padx=5, pady=5, sticky=tk.NSEW)
        self.region_lower.grid(row=1, column=0, padx=5, pady=5, sticky=tk.NSEW)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        self.Setup_Number_of_Interactions()

        self.Setup_Buttons()
        self.Setup_Interactions_By_Step()
        self.Setup_Interactions_OptionMenu()
        self.Setup_Info_Labels()
        self.Setup_Grid_All()


    def Setup_Number_of_Interactions(self):
        # InteractionVar is set by drop down, and controls number of input boxes shown
        self.InteractionVar = tk.IntVar(self.region_upper)
        self.InteractionVar.set(2) 

        # Drop down and its label
        self.NumLabel = tk.Label(self.region_upper, text="# of interactions: ", bg=self.UI_Settings.ColorBack1)
        self.NumberInteractions = tk.OptionMenu(self.region_upper, 
                                            self.InteractionVar, 
                                            *(range(2,self.MaxInteractions+1)), 
                                            command=self.NumberEnter_SelectionEvent)
        self.NumberInteractions.configure(bg=self.UI_Settings.ColorEdit)

        self.Setup_Num_of_Inputs()


    def Setup_Num_of_Inputs(self):
        # generates input boxes for Name/Feedback
        self.InputName = [tk.Entry(self.region_lower, bg=self.UI_Settings.ColorInput) for index in range(self.MaxInteractions)]
        self.InputPart = [tk.Entry(self.region_lower, bg=self.UI_Settings.ColorInput) for index in range(self.MaxInteractions)]
        self.Reset_names()
        self.InputFeed = [tk.Entry(self.region_lower, bg=self.UI_Settings.ColorInput) for index in range(self.MaxInteractions)]

        commands_list_paste = [self.Paste_Button_Press_closure(index) for index in range(self.MaxInteractions)]
        self.LabelsInput = [tk.Button(self.region_lower, text='Input #{}'.format(index+1), command=CMD,  bg=self.UI_Settings.ColorCopy) for index, CMD in enumerate(commands_list_paste)]

        # displays appropriate number of input boxes (called each time "# of interactions drop down is edited)
        self.NumberEnter_SelectionEvent(self.region_upper)


    def Setup_Buttons(self):
        # buttons
        self.Add_FB_button  = tk.Button(self.region_upper, text="Commit:\rAdd Feedbacks",    bg=self.UI_Settings.ColorCommit, command=self.Add_Feedbacks, bd=5, relief="ridge")
        self.Reset_button   = tk.Button(self.region_lower, text="Reset Part Names", bg=self.UI_Settings.ColorClear, command=self.Reset_names)
        self.Test_FB_button = tk.Button(self.region_upper, text="Display sample",     bg=self.UI_Settings.ColorTest, command=self.Test_FB)

        ### 
        # Copyable buttons
        max_number_of_buttons = max([0,]+[len(X) for X in self.Interactions_By_Step.values()])
        if max_number_of_buttons>0:
            commands_list = [self.Copy_Button_Press_closure(index) for index in range(max_number_of_buttons)]
            self.Copy_Buttons = [tk.Button(self.region_upper, text="", bg=self.UI_Settings.ColorCopy, command=CMD) for CMD in commands_list]
        else:
            self.Copy_Buttons = []

    def Setup_Interactions_By_Step(self):
        # Interactions by step
        self.Step_Inter_Label = tk.Label(self.region_upper, bg=self.UI_Settings.ColorBack1)

        # entry boxes and their labels
        self.StepVar = tk.StringVar(self.master)
        self.StepLabel = tk.Label(self.region_upper, text="Step Name: ", bg=self.UI_Settings.ColorBack1)


        if len(self.Interactions_By_Step.keys())==0:
            StepsWithInter_text    = 'No interactions used in any step'
            StepsWithOneInter_text = ''
            self.multiple_interactions  = []
        else:
            self.multiple_interactions = [KEY for KEY in self.Interactions_By_Step.keys() if len(self.Interactions_By_Step[KEY])>1]
            self.multiple_interactions = [XXX for XXX in self.Initial_Steps if XXX in self.multiple_interactions] # orders steps

            single_interaction = [KEY for KEY in self.Interactions_By_Step.keys() if len(self.Interactions_By_Step[KEY])==1]
            single_interaction = [XXX for XXX in self.Initial_Steps if XXX in single_interaction] # orders steps

            StepsWithInter_text = 'Steps with one interaction: ({SINGLE})\nSteps with multiple interactions: ({MULTI})'.format(MULTI=r',  '.join(self.multiple_interactions), SINGLE=r',  '.join(single_interaction))


        self.StepsWithInter    = tk.Label(self.region_upper, text=StepsWithInter_text, bg=self.UI_Settings.ColorBack1, justify="left")


    def Setup_Interactions_OptionMenu(self):
        if len(self.Initial_Steps) != 0:
            self.Marked_Steps = ['**{}**'.format(NAME) if NAME in self.multiple_interactions else NAME for NAME in self.Initial_Steps]
            self.StepVar.set(self.Marked_Steps[0]) 
            self.StepEnter = tk.OptionMenu(self.region_upper, self.StepVar, *(self.Marked_Steps), command=self.StepEnter_SelectionEvent)
            self.StepEnter.config(state=tk.NORMAL, bg=self.UI_Settings.ColorEdit)
        else:
            self.Marked_Steps = ['']
            self.StepEnter = tk.OptionMenu(self.region_upper, self.StepVar, '')
            self.StepEnter.config(state=tk.DISABLED, bg=self.UI_Settings.ColorDisabled)


    def Setup_Info_Labels(self):
        self.PreLabel       = tk.Label(self.region_lower, text="Feedback before each -->", bg=self.UI_Settings.ColorBack1)
        self.PostLabel      = tk.Label(self.region_lower, text="Feedback after each -->", bg=self.UI_Settings.ColorBack1)
        self.PreEnter  = tk.Entry(self.region_lower, bg=self.UI_Settings.ColorInput)
        self.PostEnter = tk.Entry(self.region_lower, bg=self.UI_Settings.ColorInput)

        self.NameLabel      = tk.Label(self.region_lower, text="Input Name", bg=self.UI_Settings.ColorBack1)
        self.PartLabel      = tk.Label(self.region_lower, text="Part Name", bg=self.UI_Settings.ColorBack1)
        self.FeedLabel      = tk.Label(self.region_lower, text="Specific Feedback", bg=self.UI_Settings.ColorBack1)
        self.ErrLabel  = tk.Label(self.region_lower, text="", bg=self.UI_Settings.ColorBack1)


    def Setup_Grid_All(self):
        # .grid: upper region (buttons and drop downs)
        self.Add_FB_button.grid(         row=0, column=99, sticky=tk.EW)
        self.Test_FB_button.grid(        row=1, column=99, sticky=tk.EW)
        self.StepsWithInter.grid(   row=1, column=2, columnspan=9, sticky=tk.W)

        self.Step_Inter_Label.grid(row=2, column=0, columnspan=2, rowspan=9, sticky=tk.NS+tk.W)

        self.NumLabel.grid(          row=0, column=0, sticky=tk.E)
        self.NumberInteractions.grid(row=0, column=1, sticky=tk.W)
        self.StepLabel.grid(         row=1, column=0, sticky=tk.E)
        self.StepEnter.grid(         row=1, column=1, sticky=tk.W)

        Max_Buttons_Per_Row = 8
        [BUTTON_N.grid( row    = 2+index//Max_Buttons_Per_Row, 
                        column = index%Max_Buttons_Per_Row+2, 
                        sticky = tk.EW) for index, BUTTON_N in enumerate(self.Copy_Buttons)]
        self.region_upper.columnconfigure(90, weight=5)

        # .grid: middle row (entry/label for "Feedback before each")
        self.PreLabel.grid(row=10, column=0, columnspan=2, sticky=tk.E)
        self.PreEnter.grid(row=10, column=2, columnspan=8, sticky=tk.EW)

        # .grid: lower region (Labels for columns of entry boxes)
        self.NameLabel.grid(    row=100, column=1, sticky=tk.W)
        self.PartLabel.grid(    row=100, column=2, sticky=tk.W)
        self.Reset_button.grid( row=100, column=3, sticky=tk.E, padx=5)
        self.FeedLabel.grid(    row=100, column=4, sticky=tk.W)
        self.ErrLabel.grid(row=200, column=0, columnspan=9, sticky=tk.W)
        self.region_lower.columnconfigure(0, weight=0)
        self.region_lower.columnconfigure(1, weight=5)
        self.region_lower.columnconfigure(2, weight=1)
        self.region_lower.columnconfigure(3, weight=1)
        self.region_lower.columnconfigure(4, weight=25)


        # .grid: very last row (entry/label for "Feedback after each")
        self.PostLabel.grid(row=1000, column=0, columnspan=2, sticky=tk.E)
        self.PostEnter.grid(row=1000, column=2, columnspan=8, sticky=tk.EW)



        
        self.StepEnter_SelectionEvent(self.Marked_Steps[0])

    def Reset_names(self):
        [INPUT.delete(0, tk.END) for INPUT in self.InputPart]
        [INPUT.insert(0,TEXT) for INPUT, TEXT in zip(self.InputPart, self.order)]

    def GetNumberOfInteractions(self):
        self.Number = int(self.InteractionVar.get())

    def NumberEnter_SelectionEvent(self, event):
        self.GetNumberOfInteractions()
        for index in range(self.Number):
            self.LabelsInput[index].grid(row=index+101, sticky=tk.E   , column=0)
            self.InputName[  index].grid(row=index+101, sticky=tk.NSEW, column=1)
            self.InputPart[  index].grid(row=index+101, sticky=tk.NSEW, column=2, columnspan=2)
            self.InputFeed[  index].grid(row=index+101, sticky=tk.NSEW, column=4)
        for index in range(self.Number,self.MaxInteractions):
            self.LabelsInput[index].grid_forget()
            self.InputName[  index].grid_forget()
            self.InputPart[  index].grid_forget()
            self.InputFeed[  index].grid_forget()

    def StepEnter_SelectionEvent(self, event):
        event = re.search('[\W\_]*([a-zA-Z][a-zA-Z0-9]*)', event).group(1)
        if len(self.Interactions_By_Step.keys())==0:
            self.Step_Inter_Label.configure(text='')
        else:
            if event in self.Interactions_By_Step.keys():
                List_of_Interactions = self.Interactions_By_Step[event]
                self.Step_Inter_Label.configure(text='Interactions in step ({}):'.format(event))
            else:
                List_of_Interactions = []
                self.Step_Inter_Label.configure(text='No Interactions in step ({}):'.format(event))

            Length_of_Interactions = len(List_of_Interactions)
            for index in range(len(self.Copy_Buttons)):
                if index<Length_of_Interactions:
                    self.Copy_Buttons[index].grid()
                    self.Copy_Buttons[index].configure(text=List_of_Interactions[index])
                else:
                    self.Copy_Buttons[index].grid_remove()


    def create_Feedbacks(self):
        self.GetNumberOfInteractions()

        self.InputedNames = [input.get() for index, input in enumerate(self.InputName) if index<self.Number]
        self.InputedParts = [input.get() for index, input in enumerate(self.InputPart) if index<self.Number]
        self.InputedFeeds = [input.get() for index, input in enumerate(self.InputFeed) if index<self.Number]

        self.StepToInput   = self.StepVar.get()
        self.StepToInput   = re.search('[\W\_]*([a-zA-Z][a-zA-Z0-9]*)', self.StepToInput).group(1)
        self.PreEnterText  = self.PreEnter.get()
        self.PostEnterText = self.PostEnter.get()

        NonLetters = ('').join(set(re.findall('\W',('').join(self.InputedNames))))

        self.Check_Value = False
        if  min([len(XXX) for XXX in self.InputedNames + self.InputedParts]) == 0:
            self.ErrLabel.configure(bg='red', text="Enter values (at least for all Inputs/Part Names)")
        elif self.Initial_Text == None:
            self.ErrLabel.configure(bg='red', text="No steps found")
        elif NonLetters != '':
            self.ErrLabel.configure(bg='red', text="Input Names contain prohibited characters: {}".format(NonLetters))
        else:
            self.InputedParts = [cgi.escape(XXX) for XXX in self.InputedParts]
            self.InputedFeeds = [cgi.escape(XXX) for XXX in self.InputedFeeds]
            self.PreEnterText = cgi.escape(self.PreEnterText)
            self.PostEnterText = cgi.escape(self.PostEnterText)
            self.InputedNames = ['~{}'.format(I) if I[0] != '~' else I for I in self.InputedNames]

            #### Names feedback_links, then generates text to be added
            #*** Names feedbacks, The variable "Digit" increments the digits before the ones-place to avoid overwriting previous feedbacks ***
            Digits = re.findall("(?<=FeedbackPart)\d+", self.Initial_Text)
            if len(Digits) == 0:
                Digit = 1
            else:
                Digits = [int(XXX) for XXX in Digits]
                Digit  = max(Digits)//10+2
            FeedbackNames = ["FeedbackPart{}".format(n) for n in range(Digit*10+1, Digit*10+2+2**self.Number)]


            #*** REreplace is the text added, to a step, to link to the feedbacks ***
            REreplace = " <step name=\"{}\g<1> {} <rvxml> ".format(self.StepToInput, self.in_correct(self.Number,self.InputedNames,FeedbackNames))

            #*** Include ".*?" in the parentheses below to avoid deleting any previous feedback links on the step ***
            REsearch = "<step name=\"{}(\".*?>).*?<rvxml>".format(self.StepToInput)
            self.Final_Text   = re.sub(REsearch, REreplace, self.Initial_Text, flags=re.IGNORECASE | re.DOTALL)
            ####


            #### Names feedbacks_steps, then generates text to be added
            #*** AddFeedbacks is the text added, to the Feedbacks Window, containing the new feedbacks ***
            # *** edit this ***
            self.PreEnterText  = re.sub('^\s+(.*?)\.?\s*$','\g<1>. ', self.PreEnterText)
            self.PostEnterText = re.sub('^\s+(.*?)\.?\s*$','\g<1>. ', self.PostEnterText)
            if self.PreEnterText != '':
                self.PreEnterText = '{} '.format(self.PreEnterText)


            self.InputedFeeds = ['' if ZZZ == '' else re.sub('^\s*(.*?)\.?\s*$','\g<1>. ', ZZZ) for ZZZ in self.InputedFeeds]


            FB = self.feedbacks(self.Number, self.InputedFeeds, self.InputedParts)
            FB = [self.PreEnterText + fb + self.PostEnterText for fb in FB]
            self.FeedBacks_List = FB


            AddFeedbacks = '\r ' + ' '.join(["<step name=\"" + names + "\"> <rvxml> <document stringtags=\"0\"> <text>" + fb + "</text> </document> </rvxml>  </step> " for names, fb in zip(FeedbackNames,FB)]) + ' \r '
            does_not_contains_feedback = self.Final_Text.find("<window name=\"feedback\"/>") + 1
            #*** Adds feedbacks ***
            if does_not_contains_feedback:
                Findfeedback = "(?<=<window name=\"feedback\")/>"
                self.Final_Text = re.sub(Findfeedback, "> " + AddFeedbacks + "    </window> ", self.Final_Text)
            else:
                Findfeedback = "(?<=<window name=\"feedback\">)(.*?)(?=</window>)"
                self.Final_Text = re.sub(Findfeedback, " \g<1> " + AddFeedbacks + " \r ", self.Final_Text, flags=re.DOTALL)
            self.Check_Value = True
            ####


    def Add_Feedbacks(self):
        self.create_Feedbacks()
        if self.Check_Value:
            # Passes edited self.Final_Text to parent class, to update all UI Tabs
            self.MASTERui.Update_TDX_File(self.Final_Text)
            self.ErrLabel.configure(bg='green', text="Feedbacks added")
            print('Commit: Add Multi-Part Feedbacks')

    def Update_File(self, New_File, New_Steps, New_Dict):
        'Deprecated'
        self.Initial_Text         = New_File
        self.Initial_Steps        = New_Steps
        self.Interactions_By_Step = New_Dict
        self.Marked_Steps = ['**{}**'.format(NAME) if NAME in self.multiple_interactions else NAME for NAME in self.Initial_Steps]
        self.Reset_DropDown_Names()

    def Reset_DropDown_Names(self):
        self.StepEnter['menu'].delete(0, 'end')
        for string in self.Marked_Steps:
            self.StepEnter["menu"].add_command(label=string, command=lambda value=string: self.StepEnter_SelectionEvent(value))
        self.StepVar.set(self.Marked_Steps[0]) 


    def AndList(self,L):
        '''
        takes list of items
        returns string, where each item is comma separated except the last 2, 
        which are ' and ' separated for 2 items, else ', and ' separated
        '''
        L = [str(XXX) for XXX in L]
        if len(L) <= 2:
            return ' and '.join(L)
        else:
            return ', '.join(L[:-2] + [L[-2] + ', and ' + L[-1]])
     
    def OptionsList(self,n):
        '''
        returns all TF options for n user inputs, except all True
        '''
        assert 1 < n < 9 and n == int(n), 'Input must be an integer between 2 and 8'
        return sorted([[int(XXX) for XXX in tuple((bin(number)[2:].zfill(n)))] for number in range(2**n)],reverse=True)[1:]
        '''
            assert 1 < n < 9 and n == int(n), 'Input must be an integer between 2 and 8'
            return sorted(zip(*[((0,)*(2**x)+(1,)*(2**x))*2**(n-x-1) for x in range(n)]), reverse=True)[1:]]
            '''

    def feedbacks(self,n, individual_feedbacks, order):
        '''
        returns feedback text for each option in OptionsList(n)
        '''
        assert 1 < n < 9 and n == int(n), 'Input must be an integer between 2 and 8 (inclusive)'
        Lst = self.OptionsList(n)
        ans = []
        for TF in Lst:
            correct = []
            incorrect = []
            incorrect_values = []
            for index, option in enumerate(TF):
                if option:
                    correct.append(order[index])
                else:
                    incorrect.append(order[index])
                    incorrect_values.append(index)
            if len(correct) == 0:
                a = '{} of your answers are incorrect. '.format('Both' if (n == 2) else 'All')
                b = ''.join([individual_feedbacks[N] for N in incorrect_values])
            else:
                a = 'Your {Part1Name} answer{IS1are} correct, but your '.format(
                    Part1Name=self.AndList(correct), IS1are=' is' if len(correct) == 1 else 's are')
                b = '{Part2Name} answer{IS2are} incorrect. '.format(Part2Name=self.AndList(incorrect), IS2are=' is' if len(incorrect) == 1 else 's are') + ''.join([individual_feedbacks[N] for N in incorrect_values])

            ans.append((a + b))
        return ans

    def in_correct(self,n, interactions, FeedbackNames):
        '''
        returns a string for the incorrect/correct boolean expressions for n items in OptionsList(n)
        '''
        assert 1 < n < 9 and n == int(n), 'Input must be an integer between 2 and 8'
        L = self.OptionsList(n)
        ans = []
        
        for indexO, O in enumerate(L):
            responses = []
            for index, option in enumerate(O):
                if option:
                    responses.append(interactions[index] + '.correct')
                else:
                    responses.append(interactions[index] + '.incorrect')
            ans.append("<msgwrong cw=\"70\" ch=\"0\"> <expr>" + ' and '.join(responses) + "</expr> <display step=\"" + FeedbackNames[indexO] + "\"/> </msgwrong> ")

        return (' '.join(ans))

    def Test_FB(self):
        self.create_Feedbacks()
        try:
            self.region_tests.grid_forget()
        except:
            pass
        self.region_tests = VerticalScrolledFrame(self, BG=self.UI_Settings.ColorBack1 )
        self.region_tests.grid(row=2, column=0, padx=5, pady=5, sticky=tk.NSEW)
        self.rowconfigure(2, weight=1)
        for index, FEEDBACK in enumerate(self.FeedBacks_List):
            LABEL = tk.Label(self.region_tests.interior, text=FEEDBACK, bg=self.UI_Settings.ColorBack1)
            LABEL.grid(row=index, column=0, sticky=tk.W)


    def Print2clip(self,text):              # Print to clipboard (general)
        clippy = tk.Tk()
        clippy.withdraw()
        clippy.clipboard_clear()
        clippy.clipboard_append(text)
        clippy.update()
        clippy.destroy()


    def Copy_Button_Press_closure(self, N):
        'Uses closure to create functions to display a copy button for each interaction in the selected step'
        def Copy_Button_Press_closed():
            Current_Step = self.StepVar.get()
            Current_Step = re.search('[\W\_]*([a-zA-Z][a-zA-Z0-9]*)', Current_Step).group(1)
            Interactions = self.Interactions_By_Step[Current_Step]
            self.Print2clip(Interactions[N])
        return Copy_Button_Press_closed


    def Paste_Button_Press_closure(self, N):
        'Uses closure to create functions to display a paste button for each displayed interaction row in UI'
        def Paste_Button_Press_closed():
            self.InputName[N].delete(0, tk.END)
            self.InputName[N].insert(0, self.clipboard_get()) 
        return Paste_Button_Press_closed


### Components
class BarGraph(tk.Frame):                   # Displays a basic bar graph
    'Simple bar graph'
    def __init__(self, parent, 
                y                = [Y**2 for Y in range(4,9)], 
                MASTER           = None,
                TITLEx           = 'Bar Chart', 
                Pixel_Accuracy   =  2000, 
                COLOR_background = 'grey', 
                COLOR_pos        = 'blue', 
                COLOR_zero       = 'red', 
                COLOR_Label      = 'white'):


        MAX   = max(y)
        MIN   = 0
        DELTA = float(MAX-MIN)
        TITLE = '{T}: y=[{A},{B}]'.format(T=TITLEx, A=MIN, B=MAX)
        LENGTH = len(y)
        if LENGTH>100:
            WIDTHa = 0
            WIDTHb = 1
        else:
            WIDTHa = 1
            WIDTHb = 50


        #creates main Frame
        _G_ = self._G_ = tk.LabelFrame(parent, text=TITLE, foreground=COLOR_Label, bg=COLOR_background, relief='ridge')
        _G_.grid(row=0, column=0, ipady=50, sticky=tk.NSEW)
        _G_.rowconfigure(0, weight=1)


        #ScaledY = [a-1= if a!=0 else a for a in y ]
        ScaledY    = [int(round(Pixel_Accuracy*(YY)/DELTA,0)) for YY in y]
        MIN_scaled = min(ScaledY)
        ScaledY_positive = [YY+MIN_scaled for YY in ScaledY]
        ScaledY_DELTA    = max(ScaledY_positive)-min([0]+ScaledY_positive)
        #print('asd',ScaledY_DELTA,ScaledY_positive)
        #print('y={}'.format(y),'H={}'.format(ScaledY))

        #print('sdf',ScaledY, y)
        for COL, (H, H_pos, Y) in enumerate(zip(ScaledY,ScaledY_positive, y)):
            # Scales used columns, so Bar's grow wider
            _G_.columnconfigure(  COL, weight=1)                    




            A = tk.Frame(_G_, height=1, width=WIDTHb, bg=COLOR_pos)
            A.grid(row=0, column=COL, padx=WIDTHa, sticky=tk.NSEW)

            #print('xy',H_pos, -H_pos+ScaledY_DELTA)
        
            Bar_zero  = tk.Frame(A, height=1, width=10, bg=COLOR_zero)
            Bar_lower = tk.Frame(A, height=1, width=10)
            Bar_upper = tk.Frame(A, height=1, width=10)

            A.columnconfigure(0, weight=1)
            A.rowconfigure(0, weight=10*(ScaledY_DELTA-H_pos))
            A.rowconfigure(1, weight=10*H_pos)
            A.rowconfigure(2, weight=10)

            [XXX.columnconfigure(0, weight=1) for XXX in [Bar_lower,Bar_upper,Bar_zero]]
            [XXX.rowconfigure(   0, weight=1) for XXX in [Bar_lower,Bar_upper,Bar_zero]]

            Bar_lower.rowconfigure(0, weight=1)
            Bar_upper.rowconfigure(0, weight=1)
            Bar_zero.rowconfigure( 0, weight=1)


            Bar_zero.grid(row=2, column=0, sticky=tk.NSEW)
            Bar_upper.grid(row=0, column=0, sticky=tk.NSEW)


class VerticalScrolledFrame(tk.Frame):      # All vertical scrollbars use this
    """A pure tk scrollable frame that actually works!
    * Use the 'interior' attribute to place widgets inside the scrollable frame
    * Construct and pack/place/grid normally
    * This frame only allows vertical scrolling
    """

    def __init__(self, parent, BG='light grey', *args, **kw):
        tk.Frame.__init__(self, parent, *args, **kw)

        # create a canvas object and a vertical scrollbar for scrolling it
        vscrollbar = tk.Scrollbar(self, orient=tk.VERTICAL)
        vscrollbar.pack(fill=tk.Y, side=tk.RIGHT, expand=tk.FALSE)
        canvas = tk.Canvas(self, bd=0, highlightthickness=0,
                        yscrollcommand=vscrollbar.set, bg=BG)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.TRUE)
        vscrollbar.config(command=canvas.yview)
        self.canvas = canvas

        # reset the view
        canvas.xview_moveto(0)
        canvas.yview_moveto(0)

        # create a frame inside the canvas which will be scrolled with it
        self.interior = interior = tk.Frame(canvas, bg=BG)
        interior_id = canvas.create_window(0, 0, window=interior,
                                           anchor=tk.NW)

        # track changes to the canvas and frame width and sync them,
        # also updating the scrollbar
        def _configure_interior(event):
            # update the scrollbars to match the size of the inner frame
            size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
            canvas.config(scrollregion="0 0 %s %s" % size)
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the canvas's width to fit the inner frame
                canvas.config(width=interior.winfo_reqwidth())
        interior.bind('<Configure>', _configure_interior)

        def _configure_canvas(event):
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the inner frame's width to fill the canvas
                canvas.itemconfigure(interior_id, width=canvas.winfo_width())
        canvas.bind('<Configure>', _configure_canvas)


class ScrolledNameList(tk.Frame):           # Displays a list of names/replacement names
    def __init__(self, parent, SELF_SETTINGS, LABEL = 'testing', Data_List = ['a','b','x'], *args, **kw):
        tk.Frame.__init__(self, parent, *args, **kw)
        self.Data_List = Data_List

        self.UI_Settings = SELF_SETTINGS

        # Set relief type and color, for each ScrolledNameList()
        self.configure(bd=5, relief='ridge', bg=self.UI_Settings.ColorBack1)

        Scrollable = VerticalScrolledFrame(self, BG=self.UI_Settings.ColorBGnoGrey)
        self.TopBox = tk.Frame(self,
            bd = 4,
            bg = self.UI_Settings.ColorBGltGrey,
            relief='groove')

        ScrollRow = 1
        self.TopBox.grid(     row=0, column=0, pady=0, ipadx=5,  sticky=tk.EW)
        Scrollable.grid(      row=ScrollRow, column=0, padx=0, ipady=5,  sticky=tk.NSEW)

        self.rowconfigure(ScrollRow, weight=1)
        self.columnconfigure(     0, weight=2)


        Column_Label = tk.Label(self.TopBox, 
            text='{}s ({})'.format(LABEL, len(Data_List)), 
            underline=0,
            bg = self.UI_Settings.ColorText,
            bd = 2,
            relief='groove') # relief = FLAT, RAISED, SUNKEN, GROOVE, RIDGE
        Reset_Button = tk.Button(self.TopBox, 
                command=self.Reset_Values, 
                text='Reset Names',
                bg= self.UI_Settings.ColorClear)
        AutoN_Button = tk.Button(self.TopBox, 
                command=self.AutoName_Values, 
                text=u'Auto Root\u2192', 
                bg = self.UI_Settings.ColorEdit , 
                anchor=tk.E)

        self.AutoName_Entry = tk.Entry(self.TopBox, bg=self.UI_Settings.ColorInput)
        self.AutoName_Entry.insert(0,LABEL)

        self.BoxVar    = tk.IntVar()
        self.BoxToggle = tk.Checkbutton(self.TopBox, 
                highlightcolor='green', 
                selectcolor="white", 
                bg=self.UI_Settings.ColorBGltGrey, 
                text=u'Allow RegEx*', 
                variable=self.BoxVar, 
                anchor=tk.W)
        self.BoxToggle.invoke()

        Column_Label.grid(    row=0,    column=0, pady=3, padx=0, sticky=tk.NS, ipadx=15, ipady=4, columnspan=2)
        AutoN_Button.grid(    row=2,    column=0, pady=0, padx=2, sticky=tk.EW, ipadx=10)
        self.AutoName_Entry.grid(row=2, column=1, pady=0, padx=2, sticky=tk.EW)
        Reset_Button.grid(    row=4,    column=0, pady=3, padx=2, sticky=tk.EW, ipadx=5)
        self.BoxToggle.grid(  row=4,    column=1, pady=3, padx=0, sticky=tk.NSEW)


        self.TopBox.columnconfigure(0, weight=3)
        self.TopBox.columnconfigure(1, weight=2)

        ###


        self.Entry_Boxes = [tk.Entry(Scrollable.interior, textvariable=tk.StringVar(self, value=Text), bg=self.UI_Settings.ColorInput) for index, Text in enumerate(Data_List)]
        Text_Label = [tk.Label(Scrollable.interior, text=Text, bg=self.UI_Settings.ColorBGnoGrey) for Text in Data_List]
        for index, (TEXT0, ENTRY) in enumerate(zip(Text_Label,self.Entry_Boxes)):
            TEXT0.grid(row=index, column=0, sticky=tk.W)
            ENTRY.grid(row=index, column=1, sticky=tk.EW)

        Scrollable.rowconfigure(   1, weight=1)
        Scrollable.columnconfigure(0, weight=1)
        Scrollable.interior.columnconfigure(0, weight=1)
        Scrollable.interior.columnconfigure(1, weight=4)


    def Get_Final_Values(self):
        return [ENTRY.get() for ENTRY in self.Entry_Boxes]

    def Get_Original_Values(self):
        return self.Data_List

    def Clear_Values(self):
        [entered.delete(0, tk.END) for entered in self.Entry_Boxes]

    def Reset_Values(self):
        self.Clear_Values()
        self.Input_Values(self.Data_List)
        [BOX.configure(bg='white') for BOX in self.Entry_Boxes]

    def Input_Values(self,VALUES):
        self.Clear_Values()
        [entered.insert(0,Text) for entered, Text in zip(self.Entry_Boxes, VALUES)]

    def Apply_Regex(self, SEARCH, REPLACE):
        if self.BoxVar.get():
            old_list = self.Get_Final_Values()
            new_list = [re.sub(SEARCH, REPLACE, CELL, flags=re.IGNORECASE) for CELL in old_list]

            self.Input_Values(new_list)

    def Highlight_Duplicates(self, DUPES):
        Final_Names = self.Get_Final_Values()
        Count = 0
        for NAME, BOX in zip(Final_Names,self.Entry_Boxes):
            if (NAME.lower() in DUPES+[r'#']):
                Count += 1
                BOX.configure(bg='red')
            else:
                ### no Color
                BOX.configure(bg='white')

    def AutoName_Values(self):
        PREFIX = self.AutoName_Entry.get()
        # Creates list of acceptable characters
        alphanumerics = [chr(XXX) for XXX in list(range(ord('a'),ord('z')+1))+list(range(ord('A'),ord('Z')+1))+list(range(ord('0'),ord('9')+1))]
        # Removes unnaceptable characters from PREFIX
        PREFIX = ''.join([LETTER for LETTER in PREFIX if LETTER in alphanumerics])      

        length = len(self.Data_List)
        digits = len(str(length))
        Names = ['{PRE}{NUM:0>{DIG}}'.format(PRE=PREFIX, NUM=index, DIG=digits) for index in range(1,1+length)]
        if self.Data_List[0] == 'step1':
            Names[0] = 'step1'
        self.Input_Values(Names)


class ScrolledNameListsREGEX(tk.Frame):     # Displays multiple ScrolledNameList(s), with a common RegEx
    def __init__(self, parent, SELF_SETTINGS, Data_Lists = ['1','2','3']*3, Data_Labels=['A','B','C'], *args, **kw):
        tk.Frame.__init__(self, parent, *args, **kw)
        self.Data_Lists  = Data_Lists
        self.Data_Labels = Data_Labels

        self.UI_Settings = SELF_SETTINGS

        self.Scrolled = [ScrolledNameList(self, SELF_SETTINGS, LABEL = _Label_, Data_List =_List_) for _Label_, _List_ in zip(Data_Labels, Data_Lists)]

        base_row = 10
        self.rowconfigure(base_row, weight=1)
        self.configure(bg= self.UI_Settings.ColorBack1)


        NumCol = len(Data_Labels)
        x_pad = 5 if NumCol<5 else 0
        for index, SCROLL in enumerate(self.Scrolled):
            SCROLL.grid(row=base_row, column=index, pady=5, padx=x_pad, sticky=tk.NSEW)

        #ensures spacing for 1-2 self.Scrolled
        if NumCol<3:
            for index in range(NumCol,4):
                tk.Label(self, text='', bg=self.UI_Settings.ColorBack1 ).grid(row=base_row, column=index, ipadx=20)
        [self.columnconfigure(index, weight=1) for index in range(max(len(self.Scrolled),3))] 



        if NumCol==0:
            LABEL = tk.Label(self, text="No items to rename in this type.")
            LABEL.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        else:
            Regex_Region = tk.LabelFrame(self, text="", bg=self.UI_Settings.ColorBack1)
            Regex_Region.grid(row=0, column=0, padx=5, pady=5, sticky=tk.NSEW, columnspan=10)

            self.RegEx_Button_Var = tk.Button(Regex_Region, text="Trigger RegEx***", bg = self.UI_Settings.ColorEdit, command=self.REGEX_command)
            self.RegEx_Search     = tk.Entry( Regex_Region, textvariable=tk.StringVar(self, value='Regex: Search string'), bg=self.UI_Settings.ColorInput)
            self.RegEx_Replace    = tk.Entry( Regex_Region, textvariable=tk.StringVar(self, value='Regex: Replacement string'), bg=self.UI_Settings.ColorInput)

            self.RegEx_Button_Var.grid(row=0, column=0, padx=5, pady=5, sticky=tk.NSEW, ipadx=5)
            self.RegEx_Search.grid(    row=0, column=1, padx=5, pady=5, sticky=tk.NSEW)
            self.RegEx_Replace.grid(   row=0, column=2, padx=5, pady=5, sticky=tk.NSEW)
            [Regex_Region.columnconfigure(index, weight=index*2) for index in range(3)]


    def REGEX_command(self):
        [XXX.Apply_Regex(self.RegEx_Search.get(), self.RegEx_Replace.get()) for XXX in self.Scrolled]

    def GET_names(self):
        self.names_old = [XXX.Get_Original_Values() for XXX in self.Scrolled]
        self.names_new = [XXX.Get_Final_Values()    for XXX in self.Scrolled]

        #print('z000', self.names_old, self.names_new)
        if max([0]+[len(XXX) for XXX in self.names_old])!=0:
            self.names_old_flat = [item for sublist in self.names_old for item in sublist]

            names_new_flat = [item for sublist in self.names_new for item in sublist]
            names_new_flat = [re.sub('\W', '', TEXT) for TEXT in names_new_flat]
            names_new_flat = [OLD if TEXT=='' else TEXT for OLD, TEXT in zip(self.names_old_flat,names_new_flat)]
            self.names_new_flat = names_new_flat

            #print('z123', self.names_old_flat, self.names_new_flat)
            self.names_old_flat, self.names_new_flat = zip(*sorted(zip(self.names_old_flat, self.names_new_flat), key=len, reverse=True))
        else:
            self.names_old_flat, self.names_new_flat = [], []

    def Highlight_Dupes(self, DUPES=[]):
        [XXX.Highlight_Duplicates(DUPES) for XXX in self.Scrolled]


class ScrolledFrameXY(tk.Frame):            # All 2-way scrollbars use this
    """A pure tk scrollable frame that actually works!
    * Use the 'interior' attribute to place widgets inside the scrollable frame
    * Construct and pack/place/grid normally
    """

    def __init__(self, parent, TitleX = 'tk Popup', *args, **kw):
        tk.Frame.__init__(self, parent, *args, **kw)            
        self.winfo_toplevel().title(TitleX)

        # create a canvas object and scrollbars for scrolling it
        vscrollbar = tk.Scrollbar(self, orient=tk.VERTICAL)
        hscrollbar = tk.Scrollbar(self, orient=tk.HORIZONTAL)
        canvas = tk.Canvas(self, bd=0, highlightthickness=0,
                        yscrollcommand=vscrollbar.set,
                        xscrollcommand=hscrollbar.set)

        hscrollbar.grid(row=1, column=0,  sticky=tk.EW)
        vscrollbar.grid(row=0, column=1, sticky=tk.NS)
        canvas.grid(row=0, column=0, sticky=tk.NSEW)

        # connect scrollbars to 'canvas' scrolling
        vscrollbar.config(command=canvas.yview)
        hscrollbar.config(command=canvas.xview)

        # reset the view
        canvas.xview_moveto(0)
        canvas.yview_moveto(0)

        canvas.configure(bg='black')

        # expands canvas, and not scrollbars
        self.columnconfigure(0, weight=1)
        self.rowconfigure(   0, weight=1)
        #parent.columnconfigure(0, weight=1)
        #parent.rowconfigure(   0, weight=1)

        # create a frame inside the canvas which will be scrolled with it
        self.interior = interior = tk.Frame(canvas)
        interior_id = canvas.create_window(0, 0, window=interior, anchor=tk.NW)

        interior.configure(bg='black')

        # track changes to the canvas and frame width and sync them,
        # also updating the scrollbar
        def _configure_interior(event):
            # update the scrollbars to match the size of the inner frame
            size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
            canvas.config(scrollregion="0 0 %s %s" % size)
        interior.bind('<Configure>', _configure_interior)


class ForcePopup(tk.Frame):                 # Yes/No Popup, that is forced to be above the main window
    def __init__(self, parent, TEXTpop, TEXTlist, *args, **kw):
        tk.Frame.__init__(self)
        self.SELECTION = None
        self.Overwrite = tk.Toplevel(parent)
        self.Force_to_Top(self.Overwrite)

        info1 = tk.Label(self.Overwrite,  text=TEXTpop, justify=tk.LEFT)
        info1.grid(      row=0, column=1, padx=5, pady=5, sticky=tk.W)

        for index, (TEXT, COLOR) in enumerate(TEXTlist):
            button = tk.Button(self.Overwrite, 
                text=TEXT, 
                bg=COLOR, 
                command=self.CMD_gen(parent, self.Overwrite, index), 
                justify=tk.LEFT)
            button.grid(row=1+index, column=1, padx=5, pady=5, sticky=tk.W)

        parent.wait_window(self.Overwrite)

    def Force_to_Top(self, FRAME):
        FRAME.attributes('-topmost', True)
        FRAME.grab_set()
        FRAME.lift()
        FRAME.focus_force()
        FRAME.minsize(400, 200)


    def CMD_gen(self, parent, FRAME, N):
        def CloseX():
            FRAME.grab_release()
            FRAME.destroy()
            parent.lift()
            parent.focus_force()
            self.SELECTION = N
            #return (N)

        return CloseX













###
###
### Initialize
if __name__=='__main__':
    Initialize = UI_Master_Class(FileDirectory = r'C:\Users\GEX\Desktop\testing')
