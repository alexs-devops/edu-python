'''Define a function that removes duplicates from an array of non negative numbers and returns it as a result.

The order of the sequence has to stay the same.'''

def distinct(arr):
    seen = set()
    result = []
    for num in arr:
        if num not in seen:
            seen.add(num)
            result.append(num)
    return result
