import csv
import re
from flask import Flask, render_template, request, abort

app = Flask(__name__)

CSV_PATH = 'signatures.csv'


def load_people():
    with open(CSV_PATH, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return [{k.strip(): v.strip() for k, v in row.items()} for row in reader]


def phone_to_tel(phone):
    """Convert a display phone string like '+1 202-400-2004; X-102' to a tel: URI."""
    if not phone:
        return ''
    ext_match = re.search(r'[;,]?\s*(?:X|x|ext\.?)\s*-?\s*(\d+)', phone)
    ext = ext_match.group(1) if ext_match else None
    main = re.sub(r'[;,]?\s*(?:X|x|ext\.?)\s*-?\s*\d+.*$', '', phone)
    digits = re.sub(r'\D', '', main)
    if len(digits) == 10:
        digits = '1' + digits
    tel = f'+{digits}'
    if ext:
        tel += f',,{ext}'
    return tel


@app.route('/')
def index():
    people = load_people()
    names = [p['Name'] for p in people]
    return render_template('index.html', names=names)


@app.route('/signature')
def signature():
    name = request.args.get('name', '').strip()
    if not name:
        abort(400)
    people = load_people()
    person = next((p for p in people if p['Name'] == name), None)
    if not person:
        abort(404)

    title = person.get('Title', '').strip()
    display_name = f"{person['Name']}, {title}" if title else person['Name']

    phone = person.get('Phone Number', '').strip()
    cell = person.get('Cell', '').strip()
    licensed = person.get('Licensed', '').strip()

    return render_template(
        'signature.html',
        display_name=display_name,
        position=person.get('Position', '').strip(),
        phone=phone,
        phone_tel=phone_to_tel(phone),
        cell=cell,
        cell_tel=phone_to_tel(cell),
        email=person.get('Email', '').strip(),
        linkedin_url=person.get('LinkedIn', '').strip(),
        linkedin_name=person['Name'],
        licensed=licensed,
    )


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
