import matplotlib.pyplot as plt
import numpy as np


def plot_digit_histograms(train_data: np.ndarray, test_data: np.ndarray,
                          title: str = "Distribution of Digits (0-9)") -> None:
    """
    Plots two histograms side-by-side: one for the training data and one for 
    the test data, focusing on the distribution of digits (0-9).

    Args:
        train_data (np.ndarray): Array of training data digits (integers 0-9).
        test_data (np.ndarray): Array of test data digits (integers 0-9).
        title (str): The main title for the entire figure.
    """

    # --- Setup for plotting ---
    # Create bins to explicitly isolate each integer from 0 to 9.
    # The bins will be: [-0.5, 0.5, 1.5, ..., 9.5, 10.5]
    bins = np.arange(11) - 0.5

    # Create a figure and a set of subplots (1 row, 2 columns)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    fig.suptitle(title, fontsize=16, fontweight='bold')

    # Define custom colors
    train_color = '#4CAF50'  # Green
    test_color = '#2196F3'  # Blue

    # --- Plot 1: Training Data Histogram ---
    ax1.hist(train_data, bins=bins, color=train_color, edgecolor='black', rwidth=0.85, alpha=0.7)

    # Set labels, title, and ticks
    ax1.set_title(f"Training Data (N={len(train_data)})", fontsize=14)
    ax1.set_xlabel("Digit Value", fontsize=12)
    ax1.set_ylabel("Frequency (Count)", fontsize=12)
    ax1.set_xticks(range(10))  # Ensure only 0-9 are labeled on the x-axis
    ax1.set_xlim(-1, 10)  # Set sensible limits
    ax1.grid(axis='y', alpha=0.5, linestyle='--')

    # --- Plot 2: Test Data Histogram ---
    ax2.hist(test_data, bins=bins, color=test_color, edgecolor='black', rwidth=0.85, alpha=0.7)

    # Set labels, title, and ticks
    ax2.set_title(f"Test Data (N={len(test_data)})", fontsize=14)
    ax2.set_xlabel("Digit Value", fontsize=12)
    ax2.set_ylabel("Frequency (Count)", fontsize=12)
    ax2.set_xticks(range(10))  # Ensure only 0-9 are labeled on the x-axis
    ax2.set_xlim(-1, 10)  # Set sensible limits
    ax2.grid(axis='y', alpha=0.5, linestyle='--')

    # Adjust layout to prevent overlapping titles/labels
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])

    # Display the plot
    plt.show()


# --- Example Usage ---

# 1. Generate synthetic data resembling digit labels (0-9)
# Training data: slightly skewed towards lower digits
np.random.seed(42)
train_samples = 5000
train_data_example = np.random.choice(range(10), size=train_samples,
                                      p=[0.15, 0.15, 0.1, 0.1, 0.1, 0.08, 0.08, 0.08, 0.08, 0.08])

# Test data: more uniformly distributed
test_samples = 1000
test_data_example = np.random.randint(0, 10, size=test_samples)

# 2. Call the function
plot_digit_histograms(
    train_data=train_data_example,
    test_data=test_data_example,
    title="Comparison of Digit Label Distribution"
)

print("Histograms generated successfully.")
import matplotlib.pyplot as plt
import numpy as np


def plot_digit_histograms(train_data: np.ndarray, test_data: np.ndarray,
                          title: str = "Distribution of Digits (0-9)") -> None:
    """
    Plots two histograms side-by-side: one for the training data and one for
    the test data, focusing on the distribution of digits (0-9).

    Args:
        train_data (np.ndarray): Array of training data digits (integers 0-9).
        test_data (np.ndarray): Array of test data digits (integers 0-9).
        title (str): The main title for the entire figure.
    """

    # --- Setup for plotting ---
    # Create bins to explicitly isolate each integer from 0 to 9.
    # The bins will be: [-0.5, 0.5, 1.5, ..., 9.5, 10.5]
    bins = np.arange(11) - 0.5

    # Create a figure and a set of subplots (1 row, 2 columns)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    fig.suptitle(title, fontsize=16, fontweight='bold')

    # Define custom colors
    train_color = '#4CAF50'  # Green
    test_color = '#2196F3'  # Blue

    # --- Plot 1: Training Data Histogram ---
    ax1.hist(train_data, bins=bins, color=train_color, edgecolor='black', rwidth=0.85, alpha=0.7)

    # Set labels, title, and ticks
    ax1.set_title(f"Training Data (N={len(train_data)})", fontsize=14)
    ax1.set_xlabel("Digit Value", fontsize=12)
    ax1.set_ylabel("Frequency (Count)", fontsize=12)
    ax1.set_xticks(range(10))  # Ensure only 0-9 are labeled on the x-axis
    ax1.set_xlim(-1, 10)  # Set sensible limits
    ax1.grid(axis='y', alpha=0.5, linestyle='--')

    # --- Plot 2: Test Data Histogram ---
    ax2.hist(test_data, bins=bins, color=test_color, edgecolor='black', rwidth=0.85, alpha=0.7)

    # Set labels, title, and ticks
    ax2.set_title(f"Test Data (N={len(test_data)})", fontsize=14)
    ax2.set_xlabel("Digit Value", fontsize=12)
    ax2.set_ylabel("Frequency (Count)", fontsize=12)
    ax2.set_xticks(range(10))  # Ensure only 0-9 are labeled on the x-axis
    ax2.set_xlim(-1, 10)  # Set sensible limits
    ax2.grid(axis='y', alpha=0.5, linestyle='--')

    # Adjust layout to prevent overlapping titles/labels
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])

    # Display the plot
    plt.show()



