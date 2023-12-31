"""Replay demonstration of FID sequence with projection gradient."""
# %%
# imports
import time

from console.pulseq_interpreter.interface_unrolled_sequence import UnrolledSequence
from console.utilities.load_config import get_instances
from console.utilities.plot_unrolled_sequence import plot_unrolled_sequence

# %%
# Get sequence provider object and read sequence
provider, tx_card, _ = get_instances("../device_config.yaml")

provider.max_amp_per_channel = tx_card.max_amplitude
provider.read("../sequences/export/fid_proj.seq")

# Unroll and plot sequence
sqnc: UnrolledSequence = provider.unroll_sequence()

fig, ax = plot_unrolled_sequence(sqnc, use_time=True)
fig.show()

# %%
# Connect to card and replay sequence
tx_card.connect()
time.sleep(1)
tx_card.start_operation(sqnc)
time.sleep(3)
tx_card.stop_operation()
tx_card.disconnect()

# %%
