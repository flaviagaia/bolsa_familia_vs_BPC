from __future__ import annotations

from pathlib import Path
import sys
import unittest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.pipeline import build_comparison_dataset, build_summary_dict


class PipelineTest(unittest.TestCase):
    def test_outputs_expected_comparison_summary(self) -> None:
        comparison_df = build_comparison_dataset()
        summary = build_summary_dict(comparison_df)

        self.assertEqual(summary["ano_referencia"], 2023)
        self.assertEqual(summary["municipios_cobertos"], 102)
        self.assertAlmostEqual(comparison_df["participacao_bolsa_pct"].add(comparison_df["participacao_bpc_pct"]).mean(), 100.0, places=1)
        self.assertIn("municipio_maior_volume_total", summary)
        self.assertGreater(summary["taxa_media_judicializacao_bpc_pct"], 5.0)


if __name__ == "__main__":
    unittest.main()
