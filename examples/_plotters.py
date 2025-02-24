import matplotlib.pyplot as plt
import numpy as np


def plot_serde_speed_chart(libraries: list[str], times: list[float], messages: list[int]) -> None:
    # libraries = ["vanilla python", "attrs", "dataclass", "pydantic"]
    # times = [van_time, attrs_time, dc_time, pd_time]
    # messages = [van_msgs, attrs_msgs, dc_msgs, pd_msgs]

    # Calculate y positions for bars
    y_pos = np.arange(len(libraries))
    width = 0.35  # Width of bars
    y1 = y_pos - width / 2  # First set of bars
    y2 = y_pos + width / 2  # Second set of bars
    fig, ax1 = plt.subplots()

    ax1.set_xlabel("Serde time (microseconds)")
    ax1.set_ylabel("Library")
    ax1.barh(y1, times, height=0.9 * width, color="blue", label="Time")
    ax1.set_yticks(y_pos)
    ax1.set_yticklabels(libraries)

    ax2 = ax1.twiny()
    ax2.set_xlabel("Maximal throughput (messages/sec)")
    ax2.barh(y2, messages, height=0.9 * width, color="red", alpha=0.5, label="Throughput")
    ax2.set_xticks(np.arange(start = 0, stop=max(messages) + 5_000, step=10_000))

    plt.title("Library Performance Comparison")
    ax2.legend(loc="center left", bbox_to_anchor=(1.0, 0.3))
    ax1.legend(loc="center left", bbox_to_anchor=(1.0, 0.5))

    fig.tight_layout(rect=[0, 0, 0.9, 1])
    fig.tight_layout()
    plt.savefig("outputs/serde_speed.png")
    plt.show()
