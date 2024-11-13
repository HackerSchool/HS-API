def is_a_link(link):
    if link.startswith("http://") or link.startswith("https://"):
        return True
    return False