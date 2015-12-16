# Final Project Random Forest Regressor
# Iteration one
# John Bozzella

from sklearn.ensemble import RandomForestRegressor
import pandas as pd 
import numpy as np 

data = []		#ideally a call of the function that we made that outputs all of our data, should probably be imported from a different file

num_trials = 3
test_accuracies = numpy.zeros(len(train_percentages))
training = True
i = 0
trial_accuracies = numpy.zeros(num_trials)
trial_predictions = numpy.zeros(num_trials)


while training:		# Loops until the number of trails has been completed, puts the accuracy from each trial into an array to be averaged. 
	i = i+1

	# Define arrays to input into the regressor.
	X_train = data.historicaltranscriptdata		# numpy.array containing all of the parameter data from the historical transcripts  (name open to change)
	y_train = data.polldata						# numpy.array containing all of the poll data corresponding to the historical debates (name open to change)
	X_test = data.testtranscriptdata			# numpy.array containing the parameter daya from the desired test transcripts (name open to change)
	y_test = data.resultpolldata				# numpy.array containing the resulting poll data (if known, this is opitonal) (name open to change)

	model = RandomForestRegressor(n_jobs = 2)
	model.fit(X_train, y_train)

	prediction = model.predict(X_test)			# actual prediction of the trial (is the mean of the predictions from each tree)
	trial_predictions[i-1] = prediction

	trialaccuracy = model.score(X_test,y_test)		#this only works if we know the resulting poll data from the test transcript, therefore it really is only for testing purposes
	trial_accuracies[i-1]=trialaccuracy

	if i == num_trials-1:
		training = False

final_prediction = numpy.mean(predictions)
test_accuracy = numpy.mean(trial_accuracies)



