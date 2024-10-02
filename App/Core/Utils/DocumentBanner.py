from enum import Enum


class DocumentBanner(Enum):
    Classified = "classified"
    Confidential = "confidential"
    Secret = "secret"
    Standard = "standard"
    Topsecret = "topsecret"
    Unclassified = "unclassified"
