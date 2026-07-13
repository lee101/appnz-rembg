import importlib.util
import pathlib
import sys
import types
import unittest


class _Input:
    def __init__(self, **_kwargs):
        pass


class _BaseRunner:
    pass


stub = types.ModuleType("cog")
stub.BaseRunner = _BaseRunner
stub.Input = _Input
stub.Path = pathlib.Path
sys.modules.setdefault("cog", stub)

spec = importlib.util.spec_from_file_location("predict", pathlib.Path(__file__).parents[1] / "predict.py")
predict = importlib.util.module_from_spec(spec)
spec.loader.exec_module(predict)


class PredictContractTest(unittest.TestCase):
    def test_supported_model_has_safe_output(self):
        self.assertEqual(predict.output_path("u2netp").name, "appnz-rembg-u2netp.png")

    def test_unknown_model_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "unsupported model"):
            predict.output_path("../../escape")

    def test_schema_and_runner_match(self):
        import json

        schema = json.loads((pathlib.Path(__file__).parents[1] / "appnz.schema.json").read_text())
        self.assertEqual(schema["outputKind"], "image")
        self.assertEqual(schema["inputs"][1]["choices"], list(predict.MODELS))


if __name__ == "__main__":
    unittest.main()
