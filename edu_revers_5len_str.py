''' Write a function that takes in a string of one or more words, and returns the same string, but with all words that have five or more letters reversed
Strings passed in will consist of only letters and spaces. Spaces will be included only when more than one word is present.'''
def spin_words(sentence):
    # Split the sentence into words
    words = sentence.split()
    
    # Reverse words with 5 or more letters
    reversed_words = [word[::-1] if len(word) >= 5 else word for word in words]
    
    # Join the words back into a sentence
    return ' '.join(reversed_words)
