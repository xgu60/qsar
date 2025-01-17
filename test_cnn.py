from data_loader import getValidationData
from evaluation import pearson_r_square, calculate_SSA
import torch
from torch.autograd import Variable
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def test_model(folder, visual, savePoints):	
	TURNON_VISUAL = visual
	NET_SAVE_POINTS = savePoints
	TRAIN_PRED = []	
	VAL_PRED = []
	folderpath = folder
	TRAIN_FILE = "data/training.csv"
	VALIDATION_FILE = "data/validation.csv"

	train_data, train_label = getValidationData(folderpath + TRAIN_FILE)
	val_data, val_label = getValidationData(folderpath + VALIDATION_FILE)
	
	train_data = Variable(train_data.view((train_data.size(0), 1, 64, 64)))
	val_data = Variable(val_data.view((val_data.size(0), 1, 64, 64)))		

	for epoch in NET_SAVE_POINTS:
		net = torch.load(folderpath + 'net/epoch' + str(epoch) + '.pkl')
		net.cpu()
		net.eval()
		train_pred = net(train_data)
		val_pred = net(val_data)		
		TRAIN_PRED.append(train_pred)	
		VAL_PRED.append(val_pred)

	#average the prediction
	train_pred_sum = torch.cat(TRAIN_PRED, 1)
	train_pred_mean = torch.mean(train_pred_sum, 1, True)
	val_pred_sum = torch.cat(VAL_PRED, 1)
	val_pred_mean = torch.mean(val_pred_sum, 1, True)
	#convert data to numpy array for further analysis
	train_pred = train_pred_mean.data.cpu().numpy()
	train_label = train_label.numpy()
	val_pred = val_pred_mean.data.cpu().numpy()
	val_label = val_label.numpy()
	#calculate r square 
	train_r2 = pearson_r_square(train_pred, train_label)
	val_r2 = pearson_r_square(val_pred, val_label)
	print(train_r2, val_r2)
	#plot the correlation between predict and label of test
	if TURNON_VISUAL:
		plt.xlabel('Predicted pIC50', fontsize=20)
		plt.ylabel('True pIC50', fontsize=20)
		plt.grid(True)		
		plt.scatter(train_pred, train_label, c='r', alpha=0.4)
		plt.scatter(val_pred, val_label, c='b')
		plt.text(3.0, 10, "Training $R^2$ = %4.2f"%train_r2, size=20, color="red", alpha=0.5)
		plt.text(3.0, 9, "Validation $R^2$ = %4.2f"%val_r2, size=20, color="blue")	
		plt.show()

		plt.xlabel('Predicted pIC50', fontsize=20)
		plt.ylabel('True pIC50', fontsize=20)
		plt.grid(True)		
		plt.scatter(val_pred, val_label, c='b')		
		plt.text(3.0, 10, "Validation $R^2$ = %4.2f"%val_r2, size=20, color="blue")	
		plt.show()

	
	
	#calculate sensitivity, selectivity and accuracy
	roc_data = calculate_SSA(val_pred, val_label, 5, 2, 10, 0.2)
	#print(roc_data)
	#df = pd.DataFrame(roc_data, columns=["pIC50", "TPR", "FPR", "Accuracy"])
	#df.to_csv("roc_table.csv")
	auc = np.trapz(roc_data[::-1, 1], roc_data[::-1, 2])
	print(auc)

	#plot roc
	if TURNON_VISUAL:
		plt.xlabel('FPR (1 - specificity)', fontsize=20)
		plt.ylabel('TPR (sensitivity)', fontsize=20)
		#plt.grid(True)	
		plt.plot(roc_data[:, 2], roc_data[:, 1], 'g-')
		plt.plot([0, 1], [0, 1], 'r-')
		plt.text(0.6, 0.1, "AUC = %4.2f"%auc, size=20)
		plt.show()

	return train_r2, val_r2, auc


if __name__ == "__main__":
	print(test_model("bace/", True, [80, 90, 100]))
	
