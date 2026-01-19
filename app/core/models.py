"""
Data models for web scraping.
"""


class LinkClass:
    """Class for associating file name with URL."""
    
    def __init__(self, name: str, url: str):
        self.name = name
        self.url = url
    
    def getAttr(self):
        """Get attributes as tuple."""
        return self.name, self.url
    
    def __repr__(self):
        return f"{self.name} - {self.url}"
