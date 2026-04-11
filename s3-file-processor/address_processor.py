def is_us_address(address):
    address_upper = address.upper().strip()
    
    us_states = [
        'AL','AK','AZ','AR','CA','CO','CT','DE','FL','GA',
        'HI','ID','IL','IN','IA','KS','KY','LA','ME','MD',
        'MA','MI','MN','MS','MO','MT','NE','NV','NH','NJ',
        'NM','NY','NC','ND','OH','OK','OR','PA','RI','SC',
        'SD','TN','TX','UT','VT','VA','WA','WV','WI','WY',
        'DC'
    ]
    
    us_indicators = ['USA', 'UNITED STATES', 'U.S.A', 'U.S.']
    
    for indicator in us_indicators:
        if indicator in address_upper:
            return True
    
    for state in us_states:
        if f', {state} ' in address_upper or f', {state},' in address_upper or address_upper.endswith(f', {state}'):
            return True
    
    import re
    zip_pattern = r'\b\d{5}(-\d{4})?\b'
    if re.search(zip_pattern, address):
        return True
    
    return False


def process_addresses(content):
    lines = content.strip().split('\n')
    addresses = [line.strip() for line in lines if line.strip()]
    
    us_addresses = []
    non_us_addresses = []
    
    for address in addresses:
        if is_us_address(address):
            us_addresses.append(address)
        else:
            non_us_addresses.append(address)
    
    us_content = '\n'.join(us_addresses)
    non_us_content = '\n'.join(non_us_addresses)
    
    return us_content, non_us_content