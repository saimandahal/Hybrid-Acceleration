import pandas as pd
import numpy as np

# Dataloader
# Proprocessing
class WeatherLoader:
    
    def __init__(self, csv_paths):
        self.data = {}
        
        for path in csv_paths:
            
            location_name = path.split('/')[-1].split('.')[0]
            self.data[location_name] = pd.read_csv(path , dtype='unicode')
            
            self.data[location_name].rename(columns=lambda x: x.strip(), inplace=True)
            
            self.data[location_name] = self.data[location_name].applymap(lambda x: x.strip() if isinstance(x, str) and x.startswith(' ') else (x.strip() if isinstance(x, str) else x))
            

    def normalizeCols(self,data, cols):
        
        temp_df = data.copy(deep = True)
        temp_df.loc[:,cols] = (temp_df.loc[:, cols] - temp_df.loc[:,cols].min())/(temp_df.loc[:, cols].max() - temp_df.loc[:,cols].min())
    
        return temp_df
    
    def cleanData(self):
    
        all_dates = []
        for location_name, location_data in self.data.items():

            cols=['LATITUDE', 'LONGITUDE', 'ELEVATION_FEET', 'AIR_TEMP_F','SECOND_AIR_TEMP_F','RELATIVE_HUMIDITY_%','DEWPOINT_F','LEAF_WETNESS','PRECIP_INCHES',
                                'WIND_DIRECTION_DEG','WIND_SPEED_MPH','SOLAR_RAD_WM2','SOIL_TEMP_8_IN_DEGREES_F']
            
            for col in cols:
                location_data[col] = pd.to_numeric(location_data[col])

            columns_to_drop = ['TSTAMP_HOUR', 'MIN_TSTAMP_PST', 'STATION_NAME', 'UNIT_ID']
            location_data = location_data.drop(columns=[col for col in columns_to_drop if col in location_data.columns])

            location_data[cols] = location_data[cols].fillna(0)

            location_data['MAX_TSTAMP_PST'] = pd.to_datetime(location_data['MAX_TSTAMP_PST'])
            location_data['DATE'] = location_data['MAX_TSTAMP_PST'].dt.date
            location_data['DATE'] = pd.to_datetime(location_data['DATE'])  # Convert DATE column to datetime

            location_data = location_data.drop(columns='MAX_TSTAMP_PST')

            all_dates.append(location_data['DATE'])


            self.data[location_name] = location_data
        sets = [set(lst) for lst in all_dates]

        included_values = set.intersection(*sets)

        # Filter data based on common dates

        for location_name, location_data in self.data.items():

            self.data[location_name] = location_data.loc[location_data['DATE'].isin(included_values),:]


    def getModelInputsAndOutputs(self):

        model_inputs = []
        model_outputs = []
        
        for location_name, location_data in self.data.items():

            elev = (location_data['ELEVATION_FEET'] - location_data['ELEVATION_FEET'].mean()) / (location_data['ELEVATION_FEET'].std())
            lat = (location_data['LATITUDE'] - location_data['LATITUDE'].mean()) / (location_data['LATITUDE'].std())
            long = (location_data['LONGITUDE'] - location_data['LONGITUDE'].mean()) / (location_data['LONGITUDE'].std())
            spatial_feature = np.array([elev,lat,long ])
            spatial_feature= spatial_feature.T


            required_columns = ['LATITUDE', 'LONGITUDE', 'ELEVATION_FEET', 'AIR_TEMP_F','SECOND_AIR_TEMP_F','RELATIVE_HUMIDITY_%','DEWPOINT_F','LEAF_WETNESS','PRECIP_INCHES',
                                'WIND_DIRECTION_DEG','WIND_SPEED_MPH','SOLAR_RAD_WM2','SOIL_TEMP_8_IN_DEGREES_F']
            location_data[required_columns] = location_data[required_columns].replace('', '0')

            inputs = location_data[required_columns].values
            outputs = location_data['AIR_TEMP_F'].values.reshape(-1, 1)

            merged_values = np.insert(inputs, [0,1,2], spatial_feature, axis=1) 
           
                                
            model_inputs.append(inputs)
            model_outputs.append(outputs)
        
        max_length = max(len(arr) for arr in model_inputs)
        model_inputs_padded = [np.pad(arr, ((0, max_length - len(arr)), (0, 0)), mode='constant', constant_values=0) for arr in model_inputs]

        max_length_1 = max(len(arr) for arr in model_outputs)
        model_output_padded = [np.pad(arr, ((0, max_length_1 - len(arr)), (0, 0)), mode='constant', constant_values=0) for arr in model_outputs]


        locations , days , input_feature_dim = np.array(model_inputs_padded).shape
        locations , days , output_feature_dim = np.array(model_output_padded).shape

        model_inputs_padded = np.concatenate(model_inputs_padded, axis = 1).reshape(days,locations,input_feature_dim)
        model_output_padded =np.concatenate(model_output_padded, axis = 1).reshape(days,locations,output_feature_dim)


        return (model_inputs_padded, model_output_padded)
    
    # Feature generation

    def generateBatches(self, data, batch_size):
        # Generate batches of data
        num_batches = len(data) // batch_size
        return np.array_split(data, num_batches)
    
    
    # Training data 
    
    def getTrainingData(self, batch_size=1):
        model_inputs, model_outputs = self.getModelInputsAndOutputs()

        input_batches = self.generateBatches(model_inputs, batch_size)
        output_batches = self.generateBatches(model_outputs, batch_size)

        input_batches_shuffled = []
        for batch in input_batches:
            shuffled_batch = np.random.permutation(batch)
            input_batches_shuffled.append(shuffled_batch)

        output_batches_shuffled = []
        for batch in output_batches:
            shuffled_batch = np.random.permutation(batch)
            output_batches_shuffled.append(shuffled_batch)

        return input_batches_shuffled, output_batches_shuffled
        
        
    # Testing data 
    def getTestingData(self):
        test_data = {}
        test_model_inputs = []
        test_model_outputs = []

        for location_name, location_data in self.data.items():

            test_data[location_name] = location_data[location_data['DATE'].dt.year.isin([2018, 2020])] 
            self.data[location_name] = self.data[location_name][~self.data[location_name]['DATE'].dt.year.isin([2018, 2020])]


            elev = (test_data[location_name]['ELEVATION_FEET'] - test_data[location_name]['ELEVATION_FEET'].mean()) / (test_data[location_name]['ELEVATION_FEET'].std())
            lat = (test_data[location_name]['LATITUDE'] - test_data[location_name]['LATITUDE'].mean()) / (test_data[location_name]['LATITUDE'].std())
            long = (test_data[location_name]['LONGITUDE'] - test_data[location_name]['LONGITUDE'].mean()) / (test_data[location_name]['LONGITUDE'].std())
            spatial_feature = np.array([elev,lat,long])
            spatial_feature = spatial_feature.T

            required_columns = ['LATITUDE', 'LONGITUDE', 'ELEVATION_FEET', 'AIR_TEMP_F','SECOND_AIR_TEMP_F','RELATIVE_HUMIDITY_%','DEWPOINT_F','LEAF_WETNESS','PRECIP_INCHES',
                                'WIND_DIRECTION_DEG','WIND_SPEED_MPH','SOLAR_RAD_WM2','SOIL_TEMP_8_IN_DEGREES_F']

            inputs = test_data[location_name][required_columns].values
            outputs = test_data[location_name]['AIR_TEMP_F'].values.reshape(-1, 1)

            merged_values = np.insert(inputs, [0,1,2], spatial_feature, axis=1)

            test_model_inputs.append(inputs)
            test_model_outputs.append(outputs)

        max_length = max(len(arr) for arr in test_model_inputs)
        test_model_inputs_padded = [np.pad(arr, ((0, max_length - len(arr)), (0, 0)), mode='constant', constant_values=0) for arr in test_model_inputs]

        max_length_1 = max(len(arr) for arr in test_model_outputs)
        test_model_output_padded = [np.pad(arr, ((0, max_length_1 - len(arr)), (0, 0)), mode='constant', constant_values=0) for arr in test_model_outputs]

        locations , days , input_feature_dim = np.array(test_model_inputs_padded).shape
        locations , days , output_feature_dim = np.array(test_model_output_padded).shape

        test_model_inputs_padded = np.concatenate(test_model_inputs_padded, axis = 1).reshape(days,locations,input_feature_dim)
        test_model_output_padded =np.concatenate(test_model_output_padded, axis = 1).reshape(days,locations,output_feature_dim)

        test_input_batches = self.generateBatches(test_model_inputs_padded, 1)
        test_output_batches = self.generateBatches(test_model_output_padded, 1)

        return (test_input_batches, test_output_batches)
