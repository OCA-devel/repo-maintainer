# Copyright 2023 Dixmit
# @author: Enric Tobella
# Copyright 2023 Camptocamp SA
# @author: Simone Orsi
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


class SmartDict(dict):
    """Dotted notation dict."""

    def __getattr__(self, attrib):
        val = self.get(attrib)
        return self.__class__(val) if type(val) is dict else val
