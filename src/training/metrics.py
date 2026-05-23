from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support
)

def compute_metrics(
    eval_pred
):

    logits,labels = eval_pred

    preds = logits.argmax(
        axis=-1
    )

    precision,recall,f1,_ = (
        precision_recall_fscore_support(
            labels,
            preds,
            average="macro"
        )
    )

    acc = accuracy_score(
        labels,
        preds
    )

    return {

        "accuracy":acc,

        "precision":precision,

        "recall":recall,

        "macro_f1":f1

    }