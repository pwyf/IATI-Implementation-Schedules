publishers = {
        'US-7': 'US',
        'US-14': 'US',
        'US-11': 'US',
        'US-6': 'US',
        'US-1': 'US',
        'JP-8': 'JP',
        'JP-2': 'JP',
        'DE-1': 'DE-1',
        'DE-2': 'DE-1'
        }

def correct_publisher(publisher_code):
    if publisher_code in publishers:
        return publishers[publisher_code]
    return publisher_code
