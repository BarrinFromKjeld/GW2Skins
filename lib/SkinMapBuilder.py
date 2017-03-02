import json
import time
from PIL import Image
from io import BytesIO

import FileAccess
import XHRRequest
 
baseUrlSkins    = 'https://api.guildwars2.com/v2/skins'
baseUrlItems    = 'https://api.guildwars2.com/v2/items'
baseUrlPrices   = 'https://api.guildwars2.com/v2/commerce/prices'
baseUrlAccounts = 'https://api.guildwars2.com/v2/account/skins'
defaultParams   = {'lang': 'en'}
defaultHeaders  = {}

updFileName     = './res/.lastUpdated.lck'
skinFileName    = './res/.skins.json'
skinIdFileName  = './res/.skinIdList.json'
itemFileName    = './res/.items.json'
itemIdFileName  = './res/.itemIdList.json'
priceFileName   = './res/.prices.json'
priceIdFileName = './res/.priceIdList.json'
iconLocation    = './res/'
apiKeyFile      = './api.key'

XHRChunkNumber    = 100
#XHRTPChunkNumber = 50

iconSize = (64,64)

##########################################
#          Universal Functions           #
##########################################
def addUnknownObjectsViaXHRandSave(unknownIds, objects, url, fileName, params=defaultParams, header=defaultHeaders , singleRequest=False):
	if (len(unknownIds) != 0):
		subsets = [unknownIds[i:i + XHRChunkNumber] for i in xrange(0, len(unknownIds), XHRChunkNumber)]
		nr = 0
		aim = len(subsets)
		print 'Request url: {}'.format(url)
		for subset in subsets:
			nr = nr + 1
			print 'Request subset {} of {}'.format(nr,aim)
			objectToAdd = XHRRequest.getJSONObjectsViaXHRbyIdList(url,subset,singleRequest=singleRequest)
			for object in objectToAdd:
				objects.append(object)
			FileAccess.writeJSONToFile(fileName,objects) #make safer e.g. via renameing

def getCommonIds (idList1,idList2):
	return list(set(idList1).intersection(idList2))

def getUnknownIds(idList1,idList2):
	return list(set(idList1) - set(idList2))

def getKnownIds(objectList):
	knownIds = []
	for object in objectList:
		try:
			knownIds.append(object["id"])
		except:
			print 'object {} has no id'.format(str(object))
			raise Exception ('ObjectWithoutId')
	return knownIds

def buildIdIndex (dictionary):
	index = {}
	idList = []
	indexList = []
	indexNr = 0
	
	for obj in dictionary:
		if ('id' in obj):
			idList.append(str(obj["id"]))
			indexList.append(indexNr)
		else:
			continue
		indexNr += 1
	index = dict(zip(idList, indexList))
	return index

def getIdList (url,file,forceUpdate=False):
	ids = []
	if (not(forceUpdate)):
		ids = FileAccess.getObjectsFromJSONFile(file)
	else:
		ids = XHRRequest.getJSONObjectsViaXHR(url)
		FileAccess.writeJSONToFile(file,ids)
	return ids

##########################################
#             Skin Functions             #
##########################################
def getSkinIdList(forceUpdate=False):
	return getIdList(baseUrlSkins,skinIdFileName,forceUpdate)

def getSkins(forceUpdate=False):
	print "load Skins"
	skinIdList = getSkinIdList(forceUpdate)
	skins = FileAccess.getObjectsFromJSONFile(skinFileName)
	knownIds = getKnownIds(skins)
	unknownIds = getUnknownIds(skinIdList, knownIds)
	addUnknownObjectsViaXHRandSave(unknownIds, skins, baseUrlSkins, skinFileName)
	return skins

##########################################
#             Item Functions             #
##########################################
def getItemIdList(forceUpdate=False):
	return getIdList(baseUrlItems,itemIdFileName,forceUpdate)

def getItems(forceUpdate=False):
	print "load Items"
	itemIdList = getItemIdList(forceUpdate)
	items = FileAccess.getObjectsFromJSONFile(itemFileName)
	knownIds = getKnownIds(items)
	unknownIds = getUnknownIds(itemIdList, knownIds)
	addUnknownObjectsViaXHRandSave(unknownIds, items, baseUrlItems, itemFileName)
	return items

def buildItemSkinMap(items):
	itemSkinMap = {}
	itemIds = []
	skinIds = []
	for item in items:
		if ('id' in item):
			itemIds.apend(item["id"])
			if ('default_skin' in item):
				skinIds.append(item["default_skin"])
			elif (item.get('details',{}).get('type','') == 'Transmutation'):
				skinIds.append(item.get('details',{}).get('skins'))
			else:
				continue
		else:
			continue
	itemSkinMap = dict(zip(itemIds, values))
	return itemSkinMap

##########################################
#             Price Functions            #
##########################################
def getPriceIdList(forceUpdate=False):
	return getIdList(baseUrlPrices,priceIdFileName,forceUpdate)

def addPricesViaXHRandSave (unknownIds, prices):
	addUnknownObjectsViaXHRandSave(unknownIds, prices, baseUrlPrices, priceFileName, params={}, singleRequest=True)

def getAllPrices(forceUpdate=False):
	print "load all Prices"
	priceIdList = getPriceIdList(forceUpdate)
	prices = FileAccess.getObjectsFromJSONFile(priceFileName)
	knownIds = getKnownIds(prices)
	unknownIds = getUnknownIds(priceIdList, knownIds)
	addPricesViaXHRandSave(unknownIds, prices)
	return prices

def getPricesForItemIds(itemIds, updateAll=False):
	print "load Prices"
	prices = []
	if (not (updateAll)):
		prices = FileAccess.getObjectsFromJSONFile(priceFileName)
	
	knownIds = getKnownIds(prices)
	unknownIds = getUnknownIds (itemIds,knownIds)
	priceIdList = getPriceIdList(updateAll)
	commonIds = getCommonIds (unknownIds,priceIdList)
		
	addPricesViaXHRandSave(commonIds,prices)

	return prices

##########################################
#                SkinIndex               #
##########################################
class SkinMapEntry(object):
	def __init__(self, skinId):
		self.skinId = skinId
		self.id = skinId
		self.name = ''
		self.itemIds = []
		self.isNotTradable = []
		self.type = ''
		self.subtype = ''
		self.subsubtype = ''
		self.restrictions = []
		self.iconPath = iconLocation
		self.iconURL = ''
		self.iconPIL = {}
		self.iconLoaded = False
		self.isBuyable = False
		self.isOwned = False
	
	def loadIcon(self):
		if (self.iconURL == ''):
			return self.iconLoaded
		
		self.loadIconFromFile()
		if (not(self.iconLoaded)):
			self.loadIconViaXHR()
			
		self.iconPIL.thumbnail(iconSize, Image.ANTIALIAS) #make all 64x64

		if (not(self.isOwned)):
			self.iconPIL = self.iconPIL.convert('L',palette="ADAPTIVE") # convert image to mono-chrome if the account doesn't have it
			#self.iconPIL = Image.alpha(self.iconPIL, 0.5) #pseudo code
		return self.iconLoaded
	
	def loadIconFromFile(self):
		try:
			content = FileAccess.getBinFromFile(self.iconPath)
			if (content == b''):
				return
			self.iconPIL = Image.open(BytesIO(content))
			self.iconLoaded = True
		except IOError as e:
			print "Error while loading file {}: {}".format(self.iconPath,str(e))
			self.iconLoaded = False
	
	def loadIconViaXHR(self):
		print "load skin {} via XHR".format(str(self.skinId))
		content=b''
		try:
			content = XHRRequest.getBinViaXHR(self.iconURL,{},{})
			self.iconPIL = Image.open(BytesIO(content))
			self.iconLoaded = True
		except Exception as e:
			print "Error during loadIconViaXHR {}".format(str(e))
			self.iconLoaded = False
			return
		
		try:
			FileAccess.writeBinToFile(self.iconPath,content)
		except IOError as e:
			print "Error when saving icon to {}: {}".format(self.iconPath,str(e))


class SkinMap(object):
	def __init__(self):
		self.map = []
		self.items = []
		self.itemIdIndex = []
		self.skins = []
		self.skinIdIndex = []
		self.ownedSkinIdList = []
		self.prices = []
		self.priceIdIndex = {}
		self.skinMapIdIndex = {}
		self.mappedItems = 0
		self.accountBoundItemsNr = 0
		self.unboundSkinsNr = 0
		self.multiSkinItemsNr = 0
		self.deleted = 0
		self.notInSkins = 0
		self.buyableSkinItemIds = []
		self.typeDict = {
			'Light Headgear': {'type': 'Armor','subtype': 'Helm', 'subsubtype': 'Light'},
			'Medium Headgear': {'type': 'Armor','subtype': 'Helm', 'subsubtype': 'Medium'},
			'Heavy Headgear': {'type': 'Armor','subtype': 'Helm', 'subsubtype': 'Heavy'},
			'Light Shoulders': {'type': 'Armor','subtype': 'Shoulders', 'subsubtype': 'Heavy'},
			'Medium Shoulders': {'type': 'Armor','subtype': 'Shoulders', 'subsubtype': 'Medium'},
			'Heavy Shoulders': {'type': 'Armor','subtype': 'Shoulders', 'subsubtype': 'Heavy'},
			'Light Chest': {'type': 'Armor','subtype': 'Coat', 'subsubtype': 'Light'},
			'Medium Chest': {'type': 'Armor','subtype': 'Coat', 'subsubtype': 'Medium'},
			'Heavy Chest': {'type': 'Armor','subtype': 'Coat', 'subsubtype': 'Heavy'},
			'Light Gloves': {'type': 'Armor','subtype': 'Gloves', 'subsubtype': 'Light'},
			'Medium Gloves': {'type': 'Armor','subtype': 'Gloves', 'subsubtype': 'Medium'},
			'Heavy Gloves': {'type': 'Armor','subtype': 'Gloves', 'subsubtype': 'Heavy'},
			'Light Leggings': {'type': 'Armor','subtype': 'Leggings', 'subsubtype': 'Light'},
			'Medium Leggings': {'type': 'Armor','subtype': 'Leggings', 'subsubtype': 'Medium'},
			'Heavy Leggings': {'type': 'Armor','subtype': 'Leggings', 'subsubtype': 'Heavy'},
			'Light Boots': {'type': 'Armor','subtype': 'Boots', 'subsubtype': 'Light'},
			'Medium Boots': {'type': 'Armor','subtype': 'Boots', 'subsubtype': 'Medium'},
			'Heavy Boots': {'type': 'Armor','subtype': 'Boots', 'subsubtype': 'Heavy'},
			'Light Aquatic Headgear': {'type': 'Armor','subtype': 'HelmAquatic', 'subsubtype': 'Light'},
			'Medium Aquatic Headgear': {'type': 'Armor','subtype': 'HelmAquatic', 'subsubtype': 'Medium'},
			'Heavy Aquatic Headgear': {'type': 'Armor','subtype': 'HelmAquatic', 'subsubtype': 'Heavy'},
			'Back': {'type': 'Back','subtype': '', 'subsubtype': ''},
			'Axe': {'type': 'Weapon','subtype': 'Axe', 'subsubtype': ''},
			'Dagger': {'type': 'Weapon','subtype': 'Dagger', 'subsubtype': ''},
			'Mace': {'type': 'Weapon','subtype': 'Mace', 'subsubtype': ''},
			'Pistol': {'type': 'Weapon','subtype': 'Pistol', 'subsubtype': ''},
			'Sword': {'type': 'Weapon','subtype': 'Sword', 'subsubtype': ''},
			'Scepter': {'type': 'Weapon','subtype': 'Scepter', 'subsubtype': ''},
			'Focus': {'type': 'Weapon','subtype': 'Focus', 'subsubtype': ''},
			'Shield': {'type': 'Weapon','subtype': 'Shield', 'subsubtype': ''},
			'Torch': {'type': 'Weapon','subtype': 'Torch', 'subsubtype': ''},
			'Warhorn': {'type': 'Weapon','subtype': 'Warhorn', 'subsubtype': ''},
			'Greatsword': {'type': 'Weapon','subtype': 'Greatsword', 'subsubtype': ''},
			'Hammer': {'type': 'Weapon','subtype': 'Hammer', 'subsubtype': ''},
			'Longbow': {'type': 'Weapon','subtype': 'Longbow', 'subsubtype': ''},
			'Rifle': {'type': 'Weapon','subtype': 'Rifle', 'subsubtype': ''},
			'Short Bow': {'type': 'Weapon','subtype': 'Shortbow', 'subsubtype': ''},
			'Staff': {'type': 'Weapon','subtype': 'Staff', 'subsubtype': ''},
			'Harpoon Gun': {'type': 'Weapon','subtype': 'Speargun', 'subsubtype': ''},
			'Spear': {'type': 'Weapon','subtype': 'Spear', 'subsubtype': ''},
			'Trident': {'type': 'Weapon','subtype': 'Trident', 'subsubtype': ''}
		}
	
		updateNecessary = checkLastUpdated(86400)
	
		self.items = getItems(updateNecessary)
		self.itemIdIndex = buildIdIndex(self.items)
	
		self.skins = getSkins(updateNecessary)
		self.skinIdIndex = buildIdIndex(self.skins)
		
		self.loadOwnedSkins()
		
		self.buildMap()
		
		self.loadIcons()
		
		self.buyableSkinItemIds = self.getBuyableItemIds()
		self.prices = getPricesForItemIds(self.buyableSkinItemIds,updateNecessary)
		self.priceIdIndex = buildIdIndex(self.prices)
	
		self.printStats()
		
	def getBuyableItemIds(self):
		buyableItemIds = []
		for skinMapEntry in self.map:
			if (skinMapEntry.isBuyable):
				itemNr = len (skinMapEntry.itemIds)
				flagNr = len (skinMapEntry.isNotTradable)
				if (itemNr <> flagNr):
					raise Exception('Error at skinMapEntry {}. itemNr({}) <> flagNr({})'.format(skinMapEntry.skinId,itemNr,flagNr))
				for number in xrange(itemNr):
					if (not(skinMapEntry.isNotTradable[number])):
						buyableItemIds.append(skinMapEntry.itemIds[number])
		return buyableItemIds

	def buildMap(self):
		print "build item-skin-map"
		map = []
		skinIds = []
		isNotTradable = False
		itemId = 0
		knownSkinIds = getKnownIds(self.skins)
		
		for item in self.items:
			flags = item.get("flags",[])
			if ('DeleteWarning' in flags):
				self.deleted += 1
			#api "prices" refer to oldest version of items so we need to consider deleted items...
			#e.g. legendaries
			#	continue
			
			itemId = item["id"]
			skinIds = []
			if ('default_skin' in item):
				skinIds.append(item["default_skin"])
			elif (item.get('details',{}).get('type','') == 'Transmutation'):
				skinIds = item.get('details',{}).get('skins')
				if (len(skinIds) > 1):
					self.multiSkinItemsNr += 1
			else:
				continue
			
			isNotTradable = 'AccountBound' in flags or 'SoulbindOnAcquire' in flags or 'MonsterOnly' in flags
			for skinId in skinIds:
				if (not (skinId in knownSkinIds)):
					self.notInSkins += 1
					continue
				found = False
				for skinMapEntry in map:
					if (skinMapEntry.skinId == skinId):
						#print 'adding itemId {} to skinId {}'.format(itemId,skinId)
						skinMapEntry.itemIds.append(itemId)
						skinMapEntry.isNotTradable.append(isNotTradable)
						self.mappedItems += 1
						if (isNotTradable):
							self.accountBoundItemsNr += 1
						elif (not(skinMapEntry.isBuyable)):
							skinMapEntry.isBuyable = True
							self.unboundSkinsNr += 1
						found = True
						break
				if (not(found)):
					#print 'adding skinId {} with itemId {}'.format(skinId,itemId)
					skinMapEntry = SkinMapEntry(skinId)
					skinMapEntry.itemIds.append(itemId)
					skinMapEntry.isNotTradable.append(isNotTradable)
					#print "skinId: {}, self.skinIdIndex[skinId]: {}".format(str(skinId), self.skinIdIndex[str(skinId)])
					skin = self.skins[self.skinIdIndex[str(skinId)]]
					skinMapEntry.name = skin.get('name','')
					skinMapEntry.type = skin.get('type','')
					if ('details' in skin):
						skinDetails = skin.get('details',{})
						skinMapEntry.subtype = skinDetails.get('type','')
						if (skinMapEntry.type == 'Armor'):
							skinMapEntry.subsubtype = skinDetails.get('weight_class','')
					skinMapEntry.restrictions = skin.get('restrictions',[])
					skinMapEntry.iconURL = skin.get('icon','')
					skinMapEntry.iconPath += str(skinId)
					skinMapEntry.iconPath += '.png'
					if (skinId in self.ownedSkinIdList):
						skinMapEntry.isOwned = True
					if (isNotTradable):
						self.accountBoundItemsNr += 1
					elif (not(skinMapEntry.isBuyable)):
						skinMapEntry.isBuyable = True
						self.unboundSkinsNr += 1
					
					map.append(skinMapEntry)
					self.mappedItems += 1
		self.map = sorted (map, key=lambda skinMapEntry: skinMapEntry.name)
		self.buildMapIdIndex()

	def buildMapIdIndex (self):
		print "indexing Map"
		index = {}
		idList = []
		indexList = []
		indexNr = 0
		for skinMapEntry in self.map:
			idList.append(str(skinMapEntry.skinId))
			indexList.append(indexNr)
			indexNr += 1
		self.skinMapIdIndex = dict(zip(idList, indexList))

	def loadIcons (self):
		print "Load Icons"
		allLoaded = True
		for skinMapEntry in self.map:
			allLoaded &= skinMapEntry.loadIcon()
		return allLoaded

	def printStats(self):
		print 'Nr of available Items:  {}'.format(len(self.items))
		print 'Nr of available Skins:  {}'.format(len(self.skins))
		print 'Nr of owned Skins:      {}'.format(len(self.ownedSkinIdList))
		print 'Nr of indexed Items:    {}'.format(self.mappedItems)
		print 'Nr of indexed Skins:    {}'.format(len(self.map))
		print 'Nr of AccBound Items:   {}'.format(self.accountBoundItemsNr)
		print 'Nr of buyable Skins:    {}'.format(self.unboundSkinsNr)
		print 'Nr of multi-skin-items: {}'.format(self.multiSkinItemsNr)
		print 'Nr of deleted items:    {}'.format(self.deleted)
		print 'Nr of itemNotInSkin:    {}'.format(self.notInSkins)
		print 'Nr of unboundSkinItems: {}'.format(len(self.buyableSkinItemIds))
		print 'Nr of prices:           {}'.format(len(self.prices))

	def getEntryIdsByCategory(self,category):
		typeInfo = self.typeDict.get(category,{})
		if (typeInfo == {}):
			raise Exception ('Category not found in typeDict')
		return self.getEntryIdsByType (typeInfo["type"],typeInfo["subtype"],typeInfo["subsubtype"])
	
	def getEntryIdsByType(self,type,subtype,subsubtype):
		ids = []
		for skinMapEntry in self.map:
			if (skinMapEntry.type == type and skinMapEntry.subtype == subtype and skinMapEntry.subsubtype == subsubtype):
				ids.append(skinMapEntry.skinId)
		return ids
	
	def getSkinMapEntry(self,skinId):
		try:
			return self.map[self.skinMapIdIndex[str(skinId)]]
		except:
			return {}
	
	def getPrice(self,id):
		try:
			return self.prices[self.priceIdIndex[str(id)]]
		except:
			return {}
	
	def getItem(self,id):
		try:
			return self.items[self.itemIdIndex[str(id)]]
		except:
			return {}

	def getSkin(self,id):
		try:
			return self.skins[self.skinIdIndex[str(id)]]
		except:
			return {}
	
	def getSellPrice(self,id):
		return self.getPrice(id).get("sells",{}).get("unit_price",0)
		
	def getBuyPrice(self,id):
		return self.getPrice(id).get("buys",{}).get("unit_price",0)
	
	def formatPrice (self,price):
		g = price / 10000
		s = (price - g*10000) / 100
		c = price - g*10000 - s*100
		str = ""
		if (g > 0):
			str += "{}G".format(g)
			if (s>0 or c>0):
				str += " "
		if (s > 0):
			if (s<10 and g>0):
				str += "0"
			str += "{}S".format(s)
			if (c>0):
				str += " "
		if (c > 0):
			if (c<10 and (s>0 or g>0)):
				str += "0"
			str += "{}C".format(c)
		
		return str
	
	def getCheapestItems (self,skinId):
		skinEntry = self.getSkinMapEntry(skinId)
		cheapestPrice = 100000001 #maximum price is 10000G 00S 00C
		cheapestItemId = -1
		freeItems = []
		
		for itemId in skinEntry.itemIds:
			itemPrice = self.getSellPrice(itemId) 
			if (itemPrice == 0): #no price, assuming karma skin
				freeItems.append (itemId)
			elif (itemPrice > 0 and itemPrice < cheapestPrice):
				cheapestPrice = itemPrice
				cheapestItemId = itemId
		
		if (cheapestItemId == -1 and len(freeItems) == 0):
			raise Exception ("neither free nor buyable item found")
		
		return (cheapestItemId, freeItems)

	def getSkinLink (self,skinId):
		name = self.getSkin(skinId).get("name","")
		if (name == ""):
			return "No Link"
		return "https://wiki.guildwars2.com/wiki/{}".format(name) #_(skin)
		
	def getItemLink (self,itemId):
		name = self.getItem(itemId).get("name","")
		if (name == ""):
			return "No Link"
		return "https://wiki.guildwars2.com/wiki/{}".format(name)
	
	def getItemDescription(self,itemId):
		item = self.getItem(itemId)
		if (item == {}):
			return ""
		desc = ""
		desc += "{} - price: ".format(item.get("name"))
		price = self.getSellPrice(itemId)
		if (price == 0):
			desc += "no price available"
		else:
			desc += "{}".format(self.formatPrice(price))
		return desc
	
	def loadOwnedSkins (self):
		print 'load skins owned by the account'
		apiKey = FileAccess.getStrFromFile (apiKeyFile)
		if (apiKey == ''):
			print 'No API-Key specified'
			return
		authHeader = {'Authorization': 'Bearer {}'.format(apiKey)}
		self.ownedSkinIdList = XHRRequest.getJSONObjectsViaXHR (baseUrlAccounts,headers=authHeader)
		if (len(self.ownedSkinIdList) == 0):
			print 'ownedSkinIdList empty. Either API key is wrong, or you never created a character'
		

##########################################
#              Misc Functions            #
##########################################
def checkLastUpdated(minTimeDiff):
	now = time.time()
	lastUpdated = 0
	try:
		with open (updFileName,'r') as file:
			try:
				lastUpdated = float(file.read())
			except Exception as e:
				lastUpdated = 0
				#print '{}'.format(str(e))
		if (now - lastUpdated > minTimeDiff): # daily updates
			with open (updFileName,'w') as file:
				#print "truncate {} and update with current timestamp {}".format(file, str(now))
				file.truncate()
				file.write(str(now))
				return True
	except IOError as e:
		print '{}'.format(str(e))
		if (e.errno == 2): #File not found
			try:
				with open (updFileName,'w') as file:
					file.write(str(now))
				return True
			except Exception as  e:
				print 'Cannot create {}\n{}'.format(updFileName,str(e))
				sys.exit (-1)
			return True
		else:
			raise e
	return False

##########################################
#                   Main                 #
##########################################
def getSkinMap():
	skinMap = SkinMap()

def main():
	getSkinMap()

if __name__ == "__main__":
	main()