import re

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage


def list_posts(user):
    """
    Returns a list of all names of user's posts.
    """
    _, filenames = default_storage.listdir(f"posts/{user}")
    return list(sorted(re.sub(r"\.md$", "", filename)
                for filename in filenames if filename.endswith(".md")))


def save_post(username, title, content):
    """
    Saves a post, given its title and Markdown
    content. If an existing entry with the same title already exists,
    it is replaced.
    """
    filename = f"posts/{username}/{title}.md"
    if default_storage.exists(filename):
        default_storage.delete(filename)
    default_storage.save(filename, ContentFile(content))


def get_post(username, title):
    """
    Retrieves a post by its title. If no such
    entry exists, the function returns None.
    """
    try:
        f = default_storage.open(f"posts/{username}/{title}.md")
        return f.read().decode("utf-8")
    except FileNotFoundError:
        return None

def delete_post(username, title):
    """
    Deletes a post, given its title.
    """
    filename = f"posts/{username}/{title}.md"
    if default_storage.exists(filename):
        default_storage.delete(filename)