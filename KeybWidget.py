

import MenuWidget
import ScorerWidgets
import Raster
import BInput
import BUIx
import MenuText
import ListWidget
import pdb
import math

import Raster
import Bladex
import acts
import netwidgets
import nvda

AdditionalKeysCallBack = None

DefInfoText = "Press ENTER to define key, DELETE to delete bindings, Escape to exit"

ActionDescriptor= {
                   "Attack"        : "Used to kill, mutilate and destroy",
                   "Forwards"      : "Double-tap FORWARDS to Run.",
                   "Backwards"     : "Press FORWARDS and BACKWARDS simultaneously to turn 180 degrees.",
                   "Select Enemy"  : "Press SELECT ENEMY to lock the movement around an enemy",
                   "Use"           : "To pick up an object, press USE",
                   "Jump"          : "Press JUMP while running to perform a long jump.",
                   "Throw"         : "While holding down THROW, press ATTACK.",
                  }

class B_ControlItemText(MenuWidget.B_MenuItemText):
  def __init__(self,Parent,MenuDescr,StackMenu,font_server=ScorerWidgets.font_server):
    MenuWidget.B_MenuItemText.__init__(self,Parent,MenuDescr,StackMenu,font_server)
    self.SetDrawFunc(self.Draw)
    self.SetAlpha(1.0)
    self.ChangingKey=0  #
    #self.SetColor(1.0)
    self.SelectionFilterUpdated=0
    self.FilterUpdated=0
    self.SetColor(207,144,49)
    self._foc=-1
    self.ActionName = None

  def SetText(self,text,ActionName=None):
    MenuWidget.B_MenuItemText.SetText(self,text)
    self.SelectionFilterUpdated=0
    self.FilterUpdated=0
    self.ActionName = ActionName

  def Draw(self,x,y,time):
    if self.GetVisible()==0:
      return

    #self.SetAlpha(0.5)

    foc=self.GetHasFocus()
    if foc!=self._foc:        
      self.SelectionFilterUpdated=0
      self.FilterIncX=0
      self.FilterUpdated=0

    self._foc=foc
    w,h=self.GetSize()

    if foc:
      if self.ActionName:
        if ActionDescriptor.has_key(self.ActionName):
          netwidgets.LabelName = MenuText.GetMenuText(ActionDescriptor[self.ActionName])
        else:
          netwidgets.LabelName = " "
      if self.ChangingKey:
        mult=math.cos(time*2)
        self.SetColor(80*mult+150,80*mult+150,45*mult+105)
        self.DefDraw(x,y,time)
        return
      elif self.SelectionFilterUpdated:
        Raster.SetPosition(x-self.FilterIncX,y-self.FilterIncY)
        Raster.DrawImage(w+2*self.FilterIncX,h+2*self.FilterIncY,"RGB","Native",self.SelectionFilter.GetImageBuffer())
        self.SetColor(252,247,167)
        self.DefDraw(x,y,time)
        self.SetColor(207,144,49)
        return
    else:
##      if self.Filter is None:
##        self.CreateBlur(x,y,time)
##      Raster.SetPosition(x-2,y-2)
##      Raster.DrawImage(w+4,h+4,"RGB","Native",self.Filter.GetImageBuffer())
##      if Raster.GetClipActive():
##        print self.Name(),"ClipActive:",Raster.GetClipWindow()
##      else:
##        print self.Name(),"ClipNoActive:"
      self.DefDraw(x,y,time)
      return

    if foc:
      #self.CreateDistorsion(x,y,time)
      #if self.Filter is None:
      #  self.CreateBlur(x,y,time)
      #  self.FilterUpdated=1
      #sfw,sfh=self.Filter.GetDimension()
      #self.SelectionFilter.CopySubBuffer(self.FilterIncX-2,0,sfw,sfh,self.Filter.GetImageBuffer(),"AddInc")
      #self.SelectionFilter.GetFromBuffer2("Substract")
      #Raster.SetPosition(x-self.FilterIncX,y-self.FilterIncY)
      #Raster.DrawImage(w+2*self.FilterIncX,h+2*self.FilterIncY,"RGB","Native",self.SelectionFilter.GetImageBuffer())
      self.SetColor(252,247,167)
      self.DefDraw(x,y,time)
      self.SetColor(207,144,49)

      if self.FilterIncX>25:
        self.SelectionFilterUpdated=1
      else:
        self.SelectionFilterUpdated=0




class B_ControlItemTexts(BUIx.B_FrameWidget,MenuWidget.B_MenuTreeItem):
  def __init__(self,Parent,MenuDescr,StackMenu):
    BUIx.B_FrameWidget.__init__(self,Parent,MenuDescr["Name"],400,15)
    MenuWidget.B_MenuTreeItem.__init__(self,MenuDescr,StackMenu)
    self.wActionName=B_ControlItemText(self,MenuDescr,StackMenu)
    self.wActionKeys=B_ControlItemText(self,MenuDescr,StackMenu)
    self.AddWidget(self.wActionName,0,0,
                   BUIx.B_FrameWidget.B_FR_AbsoluteLeft,BUIx.B_FrameWidget.B_FR_Left,
                   BUIx.B_FrameWidget.B_FR_AbsoluteTop,BUIx.B_FrameWidget.B_FR_Top)
    self.AddWidget(self.wActionKeys,0,0,
                   BUIx.B_FrameWidget.B_FR_AbsoluteRight,BUIx.B_FrameWidget.B_FR_Right,
                   BUIx.B_FrameWidget.B_FR_AbsoluteTop,BUIx.B_FrameWidget.B_FR_Top)
    self.HasFocus=0
    self.SetClipDraw(0)


  def __del__(self):
    BUIx.B_FrameWidget.__del__(self)
    MenuWidget.B_MenuTreeItem.__del__(self)

  def SetHasFocus(self,foc):
    self.HasFocus=foc
    self.wActionName.SetHasFocus(foc)
    self.wActionKeys.SetHasFocus(foc)

  def GetHasFocus(self,foc):
    return self.HasFocus




class ControlMenuItem(B_ControlItemTexts):
  def __init__(self,Parent,MenuDescr,StackMenu):
    #Bldb.set_trace()
    B_ControlItemTexts.__init__(self,Parent,MenuDescr,StackMenu)
    self.ActionName=MenuDescr["Action"]
    self.IManager=BInput.GetInputManager()
    oldInputActionsSet=self.IManager.GetInputActionsSet()
    self.IManager.SetInputActionsSet("Default")
    IActions=self.IManager.GetInputActions()
    self.IAction=IActions.Find(self.ActionName)
    self.KeyBounded=[]
    self.Parent=Parent
    self.Extras = MenuDescr["kFlags"]

    if self.IAction.Name()!="NULL":
      for i in range(self.IAction.nInputEvents()):
      	IEvent=self.IAction.GetnInputEvent(i)
      	if(IEvent.GetDevice()=="Keyboard" or IEvent.GetDevice()=="Mouse" or IEvent.GetDevice()=="Pad"):
      	  self.KeyBounded.append(IEvent.GetKey())
    else:
      print "Cant find",self.ActionName

    self.BaseText=MenuDescr["Name"]
    self.wActionName.SetText(self.BaseText,self.ActionName)
    self.wActionKeys.SetText(str(self.KeyBounded))
    self.RecalcLayout()
    self.IManager.SetInputActionsSet(oldInputActionsSet)

    self.ListenerName=MenuDescr["Name"]+" Listener"
    self.Listener=BInput.B_InputListener(self.ListenerName) #No se puede heredar mltiple de una clase generada por SWIG
    self.Listener.SetPythonFunc(self.ListenDevice)


    self.MouseListenerName=MenuDescr["Name"]+" MouseListener"
    self.MouseListener=BInput.B_InputListener(self.MouseListenerName) #No se puede heredar mltiple de una clase generada por SWIG
    self.MouseListener.SetPythonFunc(self.ListenMouseDevice)

    self.PadListenerName=MenuDescr["Name"]+" PadListener"
    self.PadListener=BInput.B_InputListener(self.PadListenerName) #No se puede heredar mltiple de una clase generada por SWIG
    self.PadListener.SetPythonFunc(self.ListenPadDevice)
    self.ReadyToEscape = 1


  def ActivateItem(self,act):
    if not act:
        if self.ReadyToEscape:
            B_ControlItemTexts.ActivateItem(self,act)
        self.ReadyToEscape = 1
        return
            
    if len(self.KeyBounded)>=3:
      self.SetStatusText(MenuText.GetMenuText("Maximun number of key bindings reached."))
      return
    self.SetStatusText(MenuText.GetMenuText("Press desired key, Escape to end"))
    keyb=self.IManager.GetAttachedDevice("Keyboard")
    if keyb.this!="NULL":
    	keyb.AddListener(self.Listener)
    keyb=self.IManager.GetAttachedDevice("Mouse")
    if keyb.this!="NULL":
    	keyb.AddListener(self.MouseListener)
    keyb=self.IManager.GetAttachedDevice("Pad")
    if keyb.this!="NULL":
    	keyb.AddListener(self.PadListener)
    self.oldInputActionsSet=self.IManager.GetInputActionsSet()
    self.IManager.SetInputActionsSet("MenuRedefine")
    self.wActionName.ChangingKey=1
    self.wActionKeys.ChangingKey=1



  def EndDefineKey(self):
    self.SetStatusText(MenuText.GetMenuText(DefInfoText))
    self.IManager.SetInputActionsSet(self.oldInputActionsSet)
    keyb=self.IManager.GetAttachedDevice("Keyboard")
    if keyb.this!="NULL":
    	keyb.RemoveListener(self.ListenerName)
    keyb=self.IManager.GetAttachedDevice("Mouse")
    if keyb.this!="NULL":
    	keyb.RemoveListener(self.MouseListenerName)
    keyb=self.IManager.GetAttachedDevice("Pad")
    if keyb.this!="NULL":
    	keyb.RemoveListener(self.PadListenerName)

    self.wActionName.ChangingKey=0
    self.wActionName.SelectionFilterUpdated=0
    self.wActionName.FilterUpdated=0

    self.wActionKeys.ChangingKey=0
    self.wActionKeys.SelectionFilterUpdated=0
    self.wActionKeys.FilterUpdated=0



  def ListenDevice(self,x,y,z):
    if z==1.0:
      if x=="Esc":
        self.EndDefineKey()
        self.ReadyToEscape = 0
      elif x not in self.KeyBounded:
        if x=="Delete":
        	self.ReadyToEscape = 0
        keyb=self.IManager.GetAttachedDevice("Keyboard")
        self.IManager.SetInputActionsSet("Default")
        if keyb.IsBinded(x):
          self.SetStatusText(MenuText.GetMenuText("The key <")+x+MenuText.GetMenuText("> is already used!"))
        elif len(self.KeyBounded)>=3:
          self.SetStatusText(MenuText.GetMenuText("You already have 3 keys assigned to that action"))
        else:
          self.IAction.AddEvent(keyb,x,1)
          for k in self.Extras:
          	if   k[0] == "Press":
          		self.IManager.GetInputActions().Find(k[1]).AddEvent(keyb,x,1)
          	elif k[0] == "Release":
          		self.IManager.GetInputActions().Find(k[1]).AddEvent(keyb,x,0)
          	else:
          		print "ERROR : '",k[0],"' is not defined yet!"
          self.KeyBounded.append(x)
          self.IManager.SetInputActionsSet("MenuRedefine")
          self.wActionKeys.SetText(str(self.KeyBounded))
          self.RecalcLayout()
          self.EndDefineKey()

  def ListenMouseDevice(self,x,y,z):
    if (x!="X_Axis") and (x!="Y_Axis") and (x!="Z_Axis"):
      if x not in self.KeyBounded:
        keyb=self.IManager.GetAttachedDevice("Mouse")
        self.IManager.SetInputActionsSet("Default")
        if keyb.IsBinded(x) or len(self.KeyBounded)>=3:
          self.SetStatusText(MenuText.GetMenuText("The mouse action <")+x+MenuText.GetMenuText("> is already used!"))
          pass
        else:
          self.IAction.AddEvent(keyb,x,1)
          for k in self.Extras:
          	if   k[0] == "Press":
          		self.IManager.GetInputActions().Find(k[1]).AddEvent(keyb,x,1)
          	elif k[0] == "Release":
          		self.IManager.GetInputActions().Find(k[1]).AddEvent(keyb,x,0)
          	else:
          		print "ERROR : '",k[0],"' is not defined yet!"
          self.KeyBounded.append(x)
          self.IManager.SetInputActionsSet("MenuRedefine")
          self.wActionKeys.SetText(str(self.KeyBounded))
          self.RecalcLayout()
          self.EndDefineKey()

  def ListenPadDevice(self,x,y,z):
      if x not in self.KeyBounded:
        keyb=self.IManager.GetAttachedDevice("Pad")
        self.IManager.SetInputActionsSet("Default")
        if keyb.IsBinded(x) or len(self.KeyBounded)>=3:
          self.SetStatusText(MenuText.GetMenuText("The pad action <")+x+MenuText.GetMenuText("> is already used!"))
          pass
        else:
          self.IAction.AddEvent(keyb,x,1)
          for k in self.Extras:
          	if   k[0] == "Press":
          		self.IManager.GetInputActions().Find(k[1]).AddEvent(keyb,x,1)
          	elif k[0] == "Release":
          		self.IManager.GetInputActions().Find(k[1]).AddEvent(keyb,x,0)
          	else:
          		print "ERROR : '",k[0],"' is not defined yet!"
          self.KeyBounded.append(x)
          self.IManager.SetInputActionsSet("MenuRedefine")
          self.wActionKeys.SetText(str(self.KeyBounded))
          self.RecalcLayout()
          self.EndDefineKey()

  def SuprMenuItem(self):
    if self.ReadyToEscape:
      self.IManager.SetInputActionsSet("Default")
      self.IAction.RemoveAllEvents()
      for k in self.Extras:
        if   k[0] == "Press":
          self.IManager.GetInputActions().Find(k[1]).RemoveAllEvents()
        elif k[0] == "Release":
          self.IManager.GetInputActions().Find(k[1]).RemoveAllEvents()
        else:
          print "ERROR : '",k[0],"' is not defined yet!"
      
      self.KeyBounded=[]
      self.wActionKeys.SetText("")
      self.wActionKeys.SelectionFilterUpdated=0
      self.wActionKeys.FilterUpdated=0
      self.RecalcLayout()
      self.IManager.SetInputActionsSet("Menu")
    self.ReadyToEscape = 1

  def SetStatusText(self,text):
    self.Parent.SetStatusText(text)
    nvda.SpeakText(text)

  def FinalRelease(self):
    self.Parent=None




MOUSE_CONTROLS = ["RightButton","LeftButton","MiddleButton","OtherButton"]

class B_KeybListWidget(ListWidget.B_ListWidget):
  def __init__(self,Parent,Menudesc,StackMenu,VertPos=0):
    ListWidget.B_ListWidget.__init__(self,Parent,Menudesc,StackMenu,VertPos)
    self.StatusText=BUIx.B_TextWidget(self,"Status",MenuText.GetMenuText(DefInfoText),ScorerWidgets.font_server,"..\\..\\Data\\Letras menu peq.bmp")
    self.StatusText.SetColor(252,247,167)
    self.StatusText.SetAlpha(1)
    self.AddLabel(self.StatusText,0.5,25,BUIx.B_Widget.B_LAB_HCenter,BUIx.B_Widget.B_LAB_Bottom,
                  BUIx.B_Widget.B_FR_HRelative,BUIx.B_Widget.B_LAB_HCenter,
                  BUIx.B_Widget.B_FR_AbsoluteTop,BUIx.B_Widget.B_FR_Top)
    self.DownArrow.SetAlpha(1) # Parche, no funciona la llamada a AdjustScrollArrows() en AddMenuElement(),
                            
                               # hasta que lo averige.
    self.SetClipDraw(1)
    self.SetDrawFunc(self.Draw)

  def __del__(self):
    #print "B_KeybListWidget.B_KeybListWidget.__del__()"
    SaveListConfig()
    if AdditionalKeysCallBack:
       AdditionalKeysCallBack()
    ListWidget.B_ListWidget.__del__(self)

  def Draw(self,x,y,time):
    #pdb.set_trace()
    self.SetClipDraw(1)
    self.DefDraw(x,y,time)

  def SetStatusText(self,text):
    self.StatusText.SetText(text)
    self.RecalcLabelLayout(BUIx.B_Widget.B_LAB_HCenter,BUIx.B_Widget.B_LAB_Bottom)


  def FinalRelease(self):
    ListWidget.B_ListWidget.FinalRelease(self)

def SaveReleaseKey(cfgfile,Action,key,adaction,device):
          text='Bladex.AssocKey("%s","%s","%s",ON_RELEASE)\n'%(adaction,device,key)
          cfgfile.write(text)

def NewAction(cfgfile,Action,key,adaction,device):

          text='Bladex.AssocKey("%s","%s","%s")\n'%(adaction,device,key)
          cfgfile.write(text)


def SaveListConfig():
    cfgfile=open('../../Config/Control.py','w')
    cfgfile.write('\n\n# File generated automatically\n')
    cfgfile.write('# DO NOT EDIT: Changes will be lost\n\n\n')

    cfgfile.write('ON_RELEASE=0\n')
    cfgfile.write('ON_PRESS=1	# default\n\n\n\n')

    cfgfile.write('import BInput\n')
    cfgfile.write('InputManager=BInput.GetInputManager()\n')
    cfgfile.write('InputManager.SetInputActionsSet("Default")  # Me aseguro de definir las acciones en el grupo correcto\n\n\n')

    IManager = BInput.GetInputManager()
    oldInputActionsSet = IManager.GetInputActionsSet()
    IManager.SetInputActionsSet("Default")
    IActions=IManager.GetInputActions()
    
    for i in acts.ConfigurableActions:
      IAction=IActions.Find(i[1])
      
      if IAction.Name()=="NULL":
        print "Cant find",self.ActionName
        continue
      
      for j in range(IAction.nInputEvents()):
      	IEvent=IAction.GetnInputEvent(j)
      	IDevice=IEvent.GetDevice()
      	if(IDevice=="Keyboard" or IDevice=="Mouse" or IDevice=="Pad"):
      	  text='Bladex.AssocKey("%s","%s","%s")\n'%(IAction.Name(),IDevice,IEvent.GetKey())
      	  cfgfile.write(text)
      	  for k in i[2]:
      	    if   k[0]=="Release":
      	      SaveReleaseKey(cfgfile,IAction.Name(),IEvent.GetKey(),k[1],IDevice)
      	    elif k[0]=="Press":
      	      NewAction(cfgfile,IAction.Name(),IEvent.GetKey(),k[1],IDevice)
      	    else:
      	      print "ERROR: '"+k[0]+" is not defined!"

    IManager.SetInputActionsSet(oldInputActionsSet)
    
    cfgfile.write('\n# Mouse stuff\nBladex.AssocKey("RotateX","Mouse","X_Axis")\nBladex.AssocKey("RotateY","Mouse","Y_Axis")\n')
    MouseData = Bladex.GetMouseState()
    text = 'Bladex.SetMouseState(%i,%f,%f)\n'%(MouseData[0],MouseData[1],MouseData[2])
    cfgfile.write(text)
    

    cfgfile.write('\n# Have a nice day.\n\n\n')
    cfgfile.close()
