# tests/test_kernel.py
import unittest
from unittest.mock import patch, MagicMock
import time
from src.kernel import CoherenceKernel, Regime, KernelSnapshot, Priority, SystemHalt, LoadShed
import src.metrics as m

class TestCoherenceKernel(unittest.TestCase):
    def setUp(self):
        self.kernel = CoherenceKernel()

    def test_metrics_clamp(self):
        self.assertEqual(m.clamp(1.5), 1.0)
        self.assertEqual(m.clamp(-0.5), 0.0)
        self.assertEqual(m.compute_phi1(0, 0.5), 0.0)
        self.assertAlmostEqual(m.compute_phi1(10, 0.5), 0.993, places=3)

    def test_regime_transition(self):
        # Force risk high
        with patch('src.kernel.CoherenceKernel.snapshot') as mock_snap:
            # Mock internal state or manually set
            self.kernel._regime = Regime.STABLE
            
            # Manually trigger update logic
            r = self.kernel._update_regime(0.10)
            self.assertEqual(r, Regime.STABLE)
            
            r = self.kernel._update_regime(0.25)
            self.assertEqual(r, Regime.PRESSURE)
            
            self.kernel._regime = Regime.PRESSURE
            r = self.kernel._update_regime(0.60)
            self.assertEqual(r, Regime.UNSTABLE)
            
            self.kernel._regime = Regime.UNSTABLE
            r = self.kernel._update_regime(0.85)
            self.assertEqual(r, Regime.FAILURE)

    def test_enforcement_hooks(self):
        # STABLE -> OK
        snap = self.kernel.check_stability_preflight()
        self.assertEqual(snap.regime, Regime.STABLE)
        
        # UNSTABLE -> LoadShed low priority
        self.kernel._regime = Regime.UNSTABLE
        with patch.object(self.kernel, 'snapshot') as mock_snap:
            mock_snap.return_value = KernelSnapshot(
                time.time(), 0,0,0,0,0, 0.6, 0.4, 0, 1, 0, Regime.UNSTABLE
            )
            with self.assertRaises(LoadShed):
                self.kernel.check_stability_preflight(Priority.LOW)
            
            # HIGH priority ok
            self.kernel.check_stability_preflight(Priority.HIGH)

    def test_panic_persistence(self):
        self.kernel._regime = Regime.FAILURE
        with patch.object(self.kernel, 'snapshot') as mock_snap:
            mock_snap.return_value = KernelSnapshot(
                time.time(), 0,0,0,0,0, 0.9, 0.1, 0, 1, 0, Regime.FAILURE
            )
            with patch("builtins.open", unittest.mock.mock_open()) as mock_file:
                with self.assertRaises(SystemHalt):
                    self.kernel.check_stability_preflight()
                mock_file.assert_called_with("data/state/panic.log", "a")

if __name__ == "__main__":
    unittest.main()
