from sklearn import metrics
import numpy as np

# def compute_acc(self,list_scores,list_labels,thr):
#     labels = np.array(list_labels)
#     scores_th = (np.array(list_scores) >= thr).astype(np.int32)
#     acc = (scores_th==labels).sum()/labels.size
#     return acc

# def compute_best_accuracy(predictions, n_samples=100):
#     acc_thrs = []
#     min_thr = min(predictions)
#     max_thr = max(predictions)
#     all_thrs = np.linspace(min_thr,max_thr,n_samples).tolist()
#     for t in all_thrs:
#         acc = self.compute_acc(self.predictions,self.gt,t)
#         acc_thrs.append((t,acc))
#     acc_thrs_arr = np.array(acc_thrs)
#     idx_max = acc_thrs_arr[:,1].argmax()
#     best_thr = acc_thrs_arr[idx_max,0]
#     best_acc = acc_thrs_arr[idx_max,1]
#     return best_thr, best_acc

def get_tpr_at_fpr(tpr_lst, fpr_lst, score_lst, fpr_value):
    abs_fpr = np.absolute(fpr_lst - fpr_value)
    idx = np.argmin(abs_fpr)
    return tpr_lst[idx], score_lst[idx]


def my_metrics(label_list, pred_list, val_phase=False):

	fpr, tpr, scores = metrics.roc_curve(label_list,pred_list,
										 drop_intermediate=True)
	auc_score = metrics.auc(fpr,tpr)
	fnr = 1 - tpr
	tnr = 1 - fpr
	# print(tpr)
	# print(fnr)
	# import sys;sys.exit(0)
	EER0 = fpr[np.nanargmin(np.absolute((fnr - fpr)))]
	EER1 = fnr[np.nanargmin(np.absolute((fnr - fpr)))]
	EER  = min(EER0, EER1) 

	## different fpr threshold can be chosen.
	## GX: you can iterate all threshold returned, then get the best one.
	# abs_fpr = np.absolute(fpr - 0.01)
	# idx = np.argmin(abs_fpr)

	# ACER_list = []
	best_ACER, best_AP, best_BP = 100, 100, 100
	best_threshold = 100
	for idx_ in range(len(tpr)):
		# print("the tpr length: ")
		# print(len(tpr))
		# print(tpr)
		# print()
		# print(fpr)
		# print()
		# print(scores)
		
		_tpr, _fpr = tpr[idx_], fpr[idx_]
		# _fnr = fnr[idx]
		_tnr, _fnr = tnr[idx_], fnr[idx_]
		assert _tpr + _fnr == 1, print(_tpr, _fnr)
		assert _tnr + _fpr == 1, print(_tnr, _fpr)

		APCER = _fpr/(_fpr+_tnr)
		BPCER = _fnr/(_fnr+_tpr)
		ACER  = 0.5 * (APCER+BPCER)
		if ACER < best_ACER:
			best_ACER = ACER
			best_AP   = APCER
			best_BP   = BPCER
			best_threshold = scores[idx_]
		# import sys;sys.exit(0)
		# ACER_list.append((scores[idx_],ACER))

	# print(ACER_list)

	# idx_best = ACER_list[:,1].argmin()
	# print(acc_thrs_arr[idx_best][0])
	# print(acc_thrs_arr[idx_best][1])
	# print(ACER_list)
	# print(best_ACER, best_threshold)
	# import sys;sys.exit(0)

	## GX: per paper, fnr == 0.5%
	abs_fnr = np.absolute(fnr - 0.005)
	idx = np.argmin(abs_fnr)
	res_tpr = tpr[idx]

	if not val_phase:
		tpr_h, _ = get_tpr_at_fpr(tpr, fpr, scores, 0.002)	# 5%
		tpr_m, _ = get_tpr_at_fpr(tpr, fpr, scores, 0.005)	# 3%
		tpr_l, _ = get_tpr_at_fpr(tpr, fpr, scores, 0.01)	# 1%

		return best_AP, best_BP, best_ACER, EER, res_tpr, auc_score, [tpr_h, tpr_m, tpr_l]
	else:
		return best_AP, best_BP, best_ACER, EER, res_tpr, auc_score
