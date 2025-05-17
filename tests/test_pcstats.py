from unittest.mock import patch
from scripts.pcstats import get_pc_stats

@patch("scripts.pcstats.psutil.cpu_percent", return_value=42.5)
@patch("scripts.pcstats.psutil.virtual_memory")
@patch("scripts.pcstats.psutil.disk_usage")
def test_get_pc_stats(mock_disk, mock_vm, mock_cpu):
    # ret vals for memory and disk mocks
    mock_vm.return_value.percent = 66.6
    mock_disk.return_value.percent = 77.7

    stats = get_pc_stats()

    assert stats["CPU Usage"] == "42.5%"
    assert stats["RAM Usage"] == "66.6%"
    assert stats["Disk Usage"] == "77.7%"

