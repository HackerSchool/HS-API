def isALink(link):
    if link.startswith("http://") or link.startswith("https://"):
        return True
    return False