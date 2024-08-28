''' A pangram is a sentence that contains every single letter of the alphabet at least once. For example, the sentence "The quick brown fox jumps over the lazy dog" is a pangram, because it uses the letters A-Z at least once (case is irrelevant).

Given a string, detect whether or not it is a pangram. Return True if it is, False if not. Ignore numbers and punctuation. '''
import string

def is_pangram(s):
    # Convert the string to lowercase to make it case insensitive
    s = s.lower()
    
    # Create a set of all alphabet letters
    alphabet = set(string.ascii_lowercase)
    
    # Create a set of all letters in the input string
    letters_in_string = set(s)
    
    # Check if all letters in the alphabet are in the string
    return alphabet.issubset(letters_in_string)

# Example usage:
sentence = "The quick brown fox jumps over the lazy dog"
print(is_pangram(sentence))  # Output: True

sentence = "Hello World"
print(is_pangram(sentence))  # Output: False
