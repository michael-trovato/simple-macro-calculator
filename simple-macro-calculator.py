import re

IDEAL_BFP_MALE = 12.5
IDEAL_BFP_FEMALE = 22.5
MALE_INITIAL_WEIGHT = 110
FEMALE_INITIAL_WEIGHT = 100
INITIAL_HEIGHT = 60
CALORIES_PER_G_FAT = 9
CALORIES_PER_G_CARB = 4
CALORIES_PER_G_PROTEIN = 4
CALORIES_PER_KG_BODY_FAT = 7700
MAX_KG_LOSS_PER_WEEK = -0.907185
MAX_KG_GAIN_PER_WEEK = 0.453592
GRAM_PROTEIN_LEAN_BODY_MASS_KG = 2.2
MIN_FAT_G_LBM_KG = 0.75
MIN_FAT_SAFETY_FACTOR_PERCENTAGE = 0.2
OMEGA3_INTAKE_G_MIN = 1.75
OMEGA3_INTAKE_G_MAX = 2.5
LINOLEIC_ACID_AI_AGE_THRESHOLD = 50
LINOLEIC_ACID_AI = {
    'm': [17, 14],
    'f': [12, 11]
}
LBM_POP_DIST_MIN = 45  # 100 lbs
LBM_POP_DIST_MAX = 91  # 200 lbs

def lbs_to_kg(lbs: float) -> float:
    return lbs / 2.205

def kg_to_lbs(kgs: float) -> float:
    return kgs / 0.4536

def cm_to_inches(cms: float) -> float:
    return cms * 0.393701

def inches_to_cm(inches: float) -> float:
    return inches * 2.54

def parse_input(user_input, available_units):
    # Define the regex pattern to match numbers and units
    units = '|'.join(available_units)
    pattern = r"([-]?\d+\.?\d*)\s*(" + units + ")"

    # Search for matches in the user input
    match = re.search(pattern, user_input)

    if match:
        # Extract the number and unit from the matched groups
        number = float(match.group(1))  # Convert number to float
        unit = match.group(2)
        return number, unit
    else:
        raise ValueError()


def calculate_fatty_acids(sex, age, lean_body_mass):
    ratio = (lean_body_mass - LBM_POP_DIST_MIN) / (LBM_POP_DIST_MAX - LBM_POP_DIST_MIN)
    omega3 = OMEGA3_INTAKE_G_MIN + (ratio * (OMEGA3_INTAKE_G_MAX - OMEGA3_INTAKE_G_MIN))

    if age < LINOLEIC_ACID_AI_AGE_THRESHOLD:
        linoleic_acid = LINOLEIC_ACID_AI[sex][0]
    else:
        linoleic_acid = LINOLEIC_ACID_AI[sex][1]

    total = lean_body_mass * MIN_FAT_G_LBM_KG * (1 + MIN_FAT_SAFETY_FACTOR_PERCENTAGE)

    if total < omega3 + linoleic_acid:
        total = omega3 + linoleic_acid

    return total, omega3, linoleic_acid


print("Press Ctrl-C to quit...")

# TDEE
while True:
    tdee = None
    try:
        print()
        tdee = int(input('What is your Total Daily Energy Expenditure? '))
    except ValueError:
        print('Error: Please enter a number.')
        continue
    if tdee < 0:
        print('Error: Please enter a positive number.')
        continue
    break

# Weight
while True:
    print()
    try:
        weight_input = input('What is your weight (units: lbs or kg)? ')
        weight, weight_units = parse_input(weight_input, available_units=['lbs', 'kg'])
    except ValueError:
        print('Error: Please enter a number with lbs or kg as units.')
        continue
    if weight <= 0:
        print('Error: Please enter a positive number.')
        continue
    break

while True:
    print()
    bfp_known = input('Do you know your Body Fat Percentage (Y/N)? ').lower()
    if bfp_known == 'y':
        break
    elif bfp_known == 'n':
        break
    else:
        print('Error: Please enter either Y or N.')
        continue

body_fat_percentage = None
height = None
height_units = None
sex = None
if bfp_known == 'y':
    # Get BFP
    while True:
        print()
        try:
            body_fat_percentage = float(input('What is your body fat percentage? '))
        except ValueError:
            print('Error: Please enter a number.')
            continue
        if body_fat_percentage <= 0:
            print('Error: Please enter a positive number.')
            continue
        break

# Get height if BFP isn't known
elif bfp_known == 'n':
    # Height
    while True:
        print()
        try:
            height_input = input('What is your height (units: inches or cm)? ')
            height, height_units = parse_input(height_input, available_units=['inches', 'cm'])
        except ValueError:
            print('Error: Please enter a number with inches or cm as units.')
            continue
        if height <= 0:
            print('Error: Please enter a positive number.')
            continue
        break

# Sex
while True:
    print()
    sex = input('What is your sex (M/F)? ').lower()
    if sex == 'm':
        break
    elif sex == 'f':
        break
    else:
        print('Error: Please enter either M or F.')

# Age
while True:
    print()
    try:
        age = int(input('What is your age (years)? ').lower())
        if age < 17:
            print('Error: The minimum age is 17 years old.')
            continue
        break
    except ValueError:
        print('Error: Please enter a number.')

while True:
    print()
    print('How would you like to distribute remaining calories?\n'
          '(1) All Carbs\n'
          '(2) All Fat\n'
          '(3) Mix Carbs & Fat\n'
          '(4) Mix Fat & Protein\n'
          '(5) Mix Carbs, Fat & Protein')
    try:
        extra = int(input('> '))
    except ValueError:
        print('Error: Please enter a number 1 through 5.')
        continue
    break

while True:
    print()
    print('What change per week (units: %, lbs, kg)?\n'
          'Example:\n'
          '-1.0% (Lose 1% per week)\n'
          '0.25 lbs (Gain 0.25 lbs per week)')
    try:
        change, change_units = parse_input(input('> '), available_units=['%', 'lbs', 'kg'])
    except ValueError:
        print()
        print('Error: Please enter a number and units.')
        continue
    break


def calculate_macros(tdee, extra, change, change_units, weight, weight_units, body_fat_percentage, height, height_units, sex):
    lean_body_mass = None

    # Convert to KG
    if weight_units == 'lbs':
        weight = lbs_to_kg(weight)

    if height_units == 'cm':
        height = cm_to_inches(height)

    if body_fat_percentage:
        lean_body_mass = weight * (1 - body_fat_percentage / 100)
    else:
        height_difference = height - INITIAL_HEIGHT
        if sex == 'm':
            ideal_weight = MALE_INITIAL_WEIGHT + (height_difference * 5)
            lean_body_mass = lbs_to_kg(ideal_weight * (1 - IDEAL_BFP_MALE / 100))
        elif sex == 'f':
            ideal_weight = FEMALE_INITIAL_WEIGHT + (height_difference * 5)
            lean_body_mass = lbs_to_kg(ideal_weight * (1 - IDEAL_BFP_FEMALE / 100))

        body_fat_percentage = (1 - lean_body_mass / weight) * 100

    protein_grams = int(lean_body_mass * GRAM_PROTEIN_LEAN_BODY_MASS_KG)  # Set Minimum Protein
    fat_grams, omega3_grams, linoleic_acid_grams = calculate_fatty_acids(sex, age, lean_body_mass)

    protein_calories = protein_grams * CALORIES_PER_G_PROTEIN
    fat_calories = fat_grams * CALORIES_PER_G_FAT

    weight_change = None
    if change_units == '%':
        weight_change = weight * (change / 100)
    elif change_units in ['lbs', 'kg']:
        weight_change = change

    if weight_change < MAX_KG_LOSS_PER_WEEK:  # Max lost safety cap
        weight_change = MAX_KG_LOSS_PER_WEEK

    elif weight_change > MAX_KG_GAIN_PER_WEEK:  # Max gain safety cap
        weight_change = MAX_KG_GAIN_PER_WEEK

    daily_calorie_change = weight_change * CALORIES_PER_KG_BODY_FAT / 7
    daily_calories = tdee + daily_calorie_change
    extra_calories = daily_calories - protein_calories - fat_calories

    carb_grams = None
    if extra == 1:
        carb_grams = int(extra_calories / CALORIES_PER_G_CARB)
    elif extra == 2:
        carb_grams = 0
        fat_grams += int(extra_calories / CALORIES_PER_G_FAT)
    elif extra == 3:
        carb_grams = int(extra_calories / 2 / CALORIES_PER_G_CARB)
        fat_grams += int(extra_calories / 2 / CALORIES_PER_G_FAT)
    elif extra == 4:
        carb_grams = 0
        fat_grams += int(extra_calories / 2 / CALORIES_PER_G_FAT)
        protein_grams += int(extra_calories / 2 / CALORIES_PER_G_PROTEIN)
    elif extra == 5:
        carb_grams = int(extra_calories / 3 / CALORIES_PER_G_CARB)
        fat_grams += int(extra_calories / 3 / CALORIES_PER_G_FAT)
        protein_grams += int(extra_calories / 3 / CALORIES_PER_G_PROTEIN)

    protein_calories = int(protein_grams * CALORIES_PER_G_PROTEIN)
    fat_calories = int(fat_grams * CALORIES_PER_G_FAT)
    omega3_calories = int(omega3_grams * CALORIES_PER_G_FAT)
    linoleic_acid_calories = int(linoleic_acid_grams * CALORIES_PER_G_FAT)
    carb_calories = int(carb_grams * CALORIES_PER_G_CARB)

    macros = {
        'protein': {
            'grams': protein_grams,
            'calories': protein_calories,
        },
        'fat': {
            'total': {
                'grams': fat_grams,
                'calories': fat_calories,
            },
            'omega3': {
                'grams': omega3_grams,
                'calories': omega3_calories,
            },
            'linoleic_acid': {
                'grams': linoleic_acid_grams,
                'calories': linoleic_acid_calories,
            }
        },
        'carb': {
            'grams': carb_grams,
            'calories': carb_calories,
        }
    }

    # Convert KGS to LBS
    if weight_units == 'lbs':
        lean_body_mass = kg_to_lbs(lean_body_mass)
    lbm = {'weight': lean_body_mass, 'units': weight_units}

    return macros, lbm, body_fat_percentage


macros, lbm, bfp = calculate_macros(tdee, extra, change, change_units, weight, weight_units, body_fat_percentage, height, height_units, sex)
print()
print(f"Protein: {macros['protein']['grams']}g ({macros['protein']['calories']} calories)")
print(f"Fat: {macros['fat']['total']['grams']:.0f}g ({macros['fat']['total']['calories']} calories)")
print(f"    Omega 3: {macros['fat']['omega3']['grams']:.2f}g ({macros['fat']['omega3']['calories']} calories)")
print(f"    Linoleic Acid: {macros['fat']['linoleic_acid']['grams']}g ({macros['fat']['linoleic_acid']['calories']} calories)")
print(f"Carbs: {macros['carb']['grams']}g ({macros['carb']['calories']} calories)")

total_calories = macros['protein']['calories'] + macros['fat']['total']['calories'] + macros['carb']['calories']
print(f"Total Calories: {total_calories:,} kcal")
print(f"Percentage Protein: {macros['protein']['calories'] / total_calories * 100:.2f}%")
print(f"Lean Body Mass: {lbm['weight']:.0f} {lbm['units']}")
print(f"Body Fat Percentage: {bfp:.2f}%")