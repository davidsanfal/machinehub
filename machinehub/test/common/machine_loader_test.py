import unittest
import tempfile
import os
from machinehub.common.machine_loader import load_machine, load_machine_from_source
from machinehub.common.errors import NotMachineHub


machine_test = '''
import sys
FREECADPATH = '/usr/lib/freecad/lib/'
sys.path.append(FREECADPATH)
import FreeCAD
import Draft
import Mesh

def machinebuilder(text, size, height, file_path):
    \'\'\'
[doc]
-title-
Super Text Generator
-images_url-
http://blog.desdelinux.net/wp-content/uploads/2013/02/TrollFace.png
-description-
Create text in 3D
[inputs]
str(text)
int(size)
int(height)
    \'\'\'

    #-- Generate text
    doc = FreeCAD.newDocument("TextGenerator")
    text = "404 ERROR"

    ss=Draft.makeShapeString(String=text,FontFile="/usr/share/fonts/truetype/droid/DroidSans.ttf",Size=size,Tracking=0)

    obj = doc.addObject("Part::Extrusion","TextGenerator")
    obj.Base = ss
    obj.Dir = (0,0,height)

    doc.recompute()
'''

no_machine_test = '''
import sys
FREECADPATH = '/usr/lib/freecad/lib/'
sys.path.append(FREECADPATH)
import FreeCAD
import Draft
import Mesh

def machine_builder(text, size, height, file_path):
    pass
'''


class LoaderTest(unittest.TestCase):

    def simple_loader_test(self):
        tmp_folder = tempfile.mkdtemp(prefix='machinehub')
        machine_path = os.path.join(tmp_folder, 'supermachine.py')
        with open(machine_path, "w+") as f:
            f.write(machine_test)
        fn, doc, inputs = load_machine(machine_path)
        self.assertEqual(fn.__name__, 'machinebuilder')
        self.assertEqual(doc.title, 'Super Text Generator')
        self.assertEqual(doc.description, 'Create text in 3D')
        self.assertEqual(doc.images,
                         ['http://blog.desdelinux.net/wp-content/uploads/2013/02/TrollFace.png'])
        self.assertEqual(inputs,
                         [['text', 'str', None, [], []],
                          ['size', 'int', None, [], []],
                          ['height', 'int', None, [], []]])

    def simple_loader_from_source_test(self):
        fn, doc, inputs = load_machine_from_source(machine_test)
        self.assertEqual(fn.__name__, 'machinebuilder')
        self.assertEqual(doc.title, 'Super Text Generator')
        self.assertEqual(doc.description, 'Create text in 3D')
        self.assertEqual(doc.images,
                         ['http://blog.desdelinux.net/wp-content/uploads/2013/02/TrollFace.png'])
        self.assertEqual(inputs,
                         [['text', 'str', None, [], []],
                          ['size', 'int', None, [], []],
                          ['height', 'int', None, [], []]])

    def simple_loader_exception_test(self):
        tmp_folder = tempfile.mkdtemp(prefix='machinehub')
        machine_path = os.path.join(tmp_folder, 'supermachine.py')
        with open(machine_path, "w+") as f:
            f.write(no_machine_test)
        self.assertRaises(NotMachineHub, load_machine, machine_path)
        self.assertRaises(NotMachineHub, load_machine_from_source, no_machine_test)
