"""."""
import pandas as pd


def plot_training_results(results):
    """."""
    pd.DataFrame(results.history).plot(title="Training History")
