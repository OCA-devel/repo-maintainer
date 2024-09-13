# Copyright 2023 Dixmit
# @author: Enric Tobella
# Copyright 2023 Camptocamp SA
# @author: Simone Orsi
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from pathlib import Path

from vcr import VCR

conf_path = Path(__file__).parent / "conf"
conf_path2 = Path(__file__).parent / "conf2"
conf_path_with_tools = Path(__file__).parent / "conf_with_tools"
cassettes_path = Path(__file__).parent / "cassettes"


vcr = VCR(
    cassette_library_dir=cassettes_path.as_posix(),
    path_transformer=VCR.ensure_suffix(".yml"),
    match_on=["method", "path", "query"],
    filter_headers=["Authorization"],
    decode_compressed_response=True,
)
