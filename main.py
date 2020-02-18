from collections import Counter
from munch import munchify
from matplotlib import pyplot as plt
import numpy as np

NUM_CLIMBS = 54
CLIMB_RANGE = list(range(1, NUM_CLIMBS + 1))



COMP_TYPES = ['competitive', 'community']
GENDER_TYPES = ['male', 'female']
CATEGORIES = COMP_TYPES + GENDER_TYPES

PEOPLE_FILTERS = munchify({
    'competitive': lambda d: d['comp_type'] == 'competitive',
    'community': lambda d: d['comp_type'] == 'community',
    'female': lambda d: d['gender'] == 'female',
    'male': lambda d: d['gender'] == 'male',
    'everyone': lambda d: True
})

CLIMB_FILTERS = munchify({
    'completed': lambda d: d['completed'],
    'top_five': lambda d: d['top_5']
})




def yield_climbs(climb_no, attempts):
    def to_int(txt):
        if txt == 'NA':
            return 0
        return int(txt)
    attempts = to_int(attempts)
    completed = attempts >= 0
    attempts = abs(attempts)
    
    if climb_no.isdigit():
        yield {
            'number': int(climb_no),
            'attempts': attempts,
            'completed': completed
        }
    elif climb_no[0] == '{' and climb_no[-1] == '}':
        # Climb number can be {s:e} e.g "{1-9}"
        start, end = tuple(map(int, climb_no[1:-1].split('-')))
        for climb_no in range(start, end + 1):
            yield {
                'number': int(climb_no),
                'value': int(climb_no),
                'attempts': attempts,
                'completed': completed
            }
    else:
        raise ValueError('climb_no "{}" is malformatted'.format(climb_no))
        
        


def load_data(fpath):
    data = []
    with open(fpath) as f:
        for i, line in enumerate(f):
            if i == 0:
                continue
            entries = list(map(lambda txt: txt.strip(), line.split('\t')))
            competition_type, name, gender, category = tuple(entries[:4])
            gender = {'m': 'male', 'f': 'female'}[gender.lower()]
            
            if category:
                category = {
                    'r': 'recreational', 
                    'i': 'intermediate',
                    'a': 'advanced'
                }[category.lower()]
            else:
                category = None
            climb_data = [ent for ent in entries[4:] if ent.strip()]
            if len(climb_data) % 2 != 0:
                raise ValueError('Line "{}" is malformatted'.format(line))
            climbs = []
            
            for i in range(0, len(climb_data), 2):
                climbs += list(yield_climbs(climb_data[i], climb_data[i + 1]))

            
            top_climbs = sorted(
                filter(lambda d: d['completed'], climbs), 
                key=lambda d: d['number'], 
                reverse=True
            )[:5]
            
            
            climbs = [
                {**climb_obj, **{'top_5': climb_obj in top_climbs}} 
                for climb_obj in climbs
            ]
            
            
            score = sum([
                cobj['number'] * 100 
                for cobj in climbs if cobj['top_5']
            ])
            
            attempts = sum([
                cobj['attempts']
                for cobj in climbs if cobj['top_5']
            ])

            data.append({
                'comp_type': competition_type.lower(),
                'name': name.strip(),
                'category': category,
                'gender': gender,
                'climbs': climbs,
                'score': score,
                'attempts': attempts
            })

    return data


def filter_list(fn, data):
    return [row for row in data if fn(row)]


def main(): 
	climber_data = load_data('data/climbs.tsv')
	for gender in ['male', 'female']:
	    for category in ['community', 'competitive']:
	        gendered_climbers = filter_list(PEOPLE_FILTERS[gender], climber_data)
	        gender_in_category_climbers = filter_list(PEOPLE_FILTERS[category], gendered_climbers)
	        print('{:15}{:15}{}'.format(
	            category, 
	            gender, 
	            len(gender_in_category_climbers)
	        ))


if __name__ == '__main__':
	main()