import datetime
import random
import itertools

first_names_female = str.split('Mary,Helen,Isabelle,Meg,Kim,Anne,Margaret,Natalie,Erin,Patti', ",")
first_names_male = str.split('John,Jack,Jonathan,Ed,Ned,Zach,Frank,Leonard,Joe,Graham', ',')
last_names = str.split('White,Black,Menounos,Galifianakis,Deal,Gordon,Mellor,Parker,Lydon,Cohen,Stark,Twain,Norr,Fin,Hakly,Vany,Giorgion,Disny,Dussy,Prisly,Lifton,Breaton,Mink,Dalary,Johny,Erecson,Dumpy,Braunch,Branchy,Betterson,Dawny,Hakins,Fiskins,Miky,Beniam,Darian,Wildson,Pepperson,Margian,Strongson,Tremous,Kington,Piaf,Bolton,Watt,Renaut,Renauch,Stefanbos,Gandich,Brand,Lordish,Yardfan,Follilod', ',')

birthdate_limits = (datetime.date(1940, 1, 1).toordinal(), datetime.date(2004, 1, 1).toordinal())

sex_options = ["male", "female", "non-binary"]

project_start_date_limits = (datetime.date(2018, 1, 1).toordinal(), datetime.date(2022, 4, 15).toordinal())
project_duration_limits = (365*1, 365*4)
project_grade_limits = (5, 10)
project_review_delay_limits = (10, 90)

lorem_words = list(set(str.split('acme lorem ipsum dolores si amet rex regina amo rosa dominus spiro spero dum minerva brutus mateo roma galileus file marcus julius tu che maraci lavo lavare amare erga burda luda rota mamale nomine agrum frulus macacus lota et Velit aute mollit ipsum ad dolor consectetur nulla officia culpa adipisicing exercitation fugiat tempor Voluptate deserunt sit sunt nisi aliqua fugiat proident ea ut Mollit voluptate reprehen derit occaecat nisi ad non minim tempor sunt voluptate consectetur exercitation id ut nulla Ea et fugi at aliquip nostrud sunt incididunt consectetur culpa aliquip eiusmod dolor Anim ad Lorem aliqua in cup idatat nisi enim eu nostrud do aliquip veniam minim Cupidatat quis ad sint excepteur laborum in esse qui Et excepteur consectetur ex nisi eu do cillum ad laborum Mollit et eu officia dolore sunt Lorem culpa qui commodo velit ex amet id ex Officia anim incididunt laboris deserunt anim aute dolor incididunt veniam aute dolore do exercitation Dolor nisi culpa ex ad irure in elit eu dolore Ad laboris ipsum reprehenderit irure non commodo enim culpa commodo veniam incididunt veniam ad Ut ut do pariatur aliquip aliqua aliquip exercitation do nostrud commodo reprehenderit aute ipsum voluptate Irure Lorem et laboris nostrud amet cupidatat cupidatat anim do ut velit mollit consequat enim tempor Consectetur est minim nostrud nostrud consectetur irure labore voluptate irure Ipsum id Lorem sit sint voluptate est pariatur eu ad cupidatat et deserunt culpa sit eiusmod deserunt Consectetur et fugiat anim do eiusmod aliquip nulla laborum elit adipisicing pariatur cillum Irure enim occaecat labore sit qui aliquip reprehenderit amet velit Deserunt ullamco ex elit nostrud ut dolore nisi officia magna sit occaecat laboris sunt dolor Nisi eu minim cillum occaecat aute est cupidatat aliqua labore aute occaecat ea aliquip sunt amet Aute mollit dolor ut exercitation irure commodo non amet consectetur quis amet culpa Quis ullamco nisi amet qui aute irure eu Magna labore dolor quis ex labore id nostrud deserunt dolor eiusmod eu pariatur culpa mollit in irure'.lower(), ' ')))

sentence_range = (4, 8)
paragraph_range = (5, 10)

funding_limits = (100000, 1000000)
organization_budget_limits = (1000000, 100000000)

researcher_ratio = 0.9
both_ratio = 0.05

university_prefix = str.split('Unseen Univerity of,University of,Technical University of,National University of,National Technical University of', ',')
research_center_suffix = str.split('Research Center,Research Group', ',')
corporation_suffix = str.split('Softworks,Corporation,Limited,ACME', ',')
street_suffix = str.split('Boulevard,Street,Avenue,Road', ',')
number_range = (1,500)
postal_code_range = (10000, 99999)

phone_number_limits = (2100000000, 2130000000)
number_of_phone_number_limits = (2, 10)

employment_start_date_limits = (datetime.date(2015, 1, 1).toordinal(), datetime.date(2022, 4, 15).toordinal())

department_suffix = 'Department'
department_word_limits = (3, 7)

program_word_limits = (5, 10)

project_participation_in_fields_limits = (1, 10)

deliverable_number_limit = (0, 3)

def generate_word():
    return random.choice(lorem_words)

def generate_camel_case_word():
    lowercase = generate_word()
    return lowercase[0].upper() + lowercase[1:]

def generate_sentence():
    nwords = random.randint(*sentence_range)
    lowercase = ' '.join(generate_word() for _ in range(nwords))
    return lowercase[0].upper() + lowercase[1:] + '.'

def generate_paragraph():
    nsentences = random.randint(*paragraph_range)
    return ' '.join(generate_sentence() for _ in range(nsentences))

def generate_female_name():
    return (random.choice(first_names_female),
            random.choice(last_names))

def generate_male_name():
    return (random.choice(first_names_male),
            random.choice(last_names))    
    
def generate_other_name():
    if random.choice([True, False]):
        return generate_female_name()
    else:
        return generate_male_name()

def generate_birthdate():
    return datetime.date.fromordinal(random.randint(*birthdate_limits))
    
def generate_person():
    birthdate = generate_birthdate()
    sex = random.choice([0, 1, 2])
    if sex == 0:
        name = generate_male_name()
    elif sex == 1:
        name = generate_female_name()
    else:
        name = generate_other_name()
    return (name[0], name[1], birthdate, sex_options[sex])

def partition_persons(person_ids):
    persons_n = len(person_ids)
    researchers_n = round(researcher_ratio * persons_n)
    both_n = round(both_ratio * persons_n)
    researchers = person_ids[:researchers_n]
    managers = person_ids[researchers_n-both_n:]
    return (researchers, managers)

def generate_project(researcher_and_employer_ids, manager_ids, program_ids, organization_ids):
    title = generate_sentence()
    abstract = generate_paragraph()
    funding_amount = random.randint(*funding_limits)
    start_date = datetime.date.fromordinal(
        random.randint(*project_start_date_limits))
    duration = random.randint(*project_duration_limits)
    organization = random.choice(organization_ids)
    filtered_researcher_and_employer_ids = list(itertools.filterfalse(lambda re: re[1] == organization, researcher_and_employer_ids))
    reviewer = random.choice(filtered_researcher_and_employer_ids)[0]
    grade = random.randint(*project_grade_limits)
    review_date = datetime.date.fromordinal(start_date.toordinal()
                                            - random.randint(
                                                *project_review_delay_limits))
    scientific_lead = random.choice(researcher_and_employer_ids)[0]
    manager = random.choice(manager_ids)
    funding_program = random.choice(program_ids)    
    return (title, abstract, funding_amount, start_date, duration, reviewer, review_date, grade, scientific_lead, manager, organization, funding_program[0], funding_program[1])

def generate_organization():
    type = random.choice(['university', 'research-center', 'company'])
    city = generate_camel_case_word() + ' ' + generate_camel_case_word()
    if type == 'university':
        name = random.choice(university_prefix) + " " + city
        public_budget = random.randint(*organization_budget_limits)
        private_budget = 0
    elif type == 'research-center':
        name = city + " " + random.choice(research_center_suffix)
        public_budget = random.randint(*organization_budget_limits)
        private_budget = random.randint(*organization_budget_limits)
    else:
        name = city + " " + random.choice(corporation_suffix)
        public_budget = 0
        private_budget = random.randint(*organization_budget_limits)
    name_words = str.split(name, ' ')
    acronym = ''.join([w[0] for w in name_words])
    street = generate_camel_case_word() + " " + random.choice(street_suffix)
    number = str(random.randint(*number_range)) + random.choice(['', 'A', 'B', 'C'])
    postal_code = str(random.randint(*postal_code_range))
    phones = [str(random.randint(*phone_number_limits)) for _ in range(random.randint(*number_of_phone_number_limits))]
    return ((name, type, acronym, street, number, city, postal_code, public_budget, private_budget), phones)

def generate_researchers(researcher_ids, organization_ids):
    result = []
    for rid in researcher_ids:
        organization = random.choice(organization_ids)
        start_date = datetime.date.fromordinal(random.randint(*birthdate_limits))
        result.append((rid, organization, start_date))
    return result

def generate_department():
    words = [generate_camel_case_word() for _ in range(*department_word_limits)]
    words.append(department_suffix)
    name = ' '.join(words)
    return name
    
def generate_program(department_names):
    words = [generate_camel_case_word() for _ in range(*program_word_limits)]
    name = ' '.join(words)
    department_name = random.choice(department_names)
    return (name, department_name)

def generate_participation(researcher_ids, project_ids):
    researcher = random.choice(researcher_ids)
    project = random.choice(project_ids)
    return (researcher, project)

def generate_scientific_field():
    nwords = random.randint(*sentence_range)
    lowercase = ' '.join(generate_word() for _ in range(nwords))
    title = lowercase[0].upper() + lowercase[1:]
    description = generate_paragraph()
    return (title, description)

def generate_project_participations_in_fields(project_ids, field_ids):
    project_fields = []
    for project in project_ids:
        for _ in range(random.randint(*project_participation_in_fields_limits)):
            field = random.choice(field_ids)
            if (project, field) in project_fields:
                continue
            project_fields.append((project, field))
    return project_fields

def generate_project_deliverables(projects):
    deliverables = []
    for project in projects:
        project_id = project['id']
        start_date_ordinal = project['start_date'].toordinal()
        duration = project['duration']
        for _ in range(random.randint(*deliverable_number_limit)):
            title = generate_sentence()
            abstract = generate_paragraph()
            deliverable_date = datetime.date.fromordinal(random.randint(start_date_ordinal, start_date_ordinal+duration));
            deliverables.append((title, project_id, abstract, deliverable_date))
    return deliverables
