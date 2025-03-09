from testora.util.PythonCodeUtil import get_locations_of_calls
from multilspy import SyncLanguageServer
from multilspy.multilspy_config import MultilspyConfig
from multilspy.multilspy_logger import MultilspyLogger
from pathlib import Path


class PythonLanguageServer:
    def __init__(self, repo_path):
        config = MultilspyConfig.from_dict({"code_language": "python"})
        logger = MultilspyLogger()
        absolute_repo_path = str(Path(repo_path).resolve())
        self.lsp = SyncLanguageServer.create(
            config, logger, absolute_repo_path)

    def get_hover_text(self, file_path, line, column):
        with self.lsp.start_server():
            raw_result = self.lsp.request_hover(file_path, line, column)
            if type(raw_result) == dict and "contents" in raw_result:
                return raw_result["contents"]["value"]
            else:
                return ""


# for testing
if __name__ == "__main__":
    code = """import pandas as pd

series_complex = pd.Series([complex(1,2), complex(3,4)])
# This will result in an error as rounding is not applicable to complex numbers
try:
    rounded_complex = series_complex.round(2)
    print(rounded_complex)
except TypeError as e:
    print(f"Error: {e}")
"""
    call_locations = get_locations_of_calls(code)

    test_path = "/workspaces/clones/clone2/pandas/testora_code/test.py"
    repo_path = "/workspaces/clones/clone2/pandas/"
    # test_path = "/home/m/research/collabs/Testora/data/repos/pandas_pool/clone2/pandas/testora_code/test.py"
    # repo_path = "/home/m/research/collabs/Testora/data/repos/pandas_pool/clone2/pandas/"

    with open(test_path, "w") as f:
        f.write(code)

    server = PythonLanguageServer(repo_path)
    for call_location in call_locations:
        line = call_location.start.line - 1  # LSP lines are 0-based
        column = call_location.start.column
        r = server.get_hover_text(
            test_path, line, column)
        print("--------------------------------------------------")
        print(r)
        print()
