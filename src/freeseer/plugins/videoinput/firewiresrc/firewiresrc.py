'''
freeseer - vga/presentation capture software

Copyright (C) 2011  Free and Open Source Software Learning Centre
http://fosslc.org

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

For support, questions, suggestions or any other inquiries, visit:
http://wiki.github.com/fosslc/freeseer/

@author: Thanh Ha
'''

import ConfigParser
import os

import pygst
pygst.require("0.10")
import gst

from PyQt4 import QtGui, QtCore

from freeseer.framework.plugin import IVideoInput

class FirewireSrc(IVideoInput):
    name = "Firewire Source"
    device = "/dev/fw1"
    device_list = []
    
    def __init__(self):
        IVideoInput.__init__(self)
        
        #
        # Detect available devices
        #
        i = 1
        path = "/dev/fw"
        devpath = path + str(i)
        
        while os.path.exists(devpath):
            self.device_list.append(devpath)
            i=i+1
            devpath=path + str(i)
    
    def get_videoinput_bin(self):
        bin = gst.Bin(self.name)

        videosrc = gst.element_factory_make("dv1394src", "videosrc")
        dv1394q1 =  gst.element_factory_make('queue', 'dv1394q1')
        dv1394dvdemux =  gst.element_factory_make('dvdemux', 'dv1394dvdemux')
        dv1394q2 =  gst.element_factory_make('queue', 'dv1394q2')
        dv1394dvdec =  gst.element_factory_make('dvdec', 'dv1394dvdec')
        
        bin.add(videosrc, dv1394q1, dv1394dvdemux, dv1394q2, dv1394dvdec)
        
        # Setup ghost pad
        pad = dv1394dvdec.get_pad("src")
        ghostpad = gst.GhostPad("videosrc", pad)
        bin.add_pad(ghostpad)
        
        return bin
    
    def load_config(self, plugman):
        self.plugman = plugman
        self.device = self.plugman.plugmanc.readOptionFromPlugin("VideoInput", self.name, "Video Device")
        self.input_type = self.plugman.plugmanc.readOptionFromPlugin("VideoInput", self.name, "Input Type")
        self.framerate = self.plugman.plugmanc.readOptionFromPlugin("VideoInput", self.name, "Framerate")
        self.resolution = self.plugman.plugmanc.readOptionFromPlugin("VideoInput", self.name, "Resolution")
        
    def get_widget(self):
        if self.widget is None:
            self.widget = QtGui.QWidget()
            
            layout = QtGui.QFormLayout()
            self.widget.setLayout(layout)
            
            self.label = QtGui.QLabel("Video Device")
            self.combobox = QtGui.QComboBox()
            layout.addRow(self.label, self.combobox)
            
            # Connections
            self.widget.connect(self.combobox, 
                                QtCore.SIGNAL('currentIndexChanged(const QString&)'), 
                                self.set_device)
                        
        return self.widget

    def widget_load_config(self, plugman):
        self.plugman = plugman
        
        try:
            self.device = self.plugman.plugmanc.readOptionFromPlugin("VideoInput", self.name, "Video Device")
        except ConfigParser.NoSectionError:
            self.plugman.plugmanc.registerOptionFromPlugin("VideoInput", self.name, "Video Device", self.device)
                
        # Load the combobox with inputs
        self.combobox.clear()
        n = 0
        for i in self.device_list:
            self.combobox.addItem(i)
            if i == self.device:
                self.combobox.setCurrentIndex(n)
            n = n +1
            
    def set_device(self, device):
        self.plugman.plugmanc.registerOptionFromPlugin("VideoInput", self.name, "Video Device", device)
        self.plugman.save()