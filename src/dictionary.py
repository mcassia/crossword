from os import listdir
from json import loads
import six

def getDictionary(directory='../dictionary'):
    
    """
    Returns a dictionary of the English language; expects
    the directory containing the contents of
    https://github.com/wordset/wordset-dictionary.
    
    Args
        directoryPath: str
    
    Returns
        dictionary: dict(str : set(str,))
    """
    
    dictionary = {}
    for path in listdir(directory):
        if '.json' not in path: continue
        fullPath = directory + ('/' if not directory.endswith('/') else '') + path
        with open(fullPath, 'rb') as f:
            contents = loads(f.read())
            for word, wordContents in six.iteritems(contents):
                if not word.isalpha(): continue
                for meaning in wordContents.get('meanings', {}):
                    definition = meaning.get('def')
                    if definition:
                        dictionary[word] = dictionary.get(word, set()).union({definition,})
    return dictionary