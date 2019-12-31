#!/usr/bin/env python3
import kivy
kivy.require('1.0.6') 
from kivy.uix.widget import Widget
from kivy.app import App
from kivy.properties import ObjectProperty, ListProperty, StringProperty, BooleanProperty, NumericProperty
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.button import Button
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.popup import Popup
from kivy.uix.image import Image
from IPTrackerData import IPTrackerData
from threading import Thread 
import configparser


class RecycleView():
	def refresh_from_data(self, force=True):
		"""The data has changed, update the RecycleView internals
		"""
		print("refresh data")
		if force:
			self.dirty_views.update(self.views)
		self.compute_views_heights()
		self.compute_visible_views()
		
''' for table like recycleview for ips'''
class RecycleViewRow(RecycleDataViewBehavior, BoxLayout):
	text = StringProperty()  
	ip = StringProperty()  
	status = StringProperty()
	hostname = StringProperty()
	note = StringProperty()
	''' Add selection support to the Label '''
	index = None
	selected = BooleanProperty(False)
	selectable = BooleanProperty(True)
	_id = 0

	def refresh_view_attrs(self, rv, index, data):
		''' Catch and handle the view changes '''
		self.index = index
		return super(RecycleViewRow, self).refresh_view_attrs(rv, index, data)

	def on_touch_down(self, touch):
		''' Add selection on touch down '''
		if super(RecycleViewRow, self).on_touch_down(touch):
			return True
		if self.collide_point(*touch.pos) and self.selectable:
			return self.parent.select_with_touch(self.index, touch)
			
	def apply_selection(self, rv, index, is_selected):
		self.selected = is_selected
		self._id = index
		#share index
		global _selindex
		_selindex = index
		_ip = str(rv.data[index]['ip'])
		
		#if is_selected:
			#print("selected: "+ str(index)+" - "+ str(_ip))
		
	def note_update(self, txt):
		print("focus: "+str(self._id))
		
	#update IP note	
	def note_write(self, val):
		_ip = str(self.ip)
		global _subnetid
		global _selindex
		
		if _subnetid != 0:
			Data = IPTrackerData()
			_ipdata = (val,_ip,_subnetid)
			Data.update_ip_note(_ipdata)
			print(" updated: "+str(_ip)+" index"+str(self._id)+" text:"+val)
		
		
	def refresh_from_data(self, force=True):
		"""The data has changed, update the RecycleView internals
		"""
		print("refresh data")
		if force:
			self.dirty_views.update(self.views)
		self.compute_views_heights()
		self.compute_visible_views()
	
class SelectableRecycleBoxLayout(FocusBehavior, LayoutSelectionBehavior, RecycleBoxLayout):
#Adds selection and focus behaviour to the view. '''
	def select_current(self):
		''' Select current row '''
		last, nodes = self.get_nodes()
		if not nodes:
			return

		self.select_node(nodes[self.selected_row])
	
class SelectableLabel(RecycleDataViewBehavior, Label):
	''' Add selection support to the Label '''
	index = None
	selected = BooleanProperty(False)
	selectable = BooleanProperty(True)

	def refresh_view_attrs(self, rv, index, data):
		''' Catch and handle the view changes '''
		self.index = index
		return super(SelectableLabel, self).refresh_view_attrs(rv, index, data)

	def on_touch_down(self, touch):
		''' Add selection on touch down '''
		if super(SelectableLabel, self).on_touch_down(touch):
			return True
		if self.collide_point(*touch.pos) and self.selectable:
			return self.parent.select_with_touch(self.index, touch)

	def apply_selection(self, rv, index, is_selected):
		''' Respond to the selection of items in the view. '''
		self.selected = is_selected
		
		#share index
		global _selindex
		_selindex = index
		
		global _navindex
		_navindex = index
		
		if is_selected:
			
			print("selection changed to {0}".format(rv.data[index]))
			_subname = str(rv.data[index]['text'])
			
			Data = IPTrackerData()
			global _subnetid
			
			_subnetid = Data.get_subnet_id(_subname)
			tblData = Data.get_ips(_subnetid)
			_data = []
			
			for _item in tblData:
				_ip = _item[0]
				_status = str(_item[1])
				_hostname = str(_item[2])
				_notes = _item[3]
				if _notes is None:
					_notes = ""
					
				_data.append({'ip':_ip, 'status':_status,'hostname':_hostname,'note':_notes})
			
			global rv2
			rv2.data = _data
			
			
		else:
			pass
			#print("selection for {0}".format(rv.data[index]))
			
		
		
class TrackerLayout(BoxLayout):
	text = StringProperty()
	#subnetid
	global _subnetid
	_subnetid = NumericProperty(20)
	_subnetid = 0

		
	def __init__(self, **kwargs):
		super(TrackerLayout, self).__init__(**kwargs)
		
		
	def update(self):
		pass
	
	def popNav(self):
	
		_tblsep = self.ids.screen_manager.get_screen("start_screen").ids.tblseparator
		_tblsep.pos = self.ids.screen_manager.get_screen("start_screen").ids.rv.width,0
		
		Data = IPTrackerData()
		global rv
		rv = self.ids.screen_manager.get_screen("start_screen").ids.rv
		nav_items = Data.subnets
		rv.data = [{'text': str(x)} for x in nav_items]
		
		global rv2
		rv2 = self.ids.screen_manager.get_screen("start_screen").ids.rv2
		
		
	def menuSel(self):
		#print("selected")
		pass
		
	def settingsdlg(self):

		#this should be updated to use Kivy settings panel in the future
		app_ref = App.get_running_app()
		_ids = app_ref.root.ids
		self.ids.screen_manager.current = "settingspop"
		
		
		db_file = StringProperty()
		#add check that file exists in main
		config = configparser.ConfigParser()
		config.read('tracker.cfg')
		
	def settingsdlg_close(self):
		self.ids.screen_manager.current = "start_screen"
		
		
	def addSubnet(self):
		app_ref = App.get_running_app()
		_ids = app_ref.root.ids
		self.ids.screen_manager.current = "addsubnetpop"

		
	def addsubnetpop_close(self):
		self.ids.screen_manager.current = "start_screen"
		
	def CreateSubnet(self):
		new_network = self.ids.screen_manager.get_screen("addsubnetpop").ids.new_network.text
		new_mask = self.ids.screen_manager.get_screen("addsubnetpop").ids.new_mask.text
		new_name = self.ids.screen_manager.get_screen("addsubnetpop").ids.new_name.text
		btn = self.ids.screen_manager.get_screen("addsubnetpop").ids.addbtn
		_image = Image(source="loading.gif")
		btn.add_widget(_image)
		
		Data = IPTrackerData()
		data = (new_name,new_network,new_mask)
		id = Data.create_subnet(data)
		
		ipdata = (id,new_network,new_mask)
		t = Thread(target=self.createIps, args=( ipdata, ))
		t.setDaemon(True) #set to exit with main thread
		t.start()
		self.ids.screen_manager.current = "start_screen"
		
		
		#refresh nav list
		Data2 = IPTrackerData()
		global rv
		rv.layout_manager.clear_selection()
		nav_items = Data2.subnets
		rv.data = [{'text': str(x)} for x in nav_items]
		rv.refresh_from_data()
		
	def createIps(self, ipdata):
		Data = IPTrackerData()
		Data.create_ips(ipdata)
		
	def removeSubnet(self):
		app_ref = App.get_running_app()
		_ids = app_ref.root.ids
		self.ids.screen_manager.current = "removesubnetpop"
		
		global _navindex
		_subname = self.ids.screen_manager.get_screen("start_screen").ids.rv.data[_navindex]['text']
		self.ids.screen_manager.get_screen("removesubnetpop").ids.rmessage.text = "Are you sure you want to remove " +_subname +"? "
		
		
	def removesubnetconf_dismiss(self):
		app_ref = App.get_running_app()
		_ids = app_ref.root.ids
		self.ids.screen_manager.current = "start_screen"
		
	def removesubnetdata(self):
		if '_subnetid' in globals():
			global _subnetid
			
			#remove subnet form database
			Data = IPTrackerData()
			Data.remove_subnet(_subnetid)
			
			#refresh nav list
			Data2 = IPTrackerData()
			global rv
			rv.layout_manager.clear_selection()
			nav_items = Data2.subnets
			rv.data = [{'text': str(x)} for x in nav_items]
			rv.refresh_from_data()
			
			self.ids.screen_manager.current = "start_screen"
			
		else:
			print('no item selected')
			
	
	def fping(self, address):
		import os
		import sys
		import subprocess
		import time
		
		startupinfo = None
		if os.name == "nt":
			startupinfo=subprocess.STARTUPINFO()
			startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
			cmd = "ping -n 1 -w 3 "+address
		else:
			cmd = ["/usr/bin/ping","-c","1","-W","3",address]
        
		p = subprocess.Popen(cmd,
							 stdout=subprocess.PIPE,
							 stderr=subprocess.STDOUT,
                             startupinfo=startupinfo)

		# Wait until process terminates (without using p.wait())
		while p.poll() is None:
			# Process hasn't exited yet, let's wait some
			time.sleep(0.5)

		#windows	
		_sub = "Received = 1"
		#linux
		#_sub = "1 received,"
		
		# Get return code from process
		ret = p.stdout.read()
		
		if _sub in str(ret):
			return True
		else:
			return False
			
	def repoprv(self):
		
		_subname = str(rv.data[_navindex]['text'])
			
		Data = IPTrackerData()
		
		_subnetid = Data.get_subnet_id(_subname)
		tblData = Data.get_ips(_subnetid)
		_data = []
		
		for _item in tblData:
			_ip = _item[0]
			_status = str(_item[1])
			_hostname = str(_item[2])
			_notes = _item[3]
			if _notes is None:
				_notes = ""
				
			_data.append({'ip':_ip, 'status':_status,'hostname':_hostname,'note':_notes})
		rv2.data = _data
		rv2.refresh_from_data()
			
	def ipscan(self, _subnetid):
		import socket 
		self.repoprv()
		
		Data = IPTrackerData()
		_ips = Data.get_ips(_subnetid)
		_cnt = 0
		for _ip in _ips:
			print(str(_ip))
			self.ids.scanstatus.text = "Scanning " + str(_ip[0])
			
			#ping ip for status
			if self.fping(_ip[0]) == True:
				_statdata = ("Alive",_ip[0],_subnetid)
				Data.update_ip_status(_statdata)
			else:
				_statdata = ("",_ip[0],_subnetid)
				Data.update_ip_status(_statdata)
			
			#check for dns name
			try:
				_dns = socket.gethostbyaddr(_ip[0])
				_hostname = _dns[0]
			except: 
				_hostname = ""
				
			_data = (_hostname,_ip[0],_subnetid)
			print(_data)
			Data.update_ip_hostname(_data)
		
	def scanCall(self):
		global _subnetid
		
		if _subnetid != 0:
			t = Thread(target=self.ipscan, args=( _subnetid, ))
			t.setDaemon(True) #set to exit with main thread
			t.start()
	
class IPTracker2(App):

	def build(self):
		tracker = TrackerLayout()
		tracker.popNav()
		
		return tracker


if __name__ == '__main__':
	IPTracker2().run()
	
	