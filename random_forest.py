# Final Project Random Forest Regressor
# Iteration one
# John Bozzella

from sklearn.ensemble import RandomForestRegressor
#from sklearn.feature_selection import SelectFromModel
import pandas as pd 
import numpy as np
from rawdatanosent import data, testtranscriptdata

data = data		#data imported from a different file
data = np.array(data)

rawtestdata = testtranscriptdata
rawtestdata = np.array(rawtestdata)

var_names = ['word_count', 'mention_count', 'accessory_count', 'poll_data']

traindata = pd.DataFrame(data, columns = var_names)

testdata = pd.DataFrame(rawtestdata, columns = var_names)



# Define arrays to input into the regressor.

X_train = traindata.drop('poll_data', axis = 1)		# numpy.array containing all of the parameter data from the historical transcripts  (name open to change)
y_train = traindata.poll_data						# numpy.array containing all of the poll data corresponding to the historical debates (name open to change)
X_test = testdata.drop('poll_data', axis = 1)		# numpy.array containing the parameter daya from the desired test transcripts (name open to change)
y_test = testdata.poll_data							# numpy.array containing the resulting poll data (if known, this is opitonal) (name open to change)


# Define number of trials and while loop variables, as well as accuracy and prediction arrays
num_trials = 50
training = True
i = 0

trial_accuracies = np.zeros(num_trials)
trial_predictions = np.zeros((num_trials,len(X_test)))


while training:		# Loops until the number of trails has been completed, puts the accuracy from each trial into an array to be averaged. 
	i = i+1		

	model = RandomForestRegressor(n_jobs = 2)
	model.fit(X_train, y_train)

	prediction = model.predict(X_test)			# actual prediction of the trial (is the mean of the predictions from each tree)
	trial_predictions[i-1] = prediction

	trialaccuracy = model.score(X_test,y_test)		#this only works if we know the resulting poll data from the test transcript, therefore it really is only for testing purposes
	trial_accuracies[i-1]=trialaccuracy

	importances = model.feature_importances_
	indices = np.argsort(importances)[::-1]



	if i == num_trials:
		training = False


test_accuracy = np.mean(trial_accuracies)
test_prediction = [np.mean(trial_predictions[:,0]), np.mean(trial_predictions[:,1])]

print "Test Accuracy:"
print test_accuracy
print "Test Predictions:"
print test_prediction


#Table of feature rankings
imptable = pd.DataFrame(zip(X_train.columns, importances), columns = ['Features', 'Estimated Importance'])
print imptable




