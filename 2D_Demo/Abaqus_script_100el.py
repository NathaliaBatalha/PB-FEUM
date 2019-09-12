# -*- coding: mbcs -*-
from part import *
from material import *
from section import *
from assembly import *
from step import *
from interaction import *
from load import *
from mesh import *
from optimization import *
from job import *
from sketch import *
from visualization import *
from connectorBehavior import *
import os

Mdb()

# Defines curent path
directory = os.getcwd()

# CHANGE HERE********
abaqus_directory = 'Insert your path here' 
#This is the path where this script is saved and 'input' files are

#-------------------------------------------------------------------------------------
# Read data from file
f = open(abaqus_directory + '\\Input_1.txt','r') #Insert the Input file name here
# Read all file lines as a vector
dados = f.readlines()
# Close file
f.close()

# Defines vectors for material parameters
young     = list()
poisson   = list()

# Goes through all input file lines
for linha in dados:
    try:
		# Replaces all "tabs" and "enters" of the srting
        linha = linha.replace("\t","")
        linha = linha.replace("\n","")
		# Creates a vetctor from string "lines", by the space ""
        vector = linha.split()
		# Removes all empty fields
        vector = filter(lambda a: a != '', vector)

		# Adds values in the vectors 
        young.append(float(vector[0]))
        poisson.append(float(vector[1]))
    except:
        pass

#---------- Define Solid and number of elements
# Size of the square (m)
l = 1.0
thick = 0.02
# Element's number in one edge
n = int(sqrt((len(young))))
print("Len_young=%.4f    n=%.4f" % (len(young),n))

# Model
mdb.models['Model-1'].ConstrainedSketch(name='__profile__', sheetSize=10.0)
mdb.models['Model-1'].sketches['__profile__'].rectangle(point1=(0.0, 0.0), 
    point2=(l, l))
mdb.models['Model-1'].Part(dimensionality=TWO_D_PLANAR, name='Plate1', type=
    DEFORMABLE_BODY)
mdb.models['Model-1'].parts['Plate1'].BaseShell(sketch=
    mdb.models['Model-1'].sketches['__profile__'])
del mdb.models['Model-1'].sketches['__profile__']
mdb.models['Model-1'].parts['Plate1'].seedEdgeByNumber(constraint=FINER, edges=
    mdb.models['Model-1'].parts['Plate1'].edges.getSequenceFromMask(('[#2 ]', 
    ), ), number=n)
mdb.models['Model-1'].parts['Plate1'].seedEdgeByNumber(constraint=FINER, edges=
    mdb.models['Model-1'].parts['Plate1'].edges.getSequenceFromMask(('[#1 ]', 
    ), ), number=n)
mdb.models['Model-1'].parts['Plate1'].generateMesh()
mdb.models['Model-1'].parts['Plate1'].setElementType(elemTypes=(ElemType(
    elemCode=CPS8, elemLibrary=STANDARD), ElemType(elemCode=CPS6M, 
    elemLibrary=STANDARD)), regions=(
    mdb.models['Model-1'].parts['Plate1'].faces.getSequenceFromMask(('[#1 ]', 
    ), ), ))

	
# Apply section
i = 0
j = 0

dx = l/n
nameId = 0
tol = l/n*.05

for j in range(int(n)):
    for i in range(int(n)):
        xMin = i*dx-tol
        xMax = (i+1)*dx+tol
        yMin = dx*j-tol
        yMax = (j+1)*dx+tol
        print("xMin=%.4f    xMax=%.4f   yMin=%.4f   yMax=%.4f" % (xMin, xMax, yMin, yMax))
        elements = mdb.models['Model-1'].parts['Plate1'].elements.getByBoundingBox(xMin=xMin,xMax=xMax,
        yMin=yMin,yMax=yMax)
        name = 'Element_'+ str(nameId+1)
        # Create elements sets
        mdb.models['Model-1'].parts['Plate1'].Set(elements=elements,name=name)        
        # Create Material
        mdb.models['Model-1'].Material(name=('Elem_Material_'+str(nameId+1)))
        mdb.models['Model-1'].materials[('Elem_Material_'+str(nameId+1))].Elastic(table=((young[nameId], poisson[nameId]), ))
        # Create section        
        mdb.models['Model-1'].HomogeneousSolidSection(material=('Elem_Material_'+str(nameId+1)), name=('Section_Elem_'+str(nameId+1)), thickness=thick)            
		# Apply created section to the created set
        mdb.models['Model-1'].parts['Plate1'].SectionAssignment(offset=0.0, offsetField='', offsetType=MIDDLE_SURFACE, region=
			mdb.models['Model-1'].parts['Plate1'].sets[name], sectionName=('Section_Elem_'+str(nameId+1)), 
			thicknessAssignment=FROM_SECTION)
        # Update id
        nameId = nameId+1
		
# Assemble
mdb.models['Model-1'].rootAssembly.DatumCsysByDefault(CARTESIAN)
mdb.models['Model-1'].rootAssembly.Instance(dependent=ON, name='Plate1-1', 
    part=mdb.models['Model-1'].parts['Plate1'])
	
# Create Step	
mdb.models['Model-1'].StaticStep(name='Step-1', previous='Initial')

# Top surface for Pressure Load
mdb.models['Model-1'].rootAssembly.Surface(name='Top_Surf', side1Edges=
    mdb.models['Model-1'].rootAssembly.instances['Plate1-1'].edges.getSequenceFromMask(
    ('[#4 ]', ), ))
	
# Pressure Load
mdb.models['Model-1'].Pressure(amplitude=UNSET, createStepName='Step-1', 
    distributionType=UNIFORM, field='', magnitude=19500000.0, name=
    'Pressure_Load_Top', region=
    mdb.models['Model-1'].rootAssembly.surfaces['Top_Surf'])
	
# Base surface BC
mdb.models['Model-1'].rootAssembly.Set(edges=
    mdb.models['Model-1'].rootAssembly.instances['Plate1-1'].edges.getSequenceFromMask(
    ('[#1 ]', ), ), name='Base_Surf')
	
# Boundary Condition - Uy=0 Base	
mdb.models['Model-1'].DisplacementBC(amplitude=UNSET, createStepName='Step-1', 
    distributionType=UNIFORM, fieldName='', fixed=OFF, localCsys=None, name=
    'BC_y', region=mdb.models['Model-1'].rootAssembly.sets['Base_Surf'], u1=
    UNSET, u2=0.0, ur3=UNSET)
	
# Node base for Uxz	BC
mdb.models['Model-1'].parts['Plate1'].Set(name='BC_xz', nodes=
    mdb.models['Model-1'].parts['Plate1'].nodes.getSequenceFromMask(mask=(
    '[#20 ]', ), ))

# Boundary Condition - Uy=0 Base
mdb.models['Model-1'].rootAssembly.regenerate()
mdb.models['Model-1'].DisplacementBC(amplitude=UNSET, createStepName='Step-1', 
    distributionType=UNIFORM, fieldName='', fixed=OFF, localCsys=None, name=
    'BC_xz', region=
    mdb.models['Model-1'].rootAssembly.instances['Plate1-1'].sets['BC_xz'], u1=
    0.0, u2=UNSET, ur3=0.0)
	
# Create a Job	
mdb.Job(atTime=None, contactPrint=OFF, description='', echoPrint=OFF, 
    explicitPrecision=SINGLE, getMemoryFromAnalysis=True, historyPrint=OFF, 
    memory=90, memoryUnits=PERCENTAGE, model='Model-1', modelPrint=OFF, name=
    'Job-1', nodalOutputPrecision=SINGLE, queue=None, resultsFormat=ODB, 
    scratch='', type=ANALYSIS, userSubroutine='', waitHours=0, waitMinutes=0)
	 
# Submit the Job	
mdb.jobs['Job-1'].submit(consistencyChecking=OFF)

