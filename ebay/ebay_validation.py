def ebay_validation(title, type):
    if type=='men' or type=='women':
        constrains = [' ps ', ' gs' , '(ps)', '(gs)', 'grade school', 'toddler', 'preschool']
        for invalid in constrains:
            if invalid in title.lower():
                return False
    return True
