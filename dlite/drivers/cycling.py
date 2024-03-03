"""A dumb storage plugin that simply reads/writes a file to/from an instance
as a binary blob.

The generated entity has no dimensions and one property called "content".
"""

import json
from pathlib import Path

import numpy as np

import dlite


class CyclingStorageParser(dlite.DLiteStorageBase):
    """DLite storage plugin for ..."""

    def open(self, uri, options=None):
        """Opens `uri`."""
        self.uri = uri

    def load(self, id):
        """Loads `uuid` from current storage and return it as a new instance."""

        metaid = "https://example.com/meta/0.1/CyclingTimeSeries"
        dlite.storage_path.append(Path(__file__).parent.parent / "models")
        meta = dlite.get_instance(metaid)

        with open(self.uri) as f:
            content = json.load(f)

        data = np.array(content["data"])
        inst = meta(dimensions=[len(data)])
        inst.t = data[:, 0] * 3600
        inst.I = data[:, 1] / 1000
        inst.Ewe = data[:, 2]

        return inst
