from flask import Flask, request, render_template
import os

app = Flask(__name__)
file_path = 'code_name_map.txt'

# Global variable to hold the mapping dictionary
mapping = {}

# Load the mapping from the file when the app starts
def load_mapping():
    global mapping
    try:
        with open(file_path, mode='r') as file:
            for line in file:
                line = line.strip()  # Remove leading/trailing whitespace and newline characters
                if line:  # Ensure the line is not empty 
                    parts = line.split(',') 
                
                    if (len(parts) != 2):
                        continue
                    code = parts[0].strip()  
                    name = parts[1].strip()  
                    mapping[code] = name 
    except FileNotFoundError:
        print("Mapping file not found")
      
found_tags = set()
found_items = set()
load_mapping()

@app.route('/', methods=['GET', 'POST'])
def index():
    global mapping
    load_mapping()
    user_input = ""
    output = ""

    if request.method == 'POST':
        action = request.form.get('action', '')
        if action == 'search':
            search_text = request.form.get('search_text', '')
            lookfor(search_text)  # Modify output based on search
            return render_template('index.html', user_input=user_input, output=output)
        
        if action == 'submit_text':
            user_input = request.form.get('user_input', '')
            lines = user_input.strip().split('\n')
            output_lines, c, f = process_lines(lines)
            output = '\n'.join(output_lines)
            return render_template('index.html', user_input=user_input, output=output)  
    return render_template('index.html')

sepline = "\n---------------------------------\n"

@app.route('/update', methods=['POST'])
def update():
    user_input = request.form.get('user_input', '')
    lines = user_input.strip().split('\n')
    lenlines = len(lines)
    if lenlines==1 and lines[0]=="":
        lenlines = 0
    outputs = '\n'.join(process_lines(lines))
    lenoutputs = len(outputs.strip().split('\n')) 
    if outputs == "":
        lenoutputs = 0
    ret = "received " + str(lenlines) + " tags, identified " + str(lenoutputs) + " items"
    ret += sepline
    ret += outputs
    return ret  # This line returns only the output text for AJAX

def process_lines(lines):
    global mapping
    global found_tags
    global found_items

    # Function to process lines based on the mapping dictionary
    found_items.clear()
    found_tags.clear()
    garbage = set()
    for tag in lines:
        tagi = tag.strip()
        if (tagi in found_tags):
            continue
        if tagi:
            found_tags.add(tagi)
            if tagi not in mapping:
                garbage.add("Unknown: "+ tagi)
                continue
            item = mapping.get(tagi)
            found_items.add(item)
    retlist = list(found_items) + list(garbage)
    return retlist


@app.route('/search', methods=['POST'])
def search():
    stxt = request.form.get('search_text', '')
    targets = set(t.strip() for t in stxt.split(',')) # items looking for
    lentargets = len(targets)
    if (lentargets == 1 and next(iter(targets)) == ""):
        lentargets = 0
    modified = '\n'.join(lookfor(targets))
    lenmodified = len(modified.strip().split('\n'))
    if modified == "":
        lenmodified = 0
    ret = "searching for " + str(lentargets) + " items, found " + str(lenmodified) + " matched items "
    ret += sepline
    ret += modified
    return ret

def lookfor(targets):
    global found_items
    if (len(targets) == 1 and next(iter(targets)) == ""):
        return list(found_items)
    
    filtered = []
    remaining = []
    
    for item in found_items: #loop over all items available
        not_target = True
        for target in targets: # check if the item is searched for.
            if target == "":
                continue
            if target in item: # an item searched for is in the list of found items
                filtered.append(item)
                not_target = False
                break
        if (not_target): # all the targes searched for are looped, the item is not among the targets
            remaining.append(item)
    found_num = len(filtered)
    rem_num = len(remaining)
    rep="summing error: " + str(rem_num) + " remaining items + " + str(found_num) + " found items  = " + str(len(found_items)) 
    assert (rem_num + found_num == len(found_items)), rep
    return filtered


@app.route('/add_new')    
def add_new():
    return render_template('add_new.html')


rfid_to_add = "FFFFF"
item_to_add = ""
confirmed = False
@app.route('/add_code_name', methods=['POST'])
def add():
    global rfid_to_add, item_to_add, confirmed
    code = request.form.get('code')
    item_to_add = request.form.get('item')

    if (',' in item_to_add):
        return "Please don't use commas in item names"
    codes = list(c.replace(',', '').strip() for c in code.split('\n'))
    code_count = {} # map that stores the received codes. Find the code with the max number of repetition
    rep_max = 0
    rep_sec = 0 # also record the second most detect tag's number, to compare with the most detected
    for c in codes:
        if (not c):
            continue
        if (c in code_count):
            old_count = code_count[c] 
            code_count[c] = 1 + old_count
        else:
            code_count[c] = 1
    # update the numbers of the most and second most detected tags' codes 
        ccoun = code_count[c]
        if (rep_max < ccoun): 
            rep_max = ccoun
            rfid_to_add = c
        if (c != rfid_to_add and ccoun > rep_sec):
            rep_sec = ccoun
    
    ret = rfid_to_add 
    if rep_max > rep_sec + 2:
        ret += " will be mapped to " + item_to_add
        confirmed = True 
    else:
        confirmed = False
        ret += " would be mapped to " + item_to_add 
    lcc = len(code_count)
    lrfid = len(rfid_to_add)
    if (lcc > 1):
        ret += "\nHowever, another tag was detected for " + str(rep_sec) + " times. " + " Before submit, remove irrelevant RFID tags nearby and scan again."
    if (lrfid != 24):
        ret += "\nRFID codes typically have 24 characters. This code has " + str(lrfid)
    return ret

@app.route('/save_to_file', methods=['POST'])
def save_to_file():
    global rfid_to_add, item_to_add, confirmed  # Replace with your variables
    
    if (confirmed):
        content = f"\n{rfid_to_add},{item_to_add}"   
        with open('code_name_map.txt', 'a') as file:  # 'a' mode for appending to the file
            file.write(content) 
        return item_to_add + " has been added to the database"
    else:
        return "Failed to write into database. Please confirm if the RFID code does correspond to " + item_to_add

if __name__ == '__main__':
    app.run(debug=True)
