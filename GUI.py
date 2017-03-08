import Tkinter as tk
import ttk as ttk
import ImageTk
import webbrowser

from lib import SkinMapBuilder

ArmorSelections = ['All','Light','Medium','Heavy','Back']

ArmorCategories = ['Light Headgear','Medium Headgear','Heavy Headgear','Light Shoulders','Medium Shoulders','Heavy Shoulders','Light Chest','Medium Chest','Heavy Chest','Light Gloves','Medium Gloves','Heavy Gloves','Light Leggings','Medium Leggings','Heavy Leggings','Light Boots','Medium Boots','Heavy Boots','Light Aquatic Headgear','Medium Aquatic Headgear','Heavy Aquatic Headgear','Back']

FilterArmorAll = xrange(0,len(ArmorCategories))
FilterLight = [0,3,6,9,12,15,18]
FilterMedium = [1,4,7,10,13,16,19]
FilterHeavy = [2,5,8,11,14,17,20]
FilterBack = [21]

WeaponSelections = ['All','Two-Handed','One-Handed','Off-Hand','Water']

WeaponCategories = ['Axe','Dagger','Mace','Pistol','Sword','Scepter','Focus','Shield','Torch','Warhorn','Greatsword','Hammer','Longbow','Rifle','Short Bow','Staff','Harpoon Gun','Spear','Trident']

FilterWeaponAll = xrange (0,len(WeaponCategories))
FilterMain = [0,1,2,3,4,5]
FilterOff = [6,7,8,9]
FilterTwo = [10,11,12,13,14,15]
FilterWater = [16,17,18]

class FrameHeader (tk.Frame):
	def __init__(self, parent, *args, **kwargs):
		tk.Frame.__init__(self, parent, *args, **kwargs)
		self.parent=parent
		self.main = parent.main
		self.labelHeader = tk.Label (self, text = 'GW2Skins')
		self.labelHeader.pack()

class FrameMain(tk.Frame):
	def __init__(self, parent, *args, **kwargs):
		tk.Frame.__init__(self, parent, *args, **kwargs)
		self.parent=parent
		self.main = parent.main
		self.createMenu()
		self.createSkinDisplay()
	
	def createMenu (self):
		self.frameMenu = FrameMenu(self)
		self.frameMenu.pack(side = tk.LEFT, fill=tk.Y, padx=(10, 60))
	
	def createSkinDisplay(self):
		self.frameSkinDisplay = FrameSkinDisplay(self)
		self.frameSkinDisplay.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

class FrameMenu(tk.Frame):
	def __init__(self, parent, *args, **kwargs):
		tk.Frame.__init__(self, parent, *args, **kwargs)
		self.parent = parent
		self.main = parent.main

		self.createArmorMenu()
		self.createWeaponMenu()
		self.showMenu('Armor')
	
	def createArmorMenu(self):
		self.frameArmorMenu = FrameMenuSelection(self,'Armor')
		self.frameArmorMenu.pack(side=tk.TOP,fill=tk.X)
	
	def createWeaponMenu(self):
		self.frameWeaponMenu = FrameMenuSelection(self,'Weapon')
		self.frameWeaponMenu.pack(side=tk.TOP,fill=tk.X)
	
	def showMenu(self,type):
		if (type == 'Armor'):
			self.frameWeaponMenu.hideSelection()
			self.frameArmorMenu.showSelection()
		elif (type == 'Weapon'):
			self.frameArmorMenu.hideSelection()
			self.frameWeaponMenu.showSelection()

class FrameMenuSelection(tk.Frame):
	def __init__(self, parent, type, *args, **kwargs):
		tk.Frame.__init__(self, parent, *args, **kwargs)
		self.parent = parent
		self.main = parent.main
		self.type = type
		self.selections = []
		if (type == 'Armor'):
			self.selections = ArmorSelections
		elif(type == 'Weapon'):
			self.selections = WeaponSelections
		else:
			raise Exception('undefined Menu selection type {}'.format (self.type))
		
		self.labelMenu = tk.Label(self, text=self.type, justify=tk.LEFT, anchor='w')
		self.labelMenu.bind ("<Button-1>",self.selectCategory)
		self.labelMenu.pack(side=tk.TOP,fill=tk.X)
		self.createMenuItems()
	
	def createMenuItems(self):
		self.frameMenuSelectionLables = tk.Frame(self)
		self.showSelection()
		
		self.labelMenuSelections = []
		for item in self.selections:
			label = tk.Label(self.frameMenuSelectionLables, text=item, justify=tk.LEFT, anchor='w')
			label.parent=self
			label.type = item
			label.bind("<Button-1>",self.selectSubCategory)
			self.labelMenuSelections.append(label)
		for label in self.labelMenuSelections:
			label.pack(side=tk.TOP,fill=tk.X)
	
	def hideSelection(self):
		self.frameMenuSelectionLables.pack_forget()
		
	def showSelection(self):
		self.frameMenuSelectionLables.pack(side=tk.TOP,fill=tk.X,padx=(10, 0))
	
	def selectCategory(self, event):
		self.parent.showMenu(self.type)
		self.parent.parent.frameSkinDisplay.showSkinDisplay(self.type)
		self.parent.parent.frameSkinDisplay.showSubcategory(self.type,'All')
	
	def selectSubCategory(self,event):
		self.parent.parent.frameSkinDisplay.showSubcategory(self.type,event.widget.type)
	
class FrameFilter(tk.Frame):
	def __init__(self, parent, *args, **kwargs):
		tk.Frame.__init__(self, parent, *args, **kwargs)
		self.parent=parent
		self.main = parent.main
		
		self.varFilterString = tk.StringVar()
		self.varFilterString.set('Search...')
		self.varCategoryString = tk.StringVar()
		self.varCategoryString.set('All Types')
		self.varExoFilter = tk.IntVar()
		self.varExoFilter.set(0)
		
		self.entryFilterText = tk.Entry(self,width=20,textvariable=self.varFilterString)
		self.entryFilterText.pack(side=tk.LEFT)
		
		self.exoFilter = tk.Checkbutton(self,text="hide exotic and higher skins", variable=self.varExoFilter, command=self.exoFilterCallback)
		self.exoFilter.pack(side=tk.LEFT, padx = (10,0))
		
		self.comboboxCategory = ttk.Combobox(self,textvariable=self.varCategoryString)
		self.comboboxCategory["state"] = 'readonly'
		self.comboboxCategory.pack(side=tk.RIGHT)
		self.setUpComboBoxValue('Armor')
	
	def setUpComboBoxValue(self,type):
		if (type == 'Armor'):
			self.varCategoryString.set('All Types')
			self.comboboxCategory["values"] = (self.varCategoryString.get(),)+tuple(ArmorCategories)
		elif (type == 'Weapon'):
			self.varCategoryString.set('All Types')
			self.comboboxCategory["values"] = (self.varCategoryString.get(),)+tuple(WeaponCategories)
	
	def exoFilterCallback(self):
		if (self.varExoFilter.get() == 1):
			self.parent.hideExosAndHigher()
		else:
			self.parent.unhideAll()

class FrameSkinDisplay(tk.Frame):
	def __init__(self, parent, *args, **kwargs):
		tk.Frame.__init__(self, parent, *args, **kwargs)
		self.parent=parent
		self.main = parent.main
		
		self.createFilter()
		self.createSkinDisplayMain()
		self.showSkinDisplay('Armor')
	
	def createFilter(self):
		self.frameFilter = FrameFilter(self)
		self.frameFilter.pack(side=tk.TOP, fill=tk.X)
	
	def createSkinDisplayMain(self):
		self.createArmorDisplayMain()
		self.createWeaponDisplayMain()
		self.showSkinDisplay('Armor')
	
	def createArmorDisplayMain(self):
		self.frameArmorDisplayParent = ScrollableFrame(self)
		self.frameArmorDisplayMain = self.frameArmorDisplayParent.scrollableFrame
		
		self.armorDisplays = []
		for category in ArmorCategories:
			skinMapEntryIds = []
			skinMapEntryIds = self.main.skinMap.getEntryIdsByCategory(category)
			frame = SkinTypeDisplayFrame(self.frameArmorDisplayMain,'Armor', category, skinMapEntryIds)
			self.armorDisplays.append(frame)
	
	def createWeaponDisplayMain(self):
		self.frameWeaponDisplayParent = ScrollableFrame(self)
		self.frameWeaponDisplayMain = self.frameWeaponDisplayParent.scrollableFrame
		
		self.weaponDisplays = []
		for category in WeaponCategories:
			skinMapEntryIds = []
			skinMapEntryIds = self.main.skinMap.getEntryIdsByCategory(category)
			frame = SkinTypeDisplayFrame(self.frameWeaponDisplayMain,'Weapon', category, skinMapEntryIds)
			self.weaponDisplays.append(frame)
	
	def showSkinDisplay(self,type):
		if (type == 'Armor'):
			self.frameWeaponDisplayParent.pack_forget()
			self.frameArmorDisplayParent.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
		elif (type == 'Weapon'):
			self.frameArmorDisplayParent.pack_forget()
			self.frameWeaponDisplayParent.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
		else :
			raise Exception('undefined SkinDisplay selection type {}'.format (type))
		self.showSubcategory(type,'All')

	def showSubcategory(self,type,subType):
		filter = []
		if (type == 'Armor'):
			i=0
			if (subType == 'All'):
				filter = FilterArmorAll
			elif (subType == 'Light'):
				filter = FilterLight
			elif (subType == 'Medium'):
				filter = FilterMedium
			elif (subType == 'Heavy'):
				filter = FilterHeavy
			elif (subType == 'Back'):
				filter = FilterBack
			else:
				raise Exception('undefined SkinDisplay sub selection type {}'.format (subType))
			
			for frame in self.armorDisplays:
				frame.pack_forget()
				if i in filter:
					frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
				i += 1
		elif (type == 'Weapon'):
			i=0
			if (subType == 'All'):
				filter = FilterWeaponAll
			elif (subType == 'Two-Handed'):
				filter = FilterTwo
			elif (subType == 'One-Handed'):
				filter = FilterMain
			elif (subType == 'Off-Hand'):
				filter = FilterOff
			elif (subType == 'Water'):
				filter = FilterWater
			else:
				raise Exception('undefined SkinDisplay sub selection type {}'.format (subType))
			
			for frame in self.weaponDisplays:
				frame.pack_forget()
				if i in filter:
					frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
				i += 1
		else :
			raise Exception('undefined SkinDisplay selection type {}'.format (type))
	
	def hideExosAndHigher(self):
		for frame in self.armorDisplays:
			frame.setHideFlags('Exotic')
			frame.setHideFlags('Ascended')
			frame.setHideFlags('Legendary')
			frame.showUnhidden()
		for frame in self.weaponDisplays:
			frame.setHideFlags('Exotic')
			frame.setHideFlags('Ascended')
			frame.setHideFlags('Legendary')
			frame.showUnhidden()
		
	def unhideAll(self):
		for frame in self.armorDisplays:
			frame.unsetHideFlags()
			frame.showUnhidden()
		for frame in self.weaponDisplays:
			frame.unsetHideFlags()
			frame.showUnhidden()
			
class SkinTypeDisplayFrame(tk.Frame):
	def __init__(self, parent, type, name, skinMapEntryIds, *args, **kwargs):
		tk.Frame.__init__(self, parent, *args, **kwargs)
		self.parent = parent
		self.main = parent.main
		self.name = name
		self.type = type
		self.skinMapEntryIds = skinMapEntryIds
		self.iconLabels = []
		
		self.labelSkinDisplayType=tk.Label(self, text=self.name,justify=tk.LEFT, anchor='w')
		self.iconsFrame=tk.Frame(self)
		self.iconsFrame.main = self.main
		self.iconsFrame.parent = self.parent
		self.iconsFrame.popUpWindow = tk.Frame(self)
		self.iconsFrame.popUpWindow.skinLabel = tk.Label(self.iconsFrame.popUpWindow)
		self.iconsFrame.popUpWindow.linkLabel = tk.Label(self.iconsFrame.popUpWindow)
		self.iconsFrame.popUpWindow.itemLabel = tk.Label(self.iconsFrame.popUpWindow)
		self.iconsFrame.popUpShown = False
		
		self.pack(side=tk.TOP, fill=tk.X, expand=True)
		self.labelSkinDisplayType.pack(side=tk.TOP, fill=tk.X, anchor='nw')
		self.iconsFrame.pack(side=tk.TOP, anchor= 'w')
		self.addIcons()

	def addIcons(self):
		#width=64, height=64
		pos = 0
		for skinId in self.skinMapEntryIds:
			skinMapEntry = self.main.skinMap.getSkinMapEntry(skinId)
			image = ImageTk.PhotoImage(skinMapEntry.iconPIL)
			label = LabelIcon(self.iconsFrame, image, skinId,borderwidth=3)
			if (skinMapEntry.isBuyable and not(skinMapEntry.isOwned)):
				label.config(bg = '#50DB00')
			self.iconLabels.append(label)
			self.showUnhidden()
	
	def setHideFlags(self,rarity):
		for label in self.iconLabels:
			label.setHideReasonRarity(rarity)
	
	def unsetHideFlags(self):
		for label in self.iconLabels:
			label.unsetHideFlag()
	
	def showUnhidden(self):
		pos = 0
		for label in self.iconLabels:
			label.grid_forget()
		for label in self.iconLabels:
			if (not label.hide):
				#grid n*10
				label.grid(row=pos/10,column=pos%10, padx=0,pady=0)
				pos += 1
		
class LabelIcon(tk.Label):
	def __init__(self, parent, image, skinId, *args, **kwargs):
		tk.Label.__init__(self, parent, image=image, *args, **kwargs)
		self.parent = parent
		self.main = parent.main
		self.image = image
		self.skinId = skinId
		self.link = ""
		self.hide = False
		#self.bind("<Enter>", self.onEnter)
		#self.bind("<Leave>", self.onLeave)
		self.bind ("<Button-1>",self.showPopUpWindow)
		self.bind ("<Button-3>",self.closePopUpWindow)
	
	#def onEnter(self,event):
	#	self.parent.popUpWindow.config (text='Show id {} blaaaaaaaaaaaaaaaaaaaaaaaaaaa\nblaa\nbla\nbla\nbla'.format(str(self.skinId)))
	#	self.parent.popUpWindow.place(x=self.winfo_x()+event.x,y=self.winfo_y()+event.y,bordermode="outside")
	
	#def onLeave(self,event):
	#	self.parent.popUpWindow.place_forget()
	
	def setHideReasonRarity(self, rarity):
		if (rarity == SkinMapBuilder.Rarities[self.main.skinMap.getSkinMapEntry(self.skinId).rarity]):
			self.hide = True
	
	def unsetHideFlag (self):
		self.hide = False
		
	def openLink(self,event):
		if (self.link <> ""):
			webbrowser.open_new(self.link)
	
	def showPopUpWindow(self,event):
		if (self.parent.popUpShown == True):
			self.closePopUpWindow(event)
		
		skinName = self.main.skinMap.getSkin(self.skinId).get("name","unkownSkin")
		self.link = self.main.skinMap.getSkinLink(self.skinId)
		(cheapest, freeList) = self.main.skinMap.getCheapestItems(self.skinId)
		itemStr = ""
		if (cheapest > 0):
			itemStr += "cheapest item on TP: \n"
			itemStr += self.main.skinMap.getItemDescription(cheapest)
		
		if (len (freeList) > 0):
			if (cheapest > 0):
				itemStr += "\n\n"
			itemStr += "not buyable items:"
			for itemId in freeList:
				itemStr += "\n{}".format(self.main.skinMap.getItemDescription(itemId))
				#itemStr += " Link: ".format(self.main.skinMap.getItemLink(itemId))
		
		self.parent.popUpWindow.skinLabel = tk.Label(self.parent.popUpWindow,text='{}'.format(skinName))
		self.parent.popUpWindow.linkLabel = tk.Label(self.parent.popUpWindow,text='GW2-Wiki',fg='blue',cursor = "hand2")
		self.parent.popUpWindow.itemLabel = tk.Label(self.parent.popUpWindow,text='\n{}'.format(itemStr),justify=tk.LEFT)
		
		#self.main.bind ("<Escape>",self.closePopUpWindow)
		self.parent.popUpWindow.bind ("<Button-3>",self.closePopUpWindow)
		self.parent.popUpWindow.skinLabel.bind("<Button-3>",self.closePopUpWindow)
		self.parent.popUpWindow.linkLabel.bind("<Button-3>",self.closePopUpWindow)
		self.parent.popUpWindow.itemLabel.bind("<Button-3>",self.closePopUpWindow)
		
		self.parent.popUpWindow.linkLabel.bind("<Button-1>",self.openLink)
		
		self.parent.popUpWindow.skinLabel.pack(side=tk.TOP)	
		self.parent.popUpWindow.linkLabel.pack(side=tk.TOP)	
		self.parent.popUpWindow.itemLabel.pack(side=tk.TOP, fill=tk.BOTH, expand=True, anchor='nw')	
		
		self.parent.popUpWindow.place(x=self.winfo_x()+event.x,y=self.winfo_y()+event.y) #,bordermode="outside"
		self.parent.popUpShown = True
	
	def closePopUpWindow(self,event):
		self.link = ""
		self.parent.popUpWindow.linkLabel.unbind("<Button-1>")
		
		self.parent.popUpWindow.skinLabel.pack_forget()
		self.parent.popUpWindow.linkLabel.pack_forget()
		self.parent.popUpWindow.itemLabel.pack_forget()
		self.parent.popUpWindow.place_forget()
		self.parent.popUpShown = False
		
class ScrollableFrame(tk.Frame):
	def __init__(self, parent, *args, **kwargs):
		tk.Frame.__init__(self, parent, *args, **kwargs)
		self.parent = parent
		self.main = parent.main
		self.canvas = tk.Canvas(self)
		self.scrollableFrame = tk.Frame(self.canvas)
		self.scrollableFrame.main = parent.main
		self.scrollbar=tk.Scrollbar(self,orient='vertical',command=self.canvas.yview)
		self.canvas.configure(yscrollcommand=self.scrollbar.set)
		self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
		self.canvas.pack(side=tk.LEFT, fill=tk.BOTH,expand=True)
		self.frame_id = self.canvas.create_window((0,0),window=self.scrollableFrame,anchor='nw')
		self.bind("<Configure>",self.scrollfunction)
		
	def scrollfunction(self,event):
		self.canvas.configure(scrollregion=self.canvas.bbox("all"))
		self.canvas.itemconfig(self.frame_id, width=event.width)

class MainApplication(tk.Frame):
	def __init__(self, *args, **kwargs):
		self.main = self
		self.root = tk.Tk()
		tk.Frame.__init__(self, *args, **kwargs)
		self.parent = self.root
		self.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
		self.loadingLabel = tk.Label(self, text='Loading')
		self.configure(width=200,height=200)
		self.loadingLabel.pack()
		self.after(100,self.loadGUI)
		
	def loadGUI (self):
		self.skinMap = SkinMapBuilder.SkinMap()
		
		self.loadingLabel.pack_forget()
		
		self.frameHeader=FrameHeader(self)
		self.frameHeader.pack(side=tk.TOP, fill=tk.BOTH)
		
		self.frameMain = FrameMain(self) 
		self.frameMain.pack(side=tk.TOP, fill=tk.BOTH, expand=True)


if __name__ == "__main__":
	mainWindow = MainApplication()
	mainWindow.root.mainloop()