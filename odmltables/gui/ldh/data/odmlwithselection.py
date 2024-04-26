import pandas as pd

# Workaround Python 2 and 3 unicode handling.
try:
    unicode = unicode
except NameError:
    unicode = str

from PyQt5.QtCore import Qt
import PyQt5.QtWidgets as Qtw
from PyQt5.QtGui import QBrush, QColor

from odmltables import OdmlTable
import odml







experiment_general_columns = ['ExperimentID', "Experimenter", "Laboratory", "LegalDocumentation", "Objective", "PetName", "PublishingInfo", "SharingTerms", "Title"] # 9
experiment_recordingequip_columns = ["Ampfliciation", "DataAcquisition", "ElectrodeDescription", "ElectrodePlacement", "ElectrodeType", "FrequencyFilters", "RecordingDevice"] #7
experiment_subject_columns = ['SubjectID', 'Species', 'Sex', 'Age', 'HealthStatus', 'BodyTemperatureStart', 'BodyTemperatureMid', 'BodyTemperatureEnd', 'MedicationChemicals', 'Weight', 'Height', 'SubjectDescription'] #12
experiment_section_property_map = { "General": experiment_general_columns, "RecordingEquip": experiment_recordingequip_columns, "Subject": experiment_subject_columns}

recording_general_columns = ['RecordingFile', 'SamplingRate', 'Software', 'SoftwareVersion', 'Quality', 'Channels', 'Summary']
recording_marking_method_columns = ['MarkingUsed', 'BaseFrequency']
recording_chemicals_columns = ['ChemicalsUsed', 'ChemicalName']
recording_fibers_columns = ['FibreCount', 'FiberDescription', 'SpontaneousActivity', 'SpontaneousHappen']
recording_electrical_stimulus_columns = ['Protocol', 'Description', 'DeviceName', 'StimulationDist']
recording_mechanical_stimulus_columns = ['MechStimUsed', 'StimulusType', 'Description']
recording_heat_stimulus_columns = ['HeatStimUsed', 'Protocol']
        
recording_section_property_map = { "General": recording_general_columns, "MarkingMethod": recording_marking_method_columns, "Chemicals": recording_chemicals_columns, 
                                          "Fibers": recording_fibers_columns, "ElectricalStimulus": recording_electrical_stimulus_columns, 
                                          "MechanicalStimulus": recording_mechanical_stimulus_columns, "HeatStimulus": recording_heat_stimulus_columns}



class OdmlTableWithSelection(OdmlTable):

    def __init__(self, load_from=None):
        super().__init__(load_from)

    
    # needed to hook __create_odmldict
    def load_from_file(self, load_from):
        """
        loads the odml-data from an odml-file
        :param load_from: the path to the odml-file
        :type load_from: string
        """
        self.input_file = load_from
        self.doc = odml.load(load_from, show_warnings=self.show_odml_warnings)
        odml.display(self.doc)
        # resolve links and includes
        self.doc.finalize()
        self._odmldict = self.__create_odmldict(self.doc)
        self._docdict = self._create_documentdict(self.doc)


    # add selected property to dict
        # this is never calleddddddddddddddddddddddddddd????????
    def __create_odmldict(self, doc):
        """
        function to create the odml-dict
        """
        # In odml 1.4 properties are the leaves of the odml tree; unwrap from there.
        props = list(doc.iterproperties())

        odmldict = [{'Path': p.get_path(),
                     'SectionType': p.parent.type,
                     'SectionDefinition': p.parent.definition,
                     'PropertyDefinition': p.definition,
                     'Value': p.values,
                     'DataUnit': p.unit,
                     'DataUncertainty': p.uncertainty,
                     'odmlDatatype': p.dtype,
                     'Selected': True
                     }
                    for p in props]

        odmldict = self._sort_odmldict(odmldict)
        return odmldict
    
    def get_selection(self, path: str):
        for item in self._odmldict:
            if item['Path'].strip('/').replace(':', '/') == path:
                return item['Selected']
        return False
    
    def set_selection(self, path: str, value: bool):
        for item in self._odmldict:
            if item['Path'].strip('/').replace(':', '/') == path:
                if not item['Selected'] == value:
                    item['Selected'] = value
                    self.create_private_odML()
                break


    # needs to be updated everytime the selection changes - some publish subscribe mechanism            
    def create_private_odML(self):
        #return private_odML_file
        self.private_odML = odml.Document()
        self.private_odML.author = self.doc.author
        self.private_odML.version = self.doc.version

        # experiment root element
        experiments_section = odml.Section(name=self.doc.sections["Experiments"].name, type=self.doc.sections["Experiments"].type, definition=self.doc.sections["Experiments"].definition)
        self.private_odML.append(experiments_section)

        # create a new odML with only the selected properties experiments = self.doc.sections["Experiments"]
        experiments = self.doc.sections["Experiments"]

        # think about how to handle lists of values 
        for experiment in experiments:
            # create experiment part
            experiment_section = odml.Section(name=experiment.name, type=experiment.type, definition=experiment.definition)
            experiments_section.append(experiment_section)

            for key, value in experiment_section_property_map.items():
                existing_properties = [v.name for v in experiment.sections[key].properties]

                curr_section = odml.Section(name=key, type=experiment.sections[key].type, definition=experiment.sections[key].definition)
                experiment_section.append(curr_section)
                
                for property in value:
                    if property in existing_properties:

                        path = "/Experiments/{}/{}:{}".format(experiment.name, key, property).strip('/').replace(':', '/')
                        if self.get_selection(path):
                            name = experiment.sections[key].properties[property].name
                            definition = experiment.sections[key].properties[property].definition
                            values = experiment.sections[key].properties[property].values
                            prop = odml.Property(name = name, definition = definition, values = values)
                            curr_section.append(prop)
            
                
            recordings_section = odml.Section(name=experiment.sections["Recordings"].name, type=experiment.sections["Recordings"].type, definition=experiment.sections["Recordings"].definition)
            experiment_section.append(recordings_section)

            for recording in experiment.sections["Recordings"]:
                recording_section = odml.Section(name=recording.name, type=recording.type, definition=recording.definition)
                recordings_section.append(recording_section)
                recording_id = recording.name
                for key, value in recording_section_property_map.items():
                    
                    curr_section = odml.Section(name=key, type=recording.sections[key].type, definition=recording.sections[key].definition)
                    recording_section.append(curr_section)

                    existing_properties = [v.name for v in recording.sections[key].properties]
                    for property in value:
                        if property in existing_properties:

                            path = "/Experiments/{}/Recordings/{}/{}:{}".format(experiment.name, recording_id, key, property).strip('/').replace(':', '/')
                            if self.get_selection(path):
                                curr_section.append(odml.Property(name = recording.sections[key].properties[property].name, definition = recording.sections[key].properties[property].definition, values = recording.sections[key].properties[property].values))

        return



    # for now only for experiment and recording template - maybe we can have a template/file this can be genrated from - as a next step
    def transform_to_single_table(self, private=False):

        full_experiment_columns = [key + " - " + value for key in experiment_section_property_map.keys() for value in experiment_section_property_map[key]]
        full_recording_columns = ["Recording - " + key + " - " + value for key in recording_section_property_map.keys() for value in recording_section_property_map[key]]
        columns = ["RecordingID"] + full_experiment_columns + full_recording_columns
        df = pd.DataFrame(columns=columns)

        #self.my_odml_dict = self.my_odml.get_dict()
        if private:
            self.create_private_odML()
            experiments = self.private_odML.sections["Experiments"]
        else:
            experiments = self.doc.sections["Experiments"]

        # think about how to handle lists of values 
        for experiment in experiments:
            # create experiment part
            experiment_info = []

            for key, value in experiment_section_property_map.items():
                existing_properties = [v.name for v in experiment.sections[key].properties]
                for property in value:
                    if property in existing_properties:
                        values = experiment.sections[key].properties[property].values
                        if values:
                            # only take first value for now - for MNG - there can always only be one value
                            experiment_info.append(values[0])
                        else:
                            experiment_info.append("")
                    else: 
                        experiment_info.append("")

            
            for recording in experiment.sections["Recordings"]:
                recording_info = []
                recording_id = recording.name
                for key, value in recording_section_property_map.items():
                    existing_properties = [v.name for v in recording.sections[key].properties]
                    for property in value:
                        if property in existing_properties:
                            values = recording.sections[key].properties[property].values
                            if values:
                                # only take first value for now - for MNG - there can always only be one value
                                recording_info.append(recording.sections[key].properties[property].values[0])
                            else:
                                recording_info.append("")
                        else: 
                            recording_info.append("")

                # insert infos of recording into df
                recording_line = [recording_id] + experiment_info + recording_info
                df.loc[len(df)] = recording_line
        
        return df
    
    # TODO later support more options than just csv :) 
    def save_private_summary_table(self, path):
        df = self.transform_to_single_table(private=True)
        df.to_csv(path, index=False)
        return path
    
    def save_private_odml_file(self, path):
        self.create_private_odML()
        odml.save(self.private_odML, path)
        return path
    