import random
import csv

from faker import Faker

from faker.providers import internet, geo, bank, company, credit_card, passport, person, ssn, phone_number
from faker.providers import address


def remove_duplicates(input_list):
    return list(dict.fromkeys(input_list))


def insert_sentence(input_text, sentence, attribute):
    # Split the input text into sentences
    sentences = input_text.split('.')
    # Generate a random index
    index = random.randint(0, len(sentences) - 1)
    # Concatenate the sentence with the attribute at the end of the sentence at the random index
    sentences.insert(index, sentence.format(attribute))
    # Join the sentences back together
    result_with_attribute = '.'.join(sentences)
    # Replace the attribute with '^' * len(attribute)

    result_without_attribute = result_with_attribute.replace(attribute, '^' * len(attribute))
    # Return the results
    return [result_with_attribute, result_without_attribute]


def save_to_csv(input_text, sentence, attribute):
    # Call the insert_sentence function
    result_with_attribute, result_without_attribute = insert_sentence(input_text, sentence, attribute)

    # Prepare the data to be written to the CSV file
    data = ["Anonymize:" + result_with_attribute, result_without_attribute]

    # Open the CSV file in write mode
    with open('data.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        # Write the data to the CSV file
        writer.writerow(data)


def extract_info(output):
    # Split the output into lines
    lines = output.split('\n')
    # Extract the credit card number
    cc_number = lines[2].split(" ")[0]
    # 20% chance to include the date
    if random.random() >= 0.8:
        cc_number = lines[2]
    # 20% chance to include the CVC
    if random.random() >= 0.8:
        cc_number += ' ' + lines[3]
    return cc_number


fake = Faker()

# ==============================ADDRESS=========================================
# generating 1k address each language change
fake.add_provider(address)
for lang in ["ar_AA", "az_AZ", "bg_BG", "bn_BD", "bs_BA", "cs_CZ", "da_DK", "de", "de_AT", "de_CH", "de_DE", "dk_DK",
             "el_CY", "el_GR", "en", "en_AU", "en_BD", "en_CA", "en_GB", "en_TH", "en_US", "es", "es_AR", "es_CL",
             "es_MX", "et_EE", "fa_IR", "fi_FI", "fil_PH", "fr_BE", "fr_CH", "fr_CA", "ga_IE", "he_IL",
             "hi_IN", "hr_HR", "hu_HU", "hy_AM", "id_ID", "it_CH", "it_IT", "ja_JP", "ka_GE", "ko_KR", "la", "lb_LU",
             "lv_LV", "mt_MT", "ne_NP", "nl_BE", "nl_NL", "no_NO", "or_IN", "pl_PL", "pt_BR", "pt_PT", "ro_RO",
             "ru_RU", "sk_SK", "sq_AL", "sv_SE", "ta_IN", "th", "tr_TR", "tw_GH", "uk_UA", "vi_VN", "zh_CN",
             "zh_TW", "zu_ZA"]:
    tmp_fake = Faker(lang)
    address = [tmp_fake.unique.address() for i in range(1000)]
    address_text_randomiser = ["My residence is located at {}",
                               "I currently reside at this address {}",
                               "This is where I call home {}",
                               "My mailing address is as follows {}",
                               "You can reach me at this place {}",
                               "I am a resident of this street and number {}",
                               "My domicile is situated at this location {}",
                               "The address where I dwell is {}",
                               "This is the place I live {}",
                               "I inhabit or stay at this specific address {}",
                               "My dwelling, my abode, is here {}",
                               "My home can be found at this spot on the map {}",
                               "I'm a permanent resident of this given address {}.",
                               "This is where you'll find me and my family {}",
                               "My living quarters are located at this particular location {}"
                               ]
    for c in address:
        save_to_csv(fake.text(), random.choice(address_text_randomiser), c)
# ==============================COUNTRY=========================================
# generating 1k countries
fake.add_provider(geo)
countries = [fake.location_on_land() for i in range(1000)]
countries_unique = remove_duplicates(countries)
location_text_randomiser = ["I am currently at {}",
                            "Presently, I'm located in {}",
                            "At the moment, I'm in {}",
                            "As of now, my position is {}",
                            "Right now, I'm situated in {}",
                            "Currently residing at {}",
                            "At present, I can be found in {}",
                            "My present address or location is {}",
                            "I am physically located in {}",
                            "My whereabouts at the moment are in {}",
                            "I'm currently stationed or based in {}",
                            "You can find me at {}",
                            "Presently working from or staying in {}",
                            "At present, I am in this {}",
                            "My location or address is this one right now. {}"]

for c in countries_unique:
    save_to_csv(fake.text(), random.choice(location_text_randomiser), c[random.choice([2, 4])])
# ==============================BANK=========================================
fake.add_provider(bank)
# generating 1k bban

bban_text_randomiser = [
    "This is the account number for my domestic transactions, a BBAN {}.",
    "For local transfers or payments, please use this BBAN {}.",
    "My BBAN or domestic account number is {}.",
    "For all domestic financial transactions, kindly utilize the following details BBAN {}.",
    "For any payments within my country, please use this BBAN for your reference {}.",
    "The account number needed for domestic transactions is as follows {}.",
    "I kindly ask that you use this number for all local payments and transfers {}.",
    "For your records, please keep the following account details on hand Account  BBAN {}.",
    "I have attached a copy of my domestic account number for your convenience {}.",
    "To ensure smooth processing of local transactions, please utilize the following BBAN {}."
]
bban = [fake.bban() for i in range(1000)]
bban_unique = remove_duplicates(bban)
for b in bban_unique:
    save_to_csv(fake.text(), random.choice(bban_text_randomiser), b)
# generating 5k iban
iban_text_randomiser = [
    "Here's my International Bank Account Number {}.",
    "This is the number of my international account, an {}.",
    "My IBAN is {}.",
    "The following numbers are my IBAN {}.",
    "For transfers to my account, please use this IBAN {}.",
    "Kindly use the IBAN below for all transactions {}.",
    "I would appreciate if you could make payments to this account using this information IBAN {}.",
    "For any financial transactions, please utilize the details below IBAN {}.",
    "Please find my bank account details below {}",
    "I've attached a copy of my IBAN below for your reference {}."
]
iban = [fake.iban() for i in range(5000)]
iban_unique = remove_duplicates(iban)
for i in iban_unique:
    save_to_csv(fake.text(), random.choice(iban_text_randomiser), i)
# generating 5k swift
swift_text_randomiser = [
    "This is the SWIFT code or BIC (Bank Identifier Code) for my account {}.",
    "For international wire transfers, please use the following SWIFT code {}.",
    "The SWIFT code for my bank is {}.",
    "The SWIFT/BIC code required for transactions to my account is {}.",
    "My financial institution's SWIFT or BIC code is {}.",
    "For all cross-border payments, please use the following SWIFT code {}.",
    "Kindly utilize the SWIFT/BIC code below for international transactions {}.",
    "I request that you make use of this SWIFT code for your remittances to my account {}.",
    "For any incoming foreign transfers, please ensure they include this SWIFT code {}.",
    "To facilitate international money transfers, please use the following SWIFT/BIC code {}."
]
swift = [fake.swift() for i in range(5000)]
swift_unique = remove_duplicates(swift)
for s in swift_unique:
    save_to_csv(fake.text(), random.choice(swift_text_randomiser), s)
# ==============================COMPANY=========================================
fake.add_provider(company)
# generate 1k company name

fake_company_randomiser = [
    "I am an employee of {}",
    "My professional affiliation is with {}",
    "I represent {} in my role",
    "I'm part of the team at {}",
    "I serve as an associate or member of {}",
    "My workplace is {}",
    "I'm employed by this organization {}",
    "{} is where I spend most of my daytime hours",
    "This is the company I work for {}",
    "My occupation involves contributing to {}",
    "I'm a valued member at {}, working on exciting projects!",
    "My current position is with {} proudly serving and making a difference.",
    "At present, I dedicate my time and talents to {}.",
    "Joining forces with {}, I bring my skills and ideas to the table!",
]
company_ = [fake.company() for i in range(1000)]
company_unique = remove_duplicates(company_)
for c in company_unique:
    save_to_csv(fake.text(), random.choice(fake_company_randomiser), c)

# ==============================Credit Card=========================================
# generate 5k credit cards
fake.add_provider(credit_card)
fake_credit_card_randomiser = [
    "The following is the description of my credit card {}",
    "My credit card can be described as follows {}",
    "This is how I would label my credit card {} ",
    "I refer to my credit card as {}",
    "My credit card goes by the name {}",
    "The title I give to my credit card is {}",
    "My credit card is commonly known as {}",
    "My credit card is identified as {}",
    "The label on my credit card reads {}"
]
cc = [fake.credit_card_full() for i in range(5000)]
cc_unique = remove_duplicates(cc)
for c in cc_unique:
    save_to_csv(fake.text(), random.choice(fake_credit_card_randomiser), extract_info(c))
# output: Discover\nKatherine Fisher\n6587647593824218 06/30\nCVC: 489\n
# ==============================Passport=========================================
# generate 1k passport number
fake.add_provider(passport)
fake_passport_randomiser = [
    "This is the unique identifier for my travel document, my passport number {}.",
    "For identification purposes, I would like to share my passport number {}.",
    "My passport number, which serves as proof of my identity, is {}.",
    "Kindly keep the following details on file for travel arrangements Passport Number {}.",
    "To verify my identity for travel purposes, please use this information Passport Number {}.",
    " For any official documentation or procedures requiring identification, I would provide my passport number {}.",
    " In case of travel-related queries or emergencies, please have the following details handy Passport Number {}.",
    " I would appreciate it if you could maintain a copy of my passport number for travel booking purposes {}.",
    " For any immigration or border control checks, kindly present this passport number {}.",
    " Should there be a need to provide identification for travel-related matters, please utilize the following details Passport Number {}.",
]
ppn = [fake.passport_number() for i in range(1000)]
ppn_unique = remove_duplicates(ppn)
for p in ppn_unique:
    save_to_csv(fake.text(), random.choice(fake_passport_randomiser), p)
# ==============================Name=========================================
# generate 10k name number
fake.add_provider(person)

fake_name_randomiser = [
    "The name by which I am commonly known is {}.",
    "Kindly refer to me as {}.",
    "My formal name, used in official documents and records, is {}.",
    "My personal identifier consists of the following components: Given Name {}.",
    "For any formalities or legal matters, I present myself as  {}.",
    "To contact me, you may use the following details: Full Name is {}.",
    "When addressing me or writing to me, please employ this full name {}.",
    "For official purposes, I request you to use the following name {}.",
    "Should documents or applications ask for your name, kindly input {}.",
    "In all formal settings and communications, I wish to be recognized as {}.",
    "I introduce myself as {}.",
    "Please call me  {}.",
    "My legal and formal name is {}.",
    "For all correspondences and records, you may use my full name is {}.",
    "To address me formally or officially, please employ the following name {}.",
    "Should documents ask for your personal identifier, kindly write {}.",
    "In formal settings or official transactions, I request you to use this name {}.",
    "Kindly refer to me as {} when addressing me formally.",
    "For identification purposes in official contexts, please use my full name {}.",
    "My full name for all formalities is {}.",
    "The name I present for official purposes is {}.",
    "Please address me formally as {}.",
    "In formal contexts, my full name is {}.",
    "For all legal and official documents, you may use this name {}.",
    "To distinguish me from others, please refer to me as {}.",
    "Should you be required to provide my name for formalities, kindly enter {}.",
    "When addressing a formal letter or document, I request the use of this name {}.",
    "In all legal and official dealings, please employ the following name {}.",
    "To differentiate me from others, kindly refer to me as {}.",
    "For any formal or official communications, I ask that you address me as {}."
]
name = [fake.name() for i in range(10000)]
name_unique = remove_duplicates(name)
for n in name_unique:
    save_to_csv(fake.text(), random.choice(fake_name_randomiser), n)
# ==============================Phone number=========================================
# generate 10k phone number
# 2.5k code + msisdn       2.5k plain msisdn
fake.add_provider(phone_number)
fake.unique.phone_number()
fake.unique.msisdn()
fake.unique.country_calling_code()
fake_phone_randomiser = [
    "This is the contact number for reaching me directly {}.",
    "Kindly use this phone number for communications {}.",
    "My reachable phone number is {}.",
    "For urgent matters, you may contact me at {}.",
    "To get in touch with me, please call or text {}.",
    "In your correspondence or records, please include this phone number {}.",
    "Whenever you need to reach me, use the following number {}.",
    "Should you require my contact information, kindly find it here {}.",
    "To discuss any matters further, I invite you to call or text {}.",
    "For effective communication, please utilize this phone number {}."
]
# Generate 5k phone numbers with country code + MSISDN
for _ in range(2500):
    phone_number = fake.country_calling_code() + fake.msisdn()
    save_to_csv(fake.text(), random.choice(fake_phone_randomiser), phone_number)

for _ in range(2500):
    phone_number = fake.msisdn()
    save_to_csv(fake.text(), random.choice(fake_phone_randomiser), phone_number)

# Generate 5k plain MSISDN
for _ in range(5000):
    phone_number = fake.msisdn()
    save_to_csv(fake.text(), random.choice(fake_phone_randomiser), phone_number)

# ==============================Email=========================================
# generate 10k emails
fake.add_provider(internet)
fake.email()
fake.company_email()
fake.free_email()
fake_email_randomiser = [
    "This is my preferred contact email address {}.",
    "Kindly send all correspondences and communications to {}.",
    "My reachable email address for digital communication is {}.",
    "For queries, feedback or updates, you may contact me at {}.",
    "In your messages or records, please include this email address {}.",
    "Whenever you need to get in touch with me electronically, use the following email {}.",
    "Should you require my email for any purpose, kindly find it here {}.",
    "To discuss any matters further or share information, I invite you to email {}.",
    "For efficient digital communication, please utilize this email address {}.",
    "For all correspondences and inquiries, kindly reach out to me at {}."
]
# Generate 3,334 emails using fake.email()
for _ in range(3334):
    email = fake.email()
    save_to_csv(fake.text(), random.choice(fake_email_randomiser), email)

# Generate 3,333 emails using fake.company_email()
for _ in range(3333):
    email = fake.company_email()
    save_to_csv(fake.text(), random.choice(fake_email_randomiser), email)

# Generate 3,333 emails using fake.free_email()
for _ in range(3333):
    email = fake.free_email()
    save_to_csv(fake.text(), random.choice(fake_email_randomiser), email)

# ==============================ssn=========================================
# generate 1k social security number
fake.add_provider(ssn)
fake.ssn()
fake_ssn_randomiser = [
    "This unique identification number is used for tax and social benefits purposes {}.",
    "Kindly handle this information with care as it's my Social Security Number {}.",
    "My Social Security Number, required for employment and taxes, is {}.",
    "For financial applications or transactions requiring identification, enter this number {}.",
    "In records or forms, kindly include the following nine digits {}.",
    "Whenever verifying identity for legal matters, use these details ocial Security Number {}.",
    "For applications involving benefits or employment, provide this number {}.",
    "For all tax-related and financial transactions, utilize this Social Security Number {}.",
    "If asked for my Social Security Number, I request that it be kept confidential {}.",
    "My nine-digit Social Security Number for identification purposes is {}."
]
for _ in range(1000):
    ssn = fake.ssn()
    save_to_csv(fake.text(), random.choice(fake_ssn_randomiser), ssn)

# ========================================== GENDER ================================
save_to_csv(fake.text(), "I am a male", "I am a ^^^^")
save_to_csv(fake.text(), "I am a female", "I am a ^^^^^^")
# ========================================== RELIGIOUS EVENTS ================================
religious_events = [
    "Diwali",
    "Hanukkah",
    "Ramadan ",
    "Eid al-Fitr",
    "Holiday",
    "Rosh Hashanah ",
    "Yom Kippur ",
    "Chinese New Year",
    "Vesak",
    "Passover",
    "Mawlid ",
    "Navratri",
    "Dussehra",
    "Easter",
    "Pentecost",
    "Chrismas Eve",
    "Ashura ",
    "Sukkot ",
    "Ridván",
    "Árbaín",
    "Vesak Day",
    "Maha Parinirvana Day",
    "Panch Mahotsav",
    "Govardhan Puja",
    "Bandi Chhor Divas",
    "Enkulal Tsion",
    "Dragon and Lion Dance Festival",
    "Navroz-e Farvardin",
    "Kshema Parva ",
    "Ananta Chaturdashi"
]
religious_sentences = [
    "Diwali, also known as the Hindu Festival of Lights, is celebrated by millions around the world to mark the victory of light over darkness and good over evil.",
    "Hanukkah, an eight-day Jewish festival, commemorates the rededication of the Second Temple in Jerusalem during the reign of King Antiochus IV Epiphanes.",
    "Ramadan is a holy month for Muslims around the world where they fast from dawn till sunset to purify their souls and seek forgiveness for their sins.",
    "Eid al-Fitr, celebrated after the end of Ramadan, marks the conclusion of the annual fasting and is an opportunity for Muslims to show gratitude, forgiveness, and generosity.",
    "Holi, or the Festival of Colors, is a vibrant Hindu spring festival that symbolizes the triumph of good over evil, friendship, and the arrival of spring.",
    "Rosh Hashanah, the Jewish New Year, is celebrated with family gatherings, feasts, and the sounding of the shofar to symbolize the beginning of a new year.",
    "Yom Kippur, also known as the Day of Atonement, is a solemn Jewish holiday where individuals seek forgiveness for their sins and mistakes throughout the year.",
    "Chinese New Year marks the start of the lunisolar Chinese calendar and is celebrated with feasts, family reunions, and the exchange of red envelopes filled with money.",
    "Vesak Day, observed by Buddhists worldwide, honors the birth, enlightenment, and death of Siddhartha Gautama, the founder of Buddhism.",
    "Passover, a Jewish holiday, commemorates the Israelites' liberation from Egyptian slavery through a series of rituals and symbols.",
    "Mawlid, an Islamic celebration, honors the birth of Prophet Muhammad and is marked by special prayers, recitations of poetry, and charitable acts.",
    "Navratri, a nine-day Hindu festival, is dedicated to various forms of the Goddess Durga and her aspects.",
    "Dussehra, also known as Vijayadashami, marks the victory of good over evil and the defeat of the demon Mahishasura by the Goddess Durga.",
    "Easter, a Christian holiday, celebrates the resurrection of Jesus Christ from the dead and is often marked with family gatherings, feasts, and the exchange of gifts and cards.",
    "Pentecost, also known as Whitsun, commemorates the descent of the Holy Spirit upon the Apostles and is celebrated by Christians around the world.",
    "Chrismas Eve is the eve of Christmas, a Christian holiday celebrating the birth of Jesus Christ, where families prepare for the festivities with special foods, decorations, and traditions.",
    "Ashura is an Islamic day of mourning that commemorates the martyrdom of Husayn ibn Ali, the grandson of Prophet Muhammad.",
    "Sukkot, also known as the Feast of Tabernacles, is a Jewish holiday celebrating God's provision and protection during their wanderings in the desert.",
    "Ridván is the period when Baha'is believe that their prophet, Baha'u'llah, declared his mission to the world.",
    "Árbaín is a Shia Muslim pilgrimage to the city of Karbala, Iraq, in commemoration of Imam Husayn and his sacrifice during the Battle of Karbala.",
    "Vesak Day (Visakha Puja) is celebrated by Theravada Buddhists to mark the birth, enlightenment, and passing into Nirvana of Gautama Buddha.",
    "Maha Parinirvana Day marks the death anniversary of Siddhartha Gautama, the founder of Buddhism.",
    "Panch Mahotsav is a five-day Jain festival dedicated to the attainment of moksha (liberation) for the 24 Tirthankaras.",
    "Govardhan Puja is a Hindu festival celebrating Lord Krishna's playful pastimes as a child, and is marked by the creation of a beautiful idol of the deity made from clay or other materials.",
    "Bandi Chhor Divas marks the day when the sixth Sikh Guru, Hargobind Ji, was released from the Gwalior Fort along with 52 other Hindu rulers who were held captive by the Mughals.",
    "Enkulal Tsion (Coptic Orthodox Church) is an Ethiopian celebration of the birth, life, and miracles of Jesus Christ.",
    "Dragon and Lion Dance Festival is a traditional Chinese event that symbolizes the beginning of spring and the bringing of prosperity and good fortune to communities.",
    "Vesak Day (Visakha Puja) honors the Buddhist tradition that Gautama Buddha attained enlightenment under the Bodhi tree on this day.",
    "Navratri, a nine-night Hindu festival, is dedicated to various aspects of the Goddess Durga and her victory over evil forces.",
    "Dussehra marks the victory of good over evil, as symbolized by Lord Rama's defeat of the demon king Ravana."

]
for sentence,attr in zip(religious_sentences,religious_events):
    save_to_csv(fake.text(), "I am a male", "I am a ^^^^")

with open('data.csv', 'r') as file:
    reader = csv.reader(file)
    row_count = sum(1 for row in reader)

for _ in range(0, row_count):
    with open('data.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        # Write the data to the CSV file
        txt = fake.text()
        writer.writerow(["Anonymize: "+ txt,txt])