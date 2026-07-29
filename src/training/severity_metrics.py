import numpy as np
from sklearn.metrics import precision_recall_fscore_support


def compute_metrics_factory(categories: list[str]):
    """Builds a Trainer-compatible compute_metrics for the multi-label presence
    head: logits are (N, num_categories) raw scores, thresholded at 0.5 after
    sigmoid to get a binary flag per category, since a text can be flagged on
    more than one category at once.
    """

    def compute_metrics(eval_pred):
        logits, labels = eval_pred
        probs = 1 / (1 + np.exp(-logits))
        preds = (probs >= 0.5).astype(int)
        labels = labels.astype(int)

        per_category_f1 = []
        for i in range(len(categories)):
            _, _, f1, _ = precision_recall_fscore_support(
                labels[:, i], preds[:, i], average="binary", zero_division=0
            )
            per_category_f1.append(f1)

        exact_match = float(np.mean(np.all(preds == labels, axis=1)))

        return {
            "macro_f1": float(np.mean(per_category_f1)),
            "exact_match": exact_match,
        }

    return compute_metrics
