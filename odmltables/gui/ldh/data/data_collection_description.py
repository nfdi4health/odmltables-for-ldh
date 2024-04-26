import pandas as pd


class DataCollectionDescription():

    def __init__(self, odML_df: pd.DataFrame):
        self.odML_df = odML_df

    def create_species_description(self, species: str):


        df = self.odML_df[self.odML_df["Subject - Species"] == species]
        df_only_experiments = df.drop_duplicates(subset=["General - ExperimentID"])

        number_of_recording = len(df["RecordingID"].unique())
        number_of_subjects = len(df["Subject - SubjectID"].unique())
        number_of_experiments = len(df["General - ExperimentID"].unique())
        
        number_of_males = len(df_only_experiments[df_only_experiments["Subject - Sex"] == "m"])
        number_of_females = len(df_only_experiments[df_only_experiments["Subject - Sex"] == "f"])


        condition_list = df["Subject - HealthStatus"].unique()
        medication_list = df["Subject - MedicationChemicals"].unique()

        description = "The dataset contains {} recordings from {} {} subjects.\n".format(number_of_recording, number_of_subjects, species)
        description += "Of the {} subjects, there are {} male, {} female and {} other subjects.\n".format(species, number_of_males, number_of_females, max(0,(number_of_subjects - number_of_males - number_of_females)))
        
        
        unknown_age_count = len(df_only_experiments[df_only_experiments["Subject - Age"] == ""])
        description += "The subjects were between the age of {} and {} with an average age of {}. The age of {} subjects is unknown.\n".format(df["Subject - Age"].apply(pd.to_numeric, errors='coerce').min(), df["Subject - Age"].apply(pd.to_numeric, errors='coerce').max(), df["Subject - Age"].apply(pd.to_numeric, errors='coerce').mean(), unknown_age_count)

        #description += "The subjects consisted of {} males, {} females and {}, between the age of {} and {}, with an avergae age of {}.\n".format(number_of_males, number_of_females, (number_of_subjects - number_of_males - number_of_females), min_subject_age, max_subject_age, df["Subject - Age"].mean())
        description += "The subjects had the following health conditions: {}.\n".format(", ".join(condition_list))
        description += "The subjects were on the following medications: {}.\n".format(", ".join(medication_list))

        description += "\n"

        return description


    def create_context_description(self):
        description = "Context of Collection:\n\n"

        # TODO not from odML-File but from meta-data of Project - but this cannot be uploaded from odML-GUI - no API call exists
        # only possible if we have this information for an existing Project - not for a new one

        # list recording people and their insitutions 
        # TODO would be nice if we could link their profiles
        person_institution_list = []
        for institution in self.odML_df["General - Laboratory"].unique():
            for person in self.odML_df[self.odML_df["General - Laboratory"] == institution]["General - Experimenter"].unique():
                person_institution_list.append(person + " (" + institution + ")")
        description += "The following people have contributed to the data collection: {}\n".format(", ".join(person_institution_list))

        # TODO publishing info + sharing terms
        # # TODO link to study protocol
        # TODO Ethik-Votum

        return description



    def create_mng_description(self):

        df = self.odML_df.astype(str)

        description = "Microneurography Specific Information:\n\n"
        # marking method
        # for how many recordings MarkingUsed == True - for those we have BaseFrequency
        description += "Overall the Marking Method was used in {} recordings.\n".format(len(df[self.odML_df["Recording - MarkingMethod - MarkingUsed"] == True]))
        description += "The following Base Frequencies were used: {}.\n".format(", ".join(self.odML_df["Recording - MarkingMethod - BaseFrequency"].astype(str).unique()))

        # fiber type
        fiber_type_strings = self.odML_df["Recording - Fibers - FiberDescription"]
        fiber_types = []
        for f in fiber_type_strings:
            fiber_types.extend(f.split(","))

        fiber_type_string = ""
        for fiber_type in set(fiber_types):
            fiber_type_string += fiber_type + " (" + str(fiber_types.count(fiber_type)) + " recordings), "

        fiber_type_string = fiber_type_string[:-2]
        description += "The following fiber types were recorded: {}.\n".format(fiber_type)

        # Stimuli
        # electrical stimuli 
        electrical_stimuli = []
        for _, row in self.odML_df.astype(str).iterrows():
            device_name = row["Recording - ElectricalStimulus - DeviceName"]
            protocol = row["Recording - ElectricalStimulus - Protocol"]
            stimulation_dist = row["Recording - ElectricalStimulus - StimulationDist"]
            electrical_stimuli.append( "(" + device_name + ", " +  protocol + ", " + stimulation_dist + ")" )

        description += "The following electrical stimuli were used: {}.\n".format(", ".join(s for s in set(electrical_stimuli)))

        # heat stimulus
        heat_stimulus_count = len(self.odML_df[self.odML_df["Recording - HeatStimulus - HeatStimUsed"] == True])
        description += "Heat stimulus was used in {} recordings.\n".format(heat_stimulus_count)

        # mechanical stimulus
        mechanical_stimulus_count = len(self.odML_df[self.odML_df["Recording - MechanicalStimulus - MechStimUsed"] == True])
        description += "Mechanical stimulus was used in {} recordings.\n".format(mechanical_stimulus_count)

        # chemical stimulus
        chemical_stimulus_count = len(self.odML_df[self.odML_df["Recording - Chemicals - ChemicalsUsed"] == True])
        description += "Chemcials were used in {} recordings.\n".format(chemical_stimulus_count)
        if chemical_stimulus_count > 0:
            description += "The following chemicals were used: {}.\n".format(", ".join(self.odML_df[self.odML_df["Recording - Chemicals - ChemicalsUsed"] == True]["Recording - Chemicals - ChemicalName"].astype(str).unique()))
            description += "The chemical used was Unknown for {} recordings.\n".format(len(self.odML_df[self.odML_df[self.odML_df["Recording - Chemicals - ChemicalsUsed"] == True]["Recording - Chemicals - ChemicalName"].astype(str) == ""]))

        return description



    def create_description(self):

        self.description = ""
        
        species = self.odML_df["Subject - Species"].unique()
        self.description += "Demography of Dataset:\n\n"
        for s in species:
            self.description += self.create_species_description(s)

        self.description += "Data:\n"
        self.description += "The dataset consists of Signal Recordings.\n"
        self.description += "General Info about the dataset:\n"

        # no duration information in odml
        #self.description += "Duration of recordings: min-duration: {} max-duration: {} average-duration: {}\n".format(self.odML_df["Recording - Duration"].min(), self.odML_df["Recording - Duration"].max(), self.odML_df["Recording - Duration"].mean())

        # sampling rate
        self.description += "Sampling Rate: {} Hz.\n".format("Hz , ".join(self.odML_df["Recording - General - SamplingRate"].unique()))

        # TODO file format

        self.description += "Average Quality (1 - 3) (1: good, 2: medium, 3: bad): {}\n".format(self.odML_df["Recording - General - Quality"].mean())

        # software + version
        technology_string = "["
        for software in self.odML_df["Recording - General - Software"].unique():
            software_string = str(software) + " ( "
            for version in self.odML_df[self.odML_df["Recording - General - Software"] == software]["Recording - General - SoftwareVersion"].unique():
                software_string += version + " , "
            software_string += " )"
            technology_string += software_string + " , "
        technology_string += "]"

        self.description += "Software that has been used to record the data: " + technology_string + "\n"

        self.description += "\n"
        self.description += "\n"

        self.description += self.create_mng_description()

        self.description += "\n"
        self.description += "\n"

        # context

        self.description += self.create_context_description()

       



        return self.description
 
        #number_of_recording = len(self.odML_df["RecordingID"].unique())
        #number_of_subjects = len(self.odML_df["SubjectID"].unique())
        #number_of_experiments = len(self.odML_df["General - ExperimentID"].unique())

        # list of conditions


