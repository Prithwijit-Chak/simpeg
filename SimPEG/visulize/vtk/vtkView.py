import numpy as np, vtk
import SimPEG as simpeg
#import SimPEG.visulize.vtk.vtkTools as vtkSP # Always get an error for this import

class vtkView(object):
	"""
	Class for storing and view of SimPEG models in VTK (visulization toolkit).

	Inputs:
	:param mesh, SimPEG mesh.
	:param propdict, dictionary of property models. 
		Can have these dictionary names:
		'cell' - cell model; 'face' - face model; 'edge' - edge model
		The dictionary properties are given as dictionaries with:
		{'NameOfThePropertyModel': np.array of the properties}. 
		The property array has to be ordered in compliance with SimPEG standards.

	::
	Example of usages.

		ToDo

	"""

	def __init__(self,mesh,propdict):
		"""
		"""

		# ToDo: Set the properties up so that there are set/get methods
		self.name = 'VTK figure of SimPEG model'
		self.extent = [0,mesh.nCx-1,0,mesh.nCy-1,0,mesh.nCz-1]
		self.limits = [0, 1e12]
		self.viewprop = {'cell':0} # Name of the tyep and Int order of the array or name of the vector.
		self._mesh = mesh


		# Set vtk object containers
		self._cell = None
		self._faces = None
		self._edges = None

		self._readPropertyDictionary(propdict)

		# Setup hidden properties
		self._ren = None
		self._iren = None
		self._renwin = None
		self._core = None
		self._viewobj = None
		self._plane = None
		self._clipper = None
		self._widget = None
		self._actor = None
		self._lut = None

	def _readPropertyDictionary(self,propdict):
		""" 
		Reads the property and assigns to the object
		"""
		import SimPEG.visulize.vtk.vtkTools as vtkSP

		# Test the property dictionary
		if len(propdict) > 3:
			raise(Exception,'Too many input items in the property dictionary')
		for propitem in propdict.iteritems():
			if propitem[0] in ['cell','face','edge']:
				if propitem[0] == 'cell':
					self._cell = vtkSP.makeCellVTKObject(self._mesh,propitem[1])
				if propitem[0] == 'face':
					self._face = vtkSP.makeFaceVTKObject(self._mesh,propitem[1])
				if propitem[0] == 'edge':
					self._edge = vtkSP.makeEdgeVTKObject(self._mesh,propitem[1])
			else:
				raise(Exception,'{:s} is not allowed as a dictonary key. Can be \'cell\',\'face\',\'edge\'.'.format(propitem[0]))

	def Show(self):
		"""
		Open the VTK figure window and show the mesh.		
		"""
		#vtkSP = simpeg.visulize.vtk.vtkTools
		import SimPEG.visulize.vtk.vtkTools as vtkSP

		# Make a renderer
		self._ren = vtk.vtkRenderer()
		# Make renderwindow. Returns the interactor.
		self._iren, self._renwin = vtkSP.makeRenderWindow(self._ren)

		imageType = self.viewprop.keys()[0]
		# Sort out the actor
		if imageType == 'cell':
			self._vtkobj, self._core = vtkSP.makeRectiVTKVOIThres(self._cell,self.extent,self.limits)
		elif imageType == 'face':
			extent = [self._mesh.vectorNx[self.extent[0]], self._mesh.vectorNx[self.extent[1]], self._mesh.vectorNy[self.extent[2]], self._mesh.vectorNy[self.extent[3]], self._mesh.vectorNz[self.extent[4]], self._mesh.vectorNz[self.extent[5]] ]
			self._vtkobj, self._core = vtkSP.makeUnstructVTKVOIThres(self._face,extent,self.limits)
		elif imageType == 'edge':
			extent = [self._mesh.vectorNx[self.extent[0]], self._mesh.vectorNx[self.extent[1]], self._mesh.vectorNy[self.extent[2]], self._mesh.vectorNy[self.extent[3]], self._mesh.vectorNz[self.extent[4]], self._mesh.vectorNz[self.extent[5]] ]
			self._vtkobj, self._core = vtkSP.makeUnstructVTKVOIThres(self._edge,extent,self.limits)
		else:
			raise Exception("{:s} is not a vailid imageType. Has to be 'cell':'face':'edge'".format(imageType))

		# Set the active scalar.
		if type(self.viewprop.values()[0]) == int:
			actScalar = self._vtkobj.GetCellData().GetArrayName(self.viewprop.values()[0])
		elif type(self.viewprop.values()[0]) == str:
			actScalar = self.viewprop.values()[0]
		else :
			raise Exception('The vtkView.viewprop.values()[0] has the wrong format. Has to be interger or a string.')
		self._vtkobj.GetCellData().SetActiveScalars(actScalar)
		# Set up the plane, clipper and the user interaction.
		global intPlane, intActor
		self._clipper, intPlane = vtkSP.makePlaneClipper(self._vtkobj)
		intActor = vtkSP.makeVTKLODActor(self._vtkobj,self._clipper)
		self._widget = vtkSP.makePlaneWidget(self._vtkobj,self._iren,self._clipper.GetClipFunction(),self._actor)
		# Callback function
		self._plane = intPlane
		self._actor = intActor
		def movePlane(obj, events):
			global intPlane, intActor
			obj.GetPlane(intPlane)
			intActor.VisibilityOn()

		self._widget.AddObserver("InteractionEvent",movePlane)		    
		lut = vtk.vtkLookupTable()
		lut.SetNumberOfColors(256)
		lut.SetHueRange(0,0.66667)
		lut.Build()
		self._lut = lut
		self._actor.GetMapper().SetLookupTable(lut)

		# Set renderer options
		self._ren.SetBackground(.5,.5,.5)
		self._ren.AddActor(self._actor)

		# Start the render Window		
		vtkSP.startRenderWindow(self._iren)
		# Close the window when exited
		vtkSP.closeRenderWindow(self._iren)
		del self._iren, self._renwin








