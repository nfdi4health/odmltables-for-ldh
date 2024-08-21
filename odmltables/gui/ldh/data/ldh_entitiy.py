from enum import Enum

import PyQt5.QtWidgets as Qtw
import PyQt5.QtGui as QtGui
import webbrowser

class InstanceType(Enum):
    PROJECT = 1
    INVESTIGATION = 2
    STUDY = 3
    COLLECTION = 4
    DATAFILE = 5

def instanceTypeToString(instance_type: InstanceType):
        if instance_type == InstanceType.PROJECT:
            return "Project"
        if instance_type == InstanceType.COLLECTION:
            return "Collection"
        if instance_type == InstanceType.DATAFILE:
            return "Data File"
        if instance_type == InstanceType.INVESTIGATION:
            return "Investigation"
        if instance_type == InstanceType.STUDY:
            return "Study"
        
        print("unknown InstanceType")
        return ""


# TODO possibly have different AttributeKinds - so we can make singleline or multi-line edits 

class Attribute():
    def __init__(self, key: str, string: str, value, position: int, is_madatory: bool):
        self.key = key
        self.string = string
        self.value = value
        self.position = position
        self.is_mandatory = is_madatory

    def get_string_representation(self):
        if self.is_mandatory:
            return self.string + "*" + ": "
        else:
            return self.string + ": "
            

class Relationship():


    def __init__(self) -> None:
        pass


class EditableTextBrowser(Qtw.QTextBrowser):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(False)

    def mousePressEvent(self, event):
        anchor = self.anchorAt(event.pos())
        if anchor:
            webbrowser.open(anchor)
        else:
            super().mousePressEvent(event)

    def keyPressEvent(self, event):
        super().keyPressEvent(event)


class LDHEntitiy():

    

    def __init__(self, type: InstanceType, title: str):
        self.type = type
        self.change_title(title)

        type = None
        self.attributes = {"title":  Attribute( "title", "Title", None,  0, True)}
        self.relationships = {}
  

    def validate_object(self) -> bool:
        # TODO check whether all mandatory attributes have a value that is not None
        return True
    

    def add_relationship(self, key, reference) -> bool:
        if key in self.relationships:
            self.relationships[key].append(reference)
            return True
        else:
            return False

    

    def change_attribute_value(self, key: str, value) -> bool:

        if type(value) == str:
            if value == "None":
                return False
            if key == "tags":
                value = value.split("[")[1]
                value = value.split("]")[0]
                value = value.split(",")

            
        if key in self.attributes:
            self.attributes[key].value= value
            return True
        else:
            return False
        
    def get_attribute_value(self, key: str):
        if key in self.attributes:
            return self.attributes[key].value
        else: 
            return None
        
    def get_attribute_string_value(self, key: str):
        if key in self.attributes:
            value = self.attributes[key].value
            if type(value) == list:
                return ", ".join(value)
            else:
                return value
        else: 
            return None
        
    def get_attribute_is_manadatory(self, key: str):
        if key in self.attributes:
            return self.attributes[key].is_mandatory
        else: 
            return None
    

    def change_title(self, title: str):
        self.change_attribute_value("title", title)

    # returns the number of attributes of the entity
    def get_number_of_attributes(self) -> int:
        return len(self.attributes)

    # returns a list of all attributes ordered by their position
    def get_ordered_attributes(self) :
        ordered_attributes = []

        for i in range(0, self.get_number_of_attributes() + 1):
            for key, attribute in self.attributes.items():
                if attribute.position == i:
                    ordered_attributes.append(attribute)
        
        return ordered_attributes
    

    def create_layout(self, project_title="", institution_name=""):

        vbox = Qtw.QVBoxLayout()

        title_font = QtGui.QFont()
        title_font.setBold(True)
        title_font.setPointSize(14)
        label = Qtw.QLabel("")
        if self.type == InstanceType.COLLECTION:
            label = Qtw.QLabel("Create New Collection")
        else:
            if self.type == InstanceType.PROJECT:
                label = Qtw.QLabel("Create New Project")

        vbox.addWidget(label)

        grid = Qtw.QGridLayout()
        vbox.addLayout(grid)

        attribute_dict = {}
        attributes = self.get_ordered_attributes()

        i = 0
        for attribute in attributes:
            temp_label = Qtw.QLabel(attribute.get_string_representation())
            temp_edit = Qtw.QLineEdit()

            # TODO enable multi-line edits and more edits # maybe a get textEdit for attribute - more elegant
            if attribute.key == "description":
                temp_edit = EditableTextBrowser()
                temp_edit.resize(400, 200)
                # temp_edit.setOpenExternalLinks(True)
            else:
                temp_edit = Qtw.QLineEdit()
            attribute_dict[attribute.key] = temp_edit
            grid.addWidget(temp_label, i, 0)
            grid.addWidget(temp_edit, i, 1)
            i = i + 1

            if self.type == InstanceType.PROJECT and attribute.key == "institution_name":
                temp_edit.setText(institution_name)
                temp_edit.setReadOnly(True)

            if attribute.key == "projects":
                temp_edit.setText(project_title)
                temp_edit.setReadOnly(True)

        return vbox, attribute_dict
            




